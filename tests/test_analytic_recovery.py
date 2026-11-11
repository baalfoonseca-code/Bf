"""Recovery and live-admission regressions on the complete shipped MQL module.

Broker history/bar APIs are explicit deterministic stubs, not exchange evidence.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest
from mql_engine_harness import compile_harness
from test_runtime_contract import TRAILER_PREFIX

SCENARIOS={
 'telemetry_columns_match_after_live_instrumentation':r'''
 resetRuntime();gHistory={trade(60001,1000),trade(60002,1100)};check(OMReadChunk(60003));
 gLatest=trade(60250,1110);gHistory.push_back(gLatest);check(OMAdmitMarketEvent());
 OMThesis current;OMCaptureThesis(60250,current);OMTelemetry("CHECK",current);
 check(gOMLiveCalls==1&&gOMLiveAdmitted==1);
 check(std::count(gWritten.front().begin(),gWritten.front().end(),',')==
       std::count(gWritten.back().begin(),gWritten.back().end(),','));
 ''',
 'long_silence_requests_recovery_not_permanent_release':r'''
 resetRuntime(); Inp_FeedMaxGapSec=30;
 gHistory={trade(60001,1000),trade(60002,1100),trade(105000,1100)};
 check(!OMReadChunk(105001)); check(gOMRecoveryPending && !gOMLive.ready);
 auto epoch=gOMEpoch; gLatest=trade(105000,1100);
 check(!OMAdmitMarketEvent()); check(gOMRecoveryPending && gOMEpoch==epoch);
 ''',
 'stable_broker_silence_rebuilds_with_new_epoch_no_past_signals':r'''
 resetRuntime(); gNow=32445; gSessionStartSec=32400; gSessionEndSec=61200;
 Inp_FeedMaxGapSec=30; Inp_DataChunksPerTimer=16;
 gHistory={trade(32400001,1000),trade(32400002,1100),trade(32445000,1100)};
 gLatest=gHistory.back(); OMFail("FEED_COVERAGE_GAP",true);
 auto before=gOMEpoch; OMService();
 check(gOMRecovering && gOMEpoch>before && !OMLiveReady(gLatest.time_msc));
 gNow=32461;gLatest=trade(32461000,1100);gHistory.push_back(gLatest);
 for(int i=0;i<30 && gOMRecovering;i++) OMService();
 check(!gOMRecovering && !gOMRecoveryPending && !gOMFault);
 check(OMLiveReady(gLatest.time_msc)); OMThesis out;check(!OMGetClosed(32400,out));
 check(gOMAttachMsc==gLatest.time_msc);
 ''',
 'independent_bar_detects_missing_tick_volume':r'''
 resetRuntime(); gOMRecovering=true; gOMRecoveryMinClose=120000;
 gHistory={trade(60001,1000),trade(60002,1100)}; gExpectedBarVolume=3;
 check(!OMReadChunk(120000));check(gOMRecoveryPending);
 check(gOMReason=="RECOVERY_BAR_VOLUME_MISMATCH" && !gOMLive.ready);
 ''',
 'temporary_history_unavailable_requires_controlled_restart':r'''
 resetRuntime(); gCopyError=4401;
 check(!OMReadChunk(60003));check(gOMRecoveryPending && !gOMVerified);
 gCopyError=0;gLatest=trade(60003,1100);gHistory={trade(60001,1000),gLatest};
 check(!OMAdmitMarketEvent()); // tick alone cannot clear the obligation
 ''',
 'new_epoch_invalidates_frozen_thesis_even_while_recovery_unready':r'''
 resetRuntime(); OMThesis frozen;ZeroMemory(frozen);
 frozen.detected=true;frozen.waveID=1;frozen.evidenceMsc=60001;frozen.dataEpoch=gOMEpoch;
 OMFail("TRAILING_FEED_GAP",true);string reason;
 check(OMRevalidate(frozen,reason)==-1 && reason=="FROZEN_EVIDENCE_REVISED");
 ''',
 'mixed_source_stays_hard_blocked_not_recoverable':r'''
 resetRuntime();auto a=trade(60001,1000),b=trade(60002,1100);b.volume_real=0;
 gHistory={a,b};check(!OMReadChunk(60003));check(gOMFault&&!gOMRecoveryPending);
 gLatest=b;OMService();check(gOMFault && !gOMLive.ready);
 ''',
 'live_tail_processes_new_trade_between_timers':r'''
 resetRuntime();gHistory={trade(60001,1000),trade(60002,1100)};
 check(OMReadChunk(60003));gLatest=trade(60250,1110);gHistory.push_back(gLatest);
 check(OMAdmitMarketEvent());check(gOMCursor==60251&&gOMWeighted.trades==3);
 check(gCopyCalls==1&&gMaxCountRequest==257);
 ''',
 'large_backlog_waits_for_timer_without_query_or_partial_commit':r'''
 resetRuntime();gHistory={trade(60001,1000),trade(60002,1100)};
 check(OMReadChunk(60003));gLatest=trade(62000,1110);gHistory.push_back(gLatest);
 auto cursor=gOMCursor;check(!OMAdmitMarketEvent());check(gCopyCalls==0&&gOMCursor==cursor);
 ''',
 'dense_same_ms_batch_is_never_partially_admitted':r'''
 resetRuntime();gHistory={trade(60001,1000),trade(60002,1100)};
 check(OMReadChunk(60003));
 for(int i=0;i<300;i++)gHistory.push_back(trade(60250,1110));
 gLatest=gHistory.back();check(!OMAdmitMarketEvent());
 check(gOMWeighted.trades==2&&gOMCursor==60003&&gMaxCountRequest==257);
 ''',
 'same_ms_return_to_same_price_keeps_all_trade_multiplicity':r'''
 resetRuntime();gHistory={trade(60001,1000),trade(60002,1100)};check(OMReadChunk(60003));
 gHistory.push_back(trade(60002,1110));gHistory.push_back(trade(60002,1100));gLatest=gHistory.back();
 check(OMAdmitMarketEvent());check(gOMWeighted.trades==4);
 check(OMAdmitMarketEvent());check(gOMWeighted.trades==4);
 ''',
 'recovery_bar_unavailable_never_approves_coverage':r'''
 resetRuntime();gOMRecovering=true;gRatesUnavailable=true;
 gHistory={trade(60001,1000),trade(60002,1100)};
 check(!OMReadChunk(120000));check(gOMRecoveryPending && !gOMLive.ready);
 ''',
}
for family in ['WIN','WDO']:
 for direction in [1,-1]:
  name='cont_two_tick_retreat_preserves_sustainment_'+family+'_'+str(direction).replace('-','minus')
  tick=5 if family=='WIN' else .5
  step=tick*2; start=1000 if family=='WIN' else 5000
  move=100 if family=='WIN' else 4
  SCENARIOS[name]=f"""
   resetRuntime();gTickSize={tick};gIsIndexFamily={'true' if family=='WIN' else 'false'};
   gCONT_MinDisplPts={50 if family=='WIN' else 1.5};
   gOMWaves.count=3;for(int i=0;i<3;i++)gOMWaves.closedVolume[i]=1;
   gHistory={{trade(60001,{start}),trade(60002,{start+direction*move})}};
   check(OMReadChunk(60003));gLatest=gHistory.back();OMThesis frozen;OMCaptureThesis(60002,frozen);
   check(frozen.detected && frozen.route=="CONT");string reason;check(OMRevalidate(frozen,reason)==1);
   gLatest=trade(60003,{start+direction*(move-tick)});gHistory.push_back(gLatest);check(OMReadChunk(60004));
   check(OMRevalidate(frozen,reason)==1);
   gLatest=trade(60004,{start+direction*(move-step)});gHistory.push_back(gLatest);check(OMReadChunk(60005));
   check(gOMWaves.active.dir=={direction});check(OMRevalidate(frozen,reason)==1);
   check(reason=="THESIS_VALID");
  """
class AnalyticRecoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='remora-recovery-')
  cases='\n'.join('if(name=="'+name+'") {'+body+' return 0;}' for name,body in SCENARIOS.items())
  trailer=TRAILER_PREFIX+'\nint main(int argc,char**argv){try{string name=argc>1?argv[1]:"";'+cases+'return 2;}catch(const std::exception&e){std::cerr<<e.what();return 1;}}'
  cls.binary=compile_harness(trailer,Path(cls.temp.name))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def run_case(self,name):
  p=subprocess.run([str(self.binary),name],text=True,capture_output=True)
  self.assertEqual(p.returncode,0,p.stderr)
for name in SCENARIOS:
 setattr(AnalyticRecoveryTests,'test_'+name,lambda self,n=name:self.run_case(n))
