"""CONT regressions on the shipped engine with deterministic terminal stubs.

These tests execute OMWavePush/OMClassify/OMRevalidate from ObjectiveMatrix.mqh.
They are portable simulated-service tests, not native MQL5/MT5 execution.
The guard fixtures explicitly seed insufficient effort/progress; cumulative wave
volume cannot naturally decrease against its frozen prior-wave baseline.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest

from mql_engine_harness import compile_harness
from test_runtime_contract import TRAILER_PREFIX


SETUP = r'''
int side=1;
double origin=0,advance=0,grid=0,reversal=0;
long clockMsc=60002;
OMThesis frozenCont;
void contSetup(bool win,int direction){
 resetRuntime();side=direction;
 gIsIndexFamily=win;gTickSize=win?5:.5;grid=gTickSize;
 origin=win?100000:5000;advance=win?300:12;
 reversal=win?Inp_WaveReversalPts_WIN:Inp_WaveReversalPts_WDO;
 gCONT_MinDisplPts=win?50:1.5;Inp_PathEventTicks=2;
 gOMWaves.count=3;gOMWaves.next=3;
 for(int i=0;i<3;i++)gOMWaves.closedVolume[i]=1;
 gHistory={trade(60001,origin),trade(60002,origin+side*advance)};
 require(OMReadChunk(60003),"initial chunk");gLatest=gHistory.back();clockMsc=60002;
 OMCaptureThesis(clockMsc,frozenCont);
 require(frozenCont.detected && frozenCont.route=="CONT" && frozenCont.dir==side,"initial CONT");
 require(frozenCont.classification==(side==1?1:2),"initial classification");
 string reason;require(OMRevalidate(frozenCont,reason)==1 && reason=="THESIS_VALID","initial revalidation");
}
void contEvent(double price){
 ++clockMsc;gLatest=trade(clockMsc,price);gHistory.push_back(gLatest);
 require(OMReadChunk(clockMsc+1),"retreat chunk");
}
void expectValid(){
 OMDecision d;OMConfig c=OMConfiguration();
 OMClassify(gOMWaves,gOMLastPrice,clockMsc,c,d);
 require(d.classification==(side==1?1:2),"CONT classification after retreat");
 require(d.waveID==frozenCont.waveID && d.dir==frozenCont.dir,"same directional wave");
 require(d.netProgress>=c.minCont && d.pathEfficiency>=c.contEfficiency &&
         d.effort>=c.contEffort,"existing evidence remains satisfied");
 string reason;require(OMRevalidate(frozenCont,reason)==1 && reason=="THESIS_VALID","CONT revalidation after retreat");
}
void expectProgressLost(){
 OMDecision d;OMClassify(gOMWaves,gOMLastPrice,clockMsc,OMConfiguration(),d);
 require(d.classification!=1 && d.classification!=2,"initial classifier must reject lost CONT evidence");
 string reason;require(OMRevalidate(frozenCont,reason)==-1 &&
     reason=="CONT_PROGRESS_OR_SUSTAINMENT_LOST","revalidation must reject lost CONT evidence");
}
'''

SCENARIOS = {}
for family in ("WIN", "WDO"):
    for direction, label in ((1, "BUY"), (-1, "SELL")):
        prefix = f"{family}_{label}_"
        setup = f"contSetup({'true' if family == 'WIN' else 'false'},{direction});\n"
        cases = {
            "two_ticks_and_resumption": r'''
 contEvent(origin+side*(advance-2*grid));
 require(gOMWaves.active.id==frozenCont.waveID,"two ticks must not reverse structural wave");
 expectValid();
 contEvent(origin+side*(advance+grid));expectValid();
''',
            "two_ticks_revalidation_without_reclassification": r'''
 contEvent(origin+side*(advance-2*grid));
 string reason;require(OMRevalidate(frozenCont,reason)==1 && reason=="THESIS_VALID","independent revalidation tolerates two ticks with sustained evidence");
''',
            "larger_retreat_with_sustained_thesis": r'''
 double retreat=(gIsIndexFamily?4:3)*grid;
 require(retreat>2*grid && retreat<reversal,"larger but substructural fixture");
 contEvent(origin+side*(advance-retreat));expectValid();
 contEvent(origin+side*(advance+grid));expectValid();
''',
            "one_tick_below_structural_reversal": r'''
 contEvent(origin+side*(advance-reversal+grid));
 require(gOMWaves.active.id==frozenCont.waveID,"below reversal keeps wave identity");
 expectValid();
''',
            "structural_reversal_at_threshold": r'''
 contEvent(origin+side*(advance-reversal));
 require(gOMWaves.active.id!=frozenCont.waveID && gOMWaves.active.dir==-side,"causal structural reversal");
 string reason;require(OMRevalidate(frozenCont,reason)==-1 && reason=="CONT_WAVE_REVERSED","structural reversal invalidates CONT");
 OMDecision d;OMClassify(gOMWaves,gOMLastPrice,clockMsc,OMConfiguration(),d);
 require(d.classification!=frozenCont.classification,"reversed wave cannot classify old continuation");
''',
            "structural_reversal_above_threshold": r'''
 contEvent(origin+side*(advance-reversal-grid));
 string reason;require(OMRevalidate(frozenCont,reason)==-1 && reason=="CONT_WAVE_REVERSED","larger structural reversal invalidates CONT");
''',
            "efficiency_loss_without_structural_reversal": r'''
 for(int i=0;i<30;i++){
  contEvent(origin+side*(advance-2*grid));
  contEvent(origin+side*advance);
 }
 require(gOMWaves.active.id==frozenCont.waveID && gOMWaves.active.dir==side,"oscillation remains one wave");
 auto w=gOMWaves.active;auto c=OMConfiguration();
 require(w.dir*(w.eventPrice-w.start)/w.eventPath<c.contEfficiency,"efficiency objectively lost");
 require(w.dir*(gOMLastPrice-w.start)>=c.minCont && w.volume/w.baseline>=c.contEffort,"other numeric guards remain satisfied");
 expectProgressLost();
''',
            "effort_guard_fixture": r'''
 // Boundary fixture for the preserved guard, not a claim that live volume decreases.
 gOMWaves.active.volume=gOMWaves.active.baseline*Inp_CONT_Effort/2;
 expectProgressLost();
''',
            "net_progress_guard_fixture": r'''
 // Seed a same-direction subthreshold net with ample sampled efficiency.
 // This isolates the net guard rather than changing any production input.
 auto &w=gOMWaves.active;
 w.start=gOMLastPrice-side*(gCONT_MinDisplPts-grid);
 w.eventPrice=gOMLastPrice;w.eventPath=gCONT_MinDisplPts-grid;
 require(w.dir*(w.eventPrice-w.start)/w.eventPath>=Inp_CONT_MinPathEfficiency,"efficiency still sufficient");
 expectProgressLost();
''',
            "sampling_scale_has_no_separate_drawdown_veto": r'''
 contEvent(origin+side*(advance-2*grid));
 // Same already measured trajectory: changing sampling config cannot impose
 // a second, independent strategic maximum retreat on classification/validation.
 for(int scale=1;scale<=3;scale++){
  Inp_PathEventTicks=scale;expectValid();
 }
''',
            "closed_m1_retreat_is_causal_and_snapshot_frozen": r'''
 // Rebuild this minute through its actual boundary; the following trade must
 // neither enter the M1 snapshot nor mutate its frozen measurements.
 resetRuntime();gTickSize=grid;gCONT_MinDisplPts=gIsIndexFamily?50:1.5;
 OMWaveReset(gOMWaves);gOMWaves.count=3;gOMWaves.next=3;
 for(int i=0;i<3;i++)gOMWaves.closedVolume[i]=1;
 OMWeightedReset(gOMWeighted);OMWeightedReset(gOMReference);
 gOMCursor=60000;gOMBoundaryMsc=0;ArrayResize(gOMBoundary,0);
 gHistory={trade(60001,origin),trade(119998,origin+side*advance),
           trade(119999,origin+side*(advance-2*grid)),
           trade(120000,origin+side*(advance-reversal))};
 require(OMReadChunk(120000),"closed M1 chunk");gLatest=gHistory[2];clockMsc=119999;
 OMThesis closed;require(OMGetClosed(60,closed),"closed M1 snapshot available");
 require(closed.detected && closed.route=="CONT" && closed.dir==side,"closed M1 includes valid two-tick retreat");
 auto saved=closed;frozenCont=closed;expectValid();
 require(!OMGetClosed(120,closed),"current M1 cannot supply signal");
 require(OMReadChunk(120001),"following M1 trade");gLatest=gHistory.back();
 require(saved.price==origin+side*(advance-2*grid) && saved.evidenceMsc==119999,"frozen snapshot retained causal data");
 string reason;require(OMRevalidate(saved,reason)==-1 && reason=="CONT_WAVE_REVERSED","following structural reversal still cancels");
''',
        }
        for name, body in cases.items():
            SCENARIOS[prefix + name] = setup + body


class ContSustainmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="remora-cont-sustainment-")
        cls.addClassCleanup(cls.temp.cleanup)
        cases = "\n".join(f'if(name=="{name}"){{{body}\nreturn 0;}}'
                          for name, body in SCENARIOS.items())
        trailer = TRAILER_PREFIX + SETUP + '\nint main(int argc,char**argv){try{'
        trailer += 'string name=argc>1?argv[1]:"";' + cases
        trailer += 'return 2;}catch(const std::exception&e){std::cerr<<e.what();return 1;}}'
        cls.binary = compile_harness(trailer, Path(cls.temp.name), "cont_sustainment")

    def run_case(self, name):
        result = subprocess.run([str(self.binary), name], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


for _name in SCENARIOS:
    setattr(ContSustainmentTests, "test_" + _name,
            lambda self, name=_name: self.run_case(name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
