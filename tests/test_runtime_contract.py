"""Adversarial collector tests against the complete delivered MQL5 include.

The shared harness mechanically adapts MQL syntax and stubs terminal services.
It does not replace the collector, snapshot or numerical implementation.
"""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mql_engine_harness import compile_harness
from test_entry_contract import function_source


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    "same_ms_multiplicity_and_append_once": r"""
        resetRuntime();
        gHistory={trade(60001,100),trade(60001,102)};
        check(OMReadChunk(60002)); check(gOMWeighted.trades==2);
        check(gOMWeighted.weight==2 && gOMWeighted.mean==101);
        gHistory.push_back(trade(60001,104));
        check(OMVerifyBoundary()); check(gOMWeighted.trades==3);
        check(gOMWeighted.weight==3 && gOMWeighted.mean==102);
        check(OMVerifyBoundary()); check(gOMWeighted.trades==3);
        gHistory.push_back(trade(60002,106));
        check(OMReadChunk(60003)); check(gOMWeighted.trades==4);
        check(gOMWeighted.weight==4 && gOMWeighted.mean==103);
    """,
    "same_ms_reordering_is_revision": r"""
        resetRuntime(); gHistory={trade(60001,100),trade(60001,102)};
        check(OMReadChunk(60002));
        std::swap(gHistory[0],gHistory[1]);
        check(!OMVerifyBoundary()); check(gOMFault && !gOMLive.ready);
        check(gOMWeighted.trades==2);
    """,
    "same_ms_removed_record_is_revision": r"""
        resetRuntime(); gHistory={trade(60001,100),trade(60001,102)};
        check(OMReadChunk(60002)); gHistory.pop_back();
        check(!OMVerifyBoundary()); check(gOMFault && !gOMLive.ready);
    """,
    "future_trade_excluded_from_closed_m1": r"""
        resetRuntime();
        gHistory={trade(119999,100),trade(119999,110),trade(120000,10000)};
        check(OMReadChunk(120000)); OMThesis closed;
        check(OMGetClosed(60,closed));
        check(closed.bands.asofMsc==119999 && closed.bands.vwap==105);
        check(!OMGetClosed(120,closed));
        check(OMGetClosed(60,closed)); auto frozen=closed;
        check(OMReadChunk(120001));
        check(gOMLive.vwap>3000 && frozen.bands.vwap==105);
    """,
    "late_boundary_append_invalidates_frozen_epoch": r"""
        resetRuntime(); gHistory={trade(119999,100),trade(119999,110)};
        check(OMReadChunk(120000)); OMThesis frozen;
        check(OMGetClosed(60,frozen)); auto epoch=gOMEpoch;
        frozen.detected=true; frozen.waveID=1; frozen.evidenceMsc=119999;
        gHistory.push_back(trade(119999,120)); gLatest=trade(119999,120);
        check(OMVerifyBoundary()); check(gOMEpoch>epoch);
        OMThesis discarded; check(!OMGetClosed(60,discarded));
        string reason; check(OMRevalidate(frozen,reason)==-1);
        check(reason=="FROZEN_EVIDENCE_REVISED");
        check(frozen.bands.vwap==105);
    """,
    "rebuild_does_not_publish_past_bar": r"""
        resetRuntime(); gOMAttachMsc=120000;
        gHistory={trade(119999,100),trade(119999,110)};
        check(OMReadChunk(120000)); OMThesis out;
        check(!OMGetClosed(60,out));
    """,
    "source_mixture_fails_before_partial_batch": r"""
        resetRuntime(); auto real=trade(60001,100),integer=trade(60002,110);
        integer.volume_real=0; integer.volume=1; gHistory={real,integer};
        check(!OMReadChunk(60003)); check(gOMFault);
        check(gOMWeighted.trades==0 && gOMWeighted.weight==0);
    """,
    "integer_trade_volume_is_valid": r"""
        resetRuntime(); auto a=trade(60001,100),b=trade(60002,110);
        a.volume_real=b.volume_real=0; a.volume=2; b.volume=3;
        gHistory={a,b}; check(OMReadChunk(60003));
        check(gOMWeighted.trades==2 && gOMWeighted.weight==5);
        check(std::abs(gOMWeighted.mean-106)<1e-12 && gOMSource==2);
    """,
    "gap_prevents_readiness": r"""
        resetRuntime(); Inp_FeedMaxGapSec=1;
        gHistory={trade(60001,100),trade(62002,110)};
        check(!OMReadChunk(62003)); check(gOMFault && !gOMLive.ready);
    """,
    "current_quote_ahead_of_verified_cursor_waits": r"""
        resetRuntime(); gHistory={trade(60001,100),trade(60002,110)};
        check(OMReadChunk(60003));
        gLatest=gHistory.back();
        check(OMLiveReady(60002));
        check(!OMLiveReady(60003));
        check(!OMLiveReady(60004));
    """,
    "zero_nan_and_missing_volume_rejected": r"""
        resetRuntime(); auto t=trade(60001,100); double volume; int source;
        t.volume_real=0; t.volume=0; check(!OMTradeValid(t,volume,source));
        t.volume_real=NAN; t.volume=1; check(!OMTradeValid(t,volume,source));
        t=trade(60001,100); t.flags=0; check(!OMTradeValid(t,volume,source));
        t=trade(60001,100); t.time=0; check(!OMTradeValid(t,volume,source));
    """,
    "warmup_is_minimum_not_statistical_guarantee": r"""
        resetRuntime(); Inp_BandsWarmupSec=300;
        gHistory={trade(60001,100),trade(60002,110)};
        check(OMReadChunk(60003)); check(!gOMLive.ready);
        check(gOMReason=="BANDS_WARMUP");
        gHistory.push_back(trade(360000,100));
        check(OMReadChunk(360001)); check(gOMLive.ready);
        Inp_BandsMinTrades=10; OMUpdateReadiness(360000);
        check(!gOMLive.ready && gOMReason=="TRADE_COUNT_NOT_READY");
    """,
    "elapsed_time_cannot_make_flat_prices_ready": r"""
        resetRuntime(); Inp_BandsWarmupSec=300;
        gHistory={trade(60001,100),trade(360000,100)};
        check(OMReadChunk(360001));
        check(!gOMLive.ready && gOMReason=="DISPERSION_UNAVAILABLE");
    """,
    "ambiguous_sessions_require_explicit_override": r"""
        resetRuntime(); gNow=36000; gSessionCount=2;
        Inp_RegularSessionStartHHMM=-1; Inp_RegularSessionEndHHMM=-1;
        check(!OMResolveSession());
        check(gOMReason=="SESSION_AMBIGUOUS_SET_REGULAR_HHMM");
        Inp_RegularSessionStartHHMM=900; Inp_RegularSessionEndHHMM=1700;
        check(OMResolveSession());
        check(gOMSessionOpen==32400 && gOMSessionEnd==61200);
    """,
    "missing_session_does_not_use_order_start_time": r"""
        resetRuntime(); gNow=36000; gSessionCount=0;
        check(!OMResolveSession());
        check(gOMReason=="SESSION_SCHEDULE_UNAVAILABLE");
    """,
    "regular_override_must_fit_published_session": r"""
        resetRuntime(); gNow=36000; gSessionCount=1;
        Inp_RegularSessionStartHHMM=800; Inp_RegularSessionEndHHMM=1700;
        check(!OMResolveSession());
        check(gOMReason=="REGULAR_OVERRIDE_OUTSIDE_PUBLISHED_SESSION");
    """,
    "disconnect_revokes_ready_and_reconnect_changes_epoch": r"""
        resetRuntime(); gHistory={trade(60001,100),trade(60002,110)};
        check(OMReadChunk(60003)); check(gOMLive.ready);
        auto epoch=gOMEpoch; gConnected=false; OMService();
        check(!gOMLive.ready && gOMReason=="TERMINAL_DISCONNECTED");
        gConnected=true; gNow=36000; gLatest=trade(36000000,100);
        gSessionCount=1; Inp_RegularSessionStartHHMM=-1;
        Inp_RegularSessionEndHHMM=-1; OMService();
        check(gOMEpoch>epoch && gOMAttachMsc==36000000);
        OMThesis out; check(!OMGetClosed(60,out));
    """,
    "revalidation_waits_when_quote_last_disagrees_with_history": r"""
        resetRuntime();
        gOMWaves.count=3;
        for(int i=0;i<3;i++) gOMWaves.closedVolume[i]=1;
        gHistory={trade(60001,1000),trade(60002,1100)};
        check(OMReadChunk(60003));
        gLatest=trade(60002,1100); OMThesis frozen;
        OMCaptureThesis(60002,frozen); check(frozen.detected);
        string reason; check(OMRevalidate(frozen,reason)==1);
        gLatest.last=1099; // same timestamp, different Last than verified history
        check(OMRevalidate(frozen,reason)==0);
    """,
    "unseen_same_ms_price_or_volume_waits_quote_only_retains_known_last": r"""
        resetRuntime(); gHistory={trade(60001,100),trade(60002,110)};
        check(OMReadChunk(60004));
        gLatest=gHistory.back(); check(OMLiveReady(60002));
        gLatest.last=111; check(!OMLiveReady(60002));
        gLatest=gHistory.back(); gLatest.volume_real=2;
        check(!OMLiveReady(60002));
        gLatest=trade(60003,110); gLatest.flags=0;
        check(OMLiveReady(60003));
        gLatest.last=111; check(!OMLiveReady(60003));
    """,
}
TRAILER_PREFIX = r"""
void check(bool value){if(!value) throw std::runtime_error("runtime assertion failed");}
MqlTick trade(long msc,double p){
 MqlTick t{}; t.time=msc/1000; t.time_msc=msc; t.last=p;
 t.bid=p; t.ask=p+1; t.volume=1; t.volume_real=1;
 t.flags=TICK_FLAG_LAST|TICK_FLAG_VOLUME; return t;
}
void resetRuntime(){
 gNow=120; gLatest=trade(120000,100); gCopyError=0; gConnected=true;
 gTickSize=1; gBandMultiplier=1; gHistory.clear(); OMReset();
 gOMSessionOpen=60; gOMSessionEnd=10000; gOMCursor=60000;
 gOMAttachMsc=1;
 Inp_BandsWarmupSec=0; Inp_BandsMinTrades=2; Inp_BandsMinSigmaTicks=.1;
 Inp_FeedMaxGapSec=1000; Inp_DataMaxChunkTrades=50000;
 Inp_SigmaCheckToleranceTicks=.000001;
}
"""


class RuntimeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="remora-runtime-")
        cases = "\n".join(f'if(name=="{name}"){{{body}\nreturn 0;}}'
                          for name, body in SCENARIOS.items())
        trailer = TRAILER_PREFIX + '\nint main(int argc,char**argv){try{'
        trailer += 'string name=argc>1?argv[1]:"";' + cases
        trailer += 'return 2;}catch(const std::exception&e){std::cerr<<e.what();return 1;}}'
        cls.binary = compile_harness(trailer, Path(cls.temp.name))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_scenario(self, name):
        result = subprocess.run([str(self.binary), name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


def _scenario_test(name):
    def test(self):
        self.run_scenario(name)
    return test


for _name in SCENARIOS:
    setattr(RuntimeContractTest, "test_" + _name, _scenario_test(_name))


class ClosedBarIntegrationTest(unittest.TestCase):
    def test_ea_requests_closed_shift_one_snapshot(self):
        text = (ROOT / "RemoraScalper_MatrizObjetiva.mq5").read_text()
        function = function_source(text, "EvaluateMatrix")
        match = re.search(r"datetime\s+(\w+)\s*=\s*iTime\(Symbol\(\),Inp_SignalTF,1\)", function)
        self.assertIsNotNone(match, "The source must explicitly obtain shift 1")
        self.assertRegex(function, r"OMGetClosed\(" + match.group(1) + r",s\)")
        self.assertIn("+PeriodSeconds(Inp_SignalTF)!=bar", function)


if __name__ == "__main__":
    unittest.main()
