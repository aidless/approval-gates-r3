"""Run unmodified official component tests with import-only package scaffolding."""
import sys
import types
import pytest
from audit_core import VENDOR,load_agt

for name in ('agentmesh','agentmesh.governance'):
    p=types.ModuleType(name);p.__path__=[];sys.modules[name]=p
sys.modules['agentmesh.governance.approval_protocol']=load_agt()
# VENDOR: src/agentmesh/governance/approval_protocol, package root is parents[3].
test=VENDOR.parents[3]/'tests/test_approval_protocol.py'
if __name__=='__main__':raise SystemExit(pytest.main(['-q',str(test)]))
