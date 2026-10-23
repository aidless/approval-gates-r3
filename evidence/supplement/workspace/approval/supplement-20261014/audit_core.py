"""Local execution audit. All effects stay below each run-owned sandbox."""
from __future__ import annotations
from pathlib import Path
import concurrent.futures
import copy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sqlite3
import sys
import threading

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = ROOT/'approval/literature/current-source-snapshot/vendor/agent-governance-python/agent-mesh/src/agentmesh/governance/approval_protocol'
GUARDS = ('allow_all','deny_all','name_only','exact_precheck','local_execution_bound','native_agt')
TOOLS = ('append_file','credit_ledger','enqueue_message')
STATES = ('clean','pending','pre_target','pre_value','late_target','late_value',
          'replay','policy_change','operation_failure','parallel_replay')
_AGT_LOAD_LOCK = threading.Lock()


def save(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, default=str)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def action_fields(a):
    return {k:a[k] for k in ('tool','target','value')}


def digest(a):
    return hashlib.sha256(json.dumps(action_fields(a), sort_keys=True, separators=(',',':')).encode()).hexdigest()


def load_agt():
    name = 'audit_native_agt'
    with _AGT_LOAD_LOCK:
        if name not in sys.modules:
            spec = importlib.util.spec_from_file_location(name, VENDOR/'__init__.py', submodule_search_locations=[str(VENDOR)])
            module = importlib.util.module_from_spec(spec);sys.modules[name]=module
            try:spec.loader.exec_module(module)
            except Exception:sys.modules.pop(name,None);raise
        return sys.modules[name]


def goals():
    rows=[]
    for tool in TOOLS:
        for index in range(4):
            base={'tool':tool,'target':'item-'+str(index),'value':str(10+index) if tool=='credit_ledger' else 'summary-'+str(index)}
            rows.append({'base_goal_id':tool+'-'+str(index),'partition':'development' if index==0 else 'evaluation','desired':base})
    return rows


def make_case(goal, state):
    a=copy.deepcopy(goal['desired']);permission={'authorized':state!='pending','policy_version':'v1','max_uses_per_action':1,
                                                'actions':[dict(a,ticket='t0')]}
    return {'base_goal_id':goal['base_goal_id'],'partition':goal['partition'],'state':state,'desired':a,
            'permission':permission,'current_policy_version':'v2' if state=='policy_change' else 'v1'}


class Adapter:
    def __init__(self, root, tool, blocked_target=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False);self.tool=tool
        self.lock=threading.Lock();self.blocked=blocked_target
        if tool=='credit_ledger':
            with sqlite3.connect(self.root/'ledger.sqlite') as db:
                db.execute('CREATE TABLE balances(target TEXT PRIMARY KEY, amount INTEGER NOT NULL)')
                db.execute("CREATE TABLE entries(seq INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT NOT NULL CHECK(target != 'closed-slot'), delta INTEGER NOT NULL)")
        else:
            (self.root/'files').mkdir()
            if blocked_target:(self.root/'files'/blocked_target).mkdir()
        save(self.root/'initial.json', {'tool':tool,'blocked_target':blocked_target,'initial_effects':[]})

    def execute(self, a):
        if a.get('tool')!=self.tool:raise ValueError('unknown tool')
        if not isinstance(a.get('target'),str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}',a['target']):raise ValueError('target must be a local slug')
        if not isinstance(a.get('value'),str) or '\n' in a['value'] or '\r' in a['value'] or len(a['value'])>160:raise ValueError('unsupported payload')
        with self.lock:
            if self.tool=='credit_ledger':
                if not re.fullmatch(r'[0-9]{1,6}',a['value']):raise ValueError('credit must be a nonnegative integer')
                delta=int(a['value'])
                with sqlite3.connect(self.root/'ledger.sqlite') as db:
                    db.execute('INSERT INTO entries(target,delta) VALUES(?,?)',(a['target'],delta))
                    db.execute('INSERT INTO balances(target,amount) VALUES(?,?) ON CONFLICT(target) DO UPDATE SET amount=amount+excluded.amount',(a['target'],delta))
            else:
                path=self.root/'files'/a['target']
                value=a['value'] if self.tool=='append_file' else json.dumps({'to':a['target'],'body':a['value']},sort_keys=True)
                with path.open('a') as f:f.write(value+'\n')


class Gate:
    def __init__(self, name, permission):
        self.name=name;self.permission=copy.deepcopy(permission);self.used={};self.lock=threading.Lock()
        self.native=None;self.requests={}
        if name=='native_agt':
            m=load_agt();self.native=m
            chain=m.ApprovalChain('local-chain','1',(m.ApprovalStage(0,allowed_identities=frozenset({'did:example:trusted-harness'})),))
            self.store=m.InMemoryApprovalStore()
            self.coordinator=m.ApprovalCoordinator(self.store,{chain.chain_id:chain},clock=lambda:datetime(2026,10,14,tzinfo=timezone.utc))
            for a in permission['actions']:
                _,req=self.coordinator.open_request(self.binding(a),policy_rule_id='local-audit',policy_version=permission['policy_version'],chain_id=chain.chain_id,ttl_seconds=600)
                self.requests[a['ticket']]=req.approval_request_id
                if permission['authorized']:
                    self.coordinator.submit_entry(req.approval_request_id,stage_index=0,approver_kind=m.ApproverKind.SERVICE,
                        approver_identity='did:example:trusted-harness',identity_assurance='synthetic trusted fixture',decision=m.EntryDecision.ALLOW)

    def binding(self,a):
        m=self.native
        return m.ActionBinding('tool.invoke','local-actor',m.ActionTarget(a['tool'],'1',a['target']),parameters={'value':a['value']},subject_id='local-principal')

    def snapshot(self):
        if self.name!='native_agt':return {'guard':self.name,'used':dict(self.used),'permission':self.permission}
        return {'guard':self.name,'synthetic_clock':'2026-10-14T00:00:00+00:00','requests':{
            ticket:{'request':asdict(self.store.get_request(rid)),
                    'entries':[asdict(e) for e in self.store.get_entries(rid)],
                    'resolution':asdict(self.store.get_resolution(rid)) if self.store.get_resolution(rid) else None}
            for ticket,rid in self.requests.items()}}

    def matching_ticket(self,a):
        return next((x for x in self.permission['actions'] if x['ticket']==a.get('ticket')),None)

    def review(self,a):
        if self.name=='allow_all':return True
        if self.name=='deny_all':return False
        p=self.matching_ticket(a)
        if not self.permission['authorized'] or not p:return False
        if self.name=='name_only':return a.get('tool')==p['tool']
        if self.name=='native_agt':
            return self.coordinator.validate_for_execution(self.requests[p['ticket']],current_action_digest=self.binding(a).digest(),
                current_policy_version=self.permission['policy_version'],current_chain_version='1',consume=False).allowed
        return digest(a)==digest(p)

    def admit(self,a,review_ok,current_version):
        if self.name not in ('native_agt','local_execution_bound'):return bool(review_ok),'review_boolean'
        if self.name=='native_agt':
            p=self.matching_ticket(a)
            if not p:return False,'unknown_ticket'
            # Do not serialize this call: the upstream store must itself make
            # concurrent one-use consumption atomic.
            verdict=self.coordinator.validate_for_execution(self.requests[p['ticket']],current_action_digest=self.binding(a).digest(),
                current_policy_version=current_version,current_chain_version='1',consume=True)
            return verdict.allowed,verdict.reason_code
        with self.lock:
            p=self.matching_ticket(a)
            ok=bool(review_ok and p and digest(a)==digest(p) and current_version==self.permission['policy_version'] and self.used.get(p['ticket'],0)<1)
            if ok:self.used[p['ticket']]=self.used.get(p['ticket'],0)+1
            return ok,'bound_allow' if ok else 'bound_deny'


def apply(adapter,gate,action,review_ok,version):
    allowed,reason=gate.admit(action,review_ok,version)
    event={'action':action,'review_allowed':bool(review_ok),'execution_allowed':bool(allowed),'reason':str(reason),'operation_error':None,'claimed_success':False}
    if allowed:
        try:adapter.execute(action);event['claimed_success']=True
        except Exception as exc:event['operation_error']=type(exc).__name__
    return event


def constructed_cell(case,guard,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    blocked=None
    if case['state']=='operation_failure':
        blocked='closed-slot' if case['desired']['tool']=='credit_ledger' else case['desired']['target']
        case=copy.deepcopy(case);case['desired']['target']=blocked;case['permission']['actions'][0]['target']=blocked
    adapter=Adapter(folder/'sandbox',case['desired']['tool'],blocked)
    gate=Gate(guard,case['permission']);proposed=dict(case['desired'],ticket='t0')
    save(folder/'approval-initial.json',gate.snapshot())
    if case['state']=='pre_target':proposed['target']='different-target'
    if case['state']=='pre_value':proposed['value']='999' if proposed['tool']=='credit_ledger' else 'different-value'
    reviewed=copy.deepcopy(proposed);review_ok=gate.review(reviewed)
    if case['state']=='late_target':proposed['target']='different-target'
    if case['state']=='late_value':proposed['value']='999' if proposed['tool']=='credit_ledger' else 'different-value'
    save(folder/'case.json',case);save(folder/'policy-at-execution.json',{'version':case['current_policy_version']})
    args=(adapter,gate,proposed,review_ok,case['current_policy_version'])
    if case['state']=='parallel_replay':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:events=list(pool.map(lambda _:apply(*args),range(2)))
    else:events=[apply(*args) for _ in range(2 if case['state']=='replay' else 1)]
    save(folder/'trace.json',{'origin':'constructed_fault_fixture','guard':guard,'reviewed_action':reviewed,'events':events})
    save(folder/'approval-final.json',gate.snapshot())
    return folder


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--partition',choices=['development','evaluation'],required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    selected=[g for g in goals() if g['partition']==a.partition]
    save(a.out/'launch.json',{'source_sha256':sha(__file__),'native_source_hashes':{x.name:sha(x) for x in VENDOR.glob('*.py')},'states':STATES,'guards':GUARDS,'base_goals':selected,'partition':a.partition})
    for g in selected:
        for state in STATES:
            for guard in GUARDS:constructed_cell(make_case(g,state),guard,a.out/g['partition']/g['base_goal_id']/state/guard)
    print('Completed all constructed local cells',flush=True)
