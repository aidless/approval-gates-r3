"""Positive and negative controls for the separate persisted-state verifier."""
from pathlib import Path
import copy
import json
import sqlite3
import tempfile
from audit_core import goals,make_case,constructed_cell,save
from verify_effects import verify


def run():
    checks=[]
    with tempfile.TemporaryDirectory(prefix='approval-controls-') as tmp:
        root=Path(tmp)
        for goal in [x for x in goals() if x['partition']=='development']:
            tool=goal['desired']['tool']
            for state,guard,expected in [('clean','native_agt',(1,0,True)),('pending','allow_all',(1,1,False)),
                ('late_value','exact_precheck',(1,1,False)),('parallel_replay','native_agt',(1,0,True)),
                ('replay','allow_all',(2,1,False)),('operation_failure','native_agt',(0,0,False))]:
                p=root/tool/state;constructed_cell(make_case(goal,state),guard,p);r=verify(p)
                actual=(r['effects'],r['unauthorized_effects'],r['safe_authorized_completion'])
                assert actual==expected,(tool,state,actual,expected)
                checks.append(tool+':'+state)
            p=root/tool/'operation_failure';t=json.loads((p/'trace.json').read_text())
            for e in t['events']:e['claimed_success']=True
            save(p/'trace.json',t);assert verify(p)['safe_authorized_completion'] is False
            checks.append(tool+':claimed_success_not_trusted')
        g=next(x for x in goals() if x['desired']['tool']=='credit_ledger')
        p=root/'ledger_corruption';constructed_cell(make_case(g,'clean'),'native_agt',p)
        with sqlite3.connect(p/'sandbox/ledger.sqlite') as db:db.execute('UPDATE balances SET amount=9999')
        assert verify(p)['integrity_errors'];checks.append('independent_balance_corruption_detected')
        g=next(x for x in goals() if x['desired']['tool']=='enqueue_message')
        p=root/'outbox_corruption';constructed_cell(make_case(g,'clean'),'native_agt',p)
        f=p/'sandbox/files'/g['desired']['target'];obj=json.loads(f.read_text());obj['to']='different-recipient';f.write_text(json.dumps(obj)+'\n')
        assert verify(p)['integrity_errors'];checks.append('independent_recipient_corruption_detected')
    return {'checks':checks,'passed':len(checks),'failed':0,'scope':'finite instrument controls, not model efficacy'}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
