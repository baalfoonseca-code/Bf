"""CONT callback regressions using shipped bodies and explicit terminal stubs.

FAR's boolean veto, accounting obligations and broker API are named stubs here.
These checks exercise ordering, causal arming and dispatch counts, not MT5,
real journal persistence, the FAR classifier or market fills.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest

from mql_engine_harness import compile_harness, translate_engine
from test_execution_integration import SHIMS, SETUP
from test_financial_invariants import declaration, functions

ROOT = Path(__file__).resolve().parents[1]
CASES = r'''
void retreat_setup(){
 fresh();gHistory.clear();
 gLatest=tick(32459998,1110);OMReset();
 gOMSessionOpen=32400;gOMSessionEnd=61200;gOMCursor=32400000;gOMAttachMsc=1;
 gOMWaves.count=3;for(int i=0;i<3;i++)gOMWaves.closedVolume[i]=1;
 gHistory={tick(32400001,800),gLatest};
 require(OMReadChunk(32459999));gNow=32459;
}
void close_retreat_and_arm(){
 retreat_setup();OnTick();require(!armed.active&&sends==0,"intrabar CONT armed");
 event(32459999,1100);require(OMReadChunk(32460000));
 OnTick();require(!armed.active&&sends==0,"armed before M1 boundary");
 event(32460001,1100);OnTick();
 require(armed.active&&armed.route=="CONT"&&armed.entry.trigger==1275,"closed retreat did not arm");
 require(gObjectiveArmed.price==1100&&gObjectiveArmed.evidenceMsc==32459999);
}
void recover_history(){
 fresh();
 // Three causally closed waves plus a current, sufficiently funded wave.
 // The low initial trade provides session dispersion; no hand-made thesis.
 gHistory={tick(32400001,100),tick(32400002,1100),tick(32400003,1040),
           tick(32400004,1100),tick(32400005,980),tick(32400006,1040),
           tick(32459999,1100)};
 gLatest=gHistory.back();gNow=32460;
 OMFail("FEED_COVERAGE_GAP",true);OnTimer();
 require(gOMRecovering&&!armed.active&&sends==0,"recovery emitted old entry");
 event(32520001,1100);
 for(int i=0;i<30&&gOMRecovering;i++)OnTimer();
 require(!gOMRecovering&&!gOMRecoveryPending&&!gOMFault,"recovery did not finish");
 require(gOMAttachMsc==32520001&&!armed.active&&sends==0,"recovery retroactively armed");
 OMThesis old;require(!OMGetClosed(32460,old),"reconstructed M1 exposed");
}
int main(int argc,char**argv){try{
 string name=argc>1?argv[1]:"";
 if(name=="retreat_cont_arms_only_after_closed_m1"){
  close_retreat_and_arm();require(sends==0);
 }else if(name=="far_veto_still_blocks_retreated_cont_dispatch"){
  close_retreat_and_arm();gFarVeto=true;event(32460250,1280);OnTick();
  require(sends==0&&preparations==0&&barriers==0,"FAR veto bypassed");
  require(std::find(gCallTrace.begin(),gCallTrace.end(),"FAR")!=gCallTrace.end());
 }else if(name=="financial_protection_precedes_live_query_after_retreat"){
  close_retreat_and_arm();gCallTrace.clear();event(32460250,1280);OnTick();
  auto data=std::find(gCallTrace.begin(),gCallTrace.end(),"history_live");
  for(const string tag:{"accounting","EOD","BE"}){
   auto call=std::find(gCallTrace.begin(),gCallTrace.end(),tag);
   require(call!=gCallTrace.end()&&data!=gCallTrace.end()&&call<data,"finance ran after analysis");
  }
  require(sends==1&&barriers==1);
 }else if(name=="recovery_waits_for_new_m1_and_never_duplicates_dispatch"){
  recover_history();OnTick();OnTimer();require(!armed.active&&sends==0);
  event(32579999,1100);OnTick();require(!armed.active&&sends==0);
  event(32580001,1100);for(int i=0;i<20&&!armed.active;i++)OnTimer();
  require(armed.active&&gObjectiveArmed.evidenceMsc==32579999,"fresh closed M1 not armed: "+gOMReason+" closed="+gOMClosed.reason+" detect="+std::to_string(gOMClosed.detected)+" eligible="+std::to_string(gOMClosed.eligible)+" cursor="+std::to_string(gOMCursor)+" attach="+std::to_string(gOMAttachMsc)+" diag="+lastReason);
  event(32580250,1280);OnTick();require(sends==1&&barriers==1);
  OnTick();OnTimer();OnTick();require(sends==1&&barriers==1,"duplicated request");
 }else if(name=="uncertain_request_owns_armed_signal_through_recovery"){
  close_retreat_and_arm();inFlight=true;gPendingExec.active=true;
  OMFail("FEED_COVERAGE_GAP",true);auto epoch=gOMEpoch;
  event(32460250,1280);OnTick();OnTimer();
  require(armed.active&&inFlight&&gPendingExec.active,"analysis cleared financial obligation");
  require(sends==0&&preparations==0&&gOMEpoch>=epoch);
 }else if(name=="accounting_obligation_blocks_retreated_cont"){
  close_retreat_and_arm();gAccountingUnresolved=true;
  event(32460250,1280);OnTick();OnTimer();
  require(armed.active&&gAccountingUnresolved&&sends==0&&preparations==0);
 }else return 2;
 return 0;
 }catch(const std::exception&e){std::cerr<<e.what();return 1;}}
'''


class ContExecutionSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / 'RemoraScalper_MatrizObjetiva.mq5').read_text()
        found = functions(source)
        structs = '\n'.join(declaration(source, kind, name) + ';' for kind, name in (
            ('enum', 'ENTRY_PHASE'), ('struct', 'EntryTriggerState'),
            ('struct', 'ArmedSignal'), ('enum', 'EXIT_MODE')))
        names = ['DirStr', 'NormPriceDigits', 'RoundUpTick', 'RoundDownTick',
                 'EntryGridValid', 'EntryTimeoutExpired', 'InitSignalCloseTrigger',
                 'EntryRealTrade', 'ObserveEntryTrade', 'ValidateEntryDispatch',
                 'ClaimEntryDispatch', 'NormEntrySL', 'NormEntryTP', 'ArmedTriggerReady',
                 'ArmedTriggerPrice', 'ObjectiveContInsideB3', 'ResetArmedSignal',
                 'ObjectiveRevalidate', 'EntryDispatchGuard', 'SpreadOk', 'EntryTPValid',
                 'SendOrder', 'EvaluateMatrix', 'ProcessArmedSignal',
                 'ObjectiveDecisionCycle', 'OnTick', 'OnTimer']
        body = '\n'.join(found[name] for name in names)
        # Expose the existing callback's boolean veto, without replacing any EA body.
        old = 'bool FARBeforeDecision(){gCallTrace.push_back("FAR");return false;}'
        assert SHIMS.count(old) == 1
        shims = SHIMS.replace(old, 'bool gFarVeto=false;\n'
                              'bool FARBeforeDecision(){gCallTrace.push_back("FAR");return gFarVeto;}')
        cls.temp = tempfile.TemporaryDirectory(prefix='remora-cont-safety-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = compile_harness(
            structs + '\nArmedSignal armed;EXIT_MODE Inp_ExitMode=PROGRESSIVE_NO_TP;\n'
            + shims + translate_engine(body) + SETUP.split('int main(', 1)[0] + CASES,
            Path(cls.temp.name), 'cont_safety')

    def run_case(self, name):
        result = subprocess.run([str(self.binary), name], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


for _name in ('retreat_cont_arms_only_after_closed_m1',
              'far_veto_still_blocks_retreated_cont_dispatch',
              'financial_protection_precedes_live_query_after_retreat',
              'recovery_waits_for_new_m1_and_never_duplicates_dispatch',
              'uncertain_request_owns_armed_signal_through_recovery',
              'accounting_obligation_blocks_retreated_cont'):
    setattr(ContExecutionSafetyTests, 'test_' + _name,
            lambda self, name=_name: self.run_case(name))
