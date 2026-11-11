"""Synthetic full callback/decision/dispatch sequence using shipped function bodies.

Financial server APIs are named stubs. API attempts here are NOT real fills or
market latency. Legacy OnTick is read from the preserved parent Git revision.
"""
from pathlib import Path
import subprocess,tempfile,unittest,hashlib
from mql_engine_harness import compile_harness,translate_engine
from test_financial_invariants import functions,declaration

ROOT=Path(__file__).resolve().parents[1]
SHIMS=r'''
constexpr int SYMBOL_DIGITS=1,SYMBOL_TRADE_STOPS_LEVEL=2,SYMBOL_POINT=3;
constexpr int ACCOUNT_MARGIN_FREE=4,ORDER_TYPE_BUY=0,ORDER_TYPE_SELL=1,ORDER_FILLING_FOK=1;
constexpr uint TRADE_RETCODE_DONE=10009,TRADE_RETCODE_PLACED=10008,TRADE_RETCODE_DONE_PARTIAL=10010;
using ENUM_ORDER_TYPE=int;
long SymbolInfoInteger(const string&,int key){return key==SYMBOL_DIGITS?8:0;}
double SymbolInfoDouble(const string&,int){return 1;}
double AccountInfoDouble(int){return 100000;}
double NormalizeDouble(double x,int digits){double p=std::pow(10.,digits);return std::round(x*p)/p;}
bool OrderCalcMargin(int,const string&,double,double,double &m){m=1;return true;}
datetime TimeCurrent(){return gNow;}
datetime iTime(const string&,int tf,int shift){return gLatest.time_msc/(tf*1000)*tf-shift*tf;}
double iClose(const string&,int,int){return 1100;}
int Inp_ArmedTimeoutSec=300,Inp_StopEntryHHMM=1530,Inp_StartHHMM=900,Inp_MaxTradesDay=10;
int Inp_CooldownSec=0,Inp_LossCooldownSec=0,Inp_EOD_CloseHHMM=1750;
int ordersEnteredToday=0,gMagicCore=60001,gMaxDeviationPts=100;
bool gAccountingUnresolved=false,dailyRiskBlocked=false,lastTradeWasLoss=false;
bool inFlight=false,position=false;datetime lastCloseConfirmedTime=0,BacktestStart=0;
double gBreakoutMargin=175,gMaxOvershoot=100,gSpreadMaxPts=30,gSL_Pts=400,gTP_Pts=2000;
double gLastBreakoutPrice=0;
datetime gLastMatrixEvalBar=0,gObjectiveAttachBar=0,gObjectiveObservedBar=0,gCachedMicroBar=0;
datetime gFinancialTimerDue=0,gLastFlushTime=0;int gDayKey=1970000;
int gEntryDiagnosticHandle=-1,csvTradeHandle=-1,sends=0,barriers=0,preparations=0,proofs=0;
long sentAtMsc=0;string lastReason;OMThesis gObjectiveArmed;
struct {bool active=false;} gOpenPos;
struct {bool active=false;double breakoutPrice=0;bool breakoutPriceAvailable=false;} gPendingExec;
struct MqlTradeResult {uint retcode=TRADE_RETCODE_DONE,request_id=1;ulong order=1,deal=0;};
struct BrokerStub {
 void SetExpertMagicNumber(int){} void SetTypeFilling(int){}
 bool PositionOpen(const string&,int,double,double,double,double,const string&){
   ++sends;sentAtMsc=gLatest.time_msc;gCallTrace.push_back("PositionOpen");return true;
 }
 uint ResultRetcode(){return TRADE_RETCODE_DONE;}
 ulong ResultOrder(){return 1;}ulong ResultDeal(){return 0;}
 void Result(MqlTradeResult &r){r=MqlTradeResult{};}
} trade;
bool OperationalAccountModeSupported(){return true;}
bool HasOpenPosition(){return position;}bool HasExecutionInFlight(){return inFlight;}
bool HasOwnPendingOrder(){return inFlight;}
bool FARBeforeDecision(){gCallTrace.push_back("FAR");return false;}
void FARClearEvidence(){} void FARCaptureArm(){}
bool FARPriceValid(double x){return x>0&&std::isfinite(x);}
string NewEntrySignalID(){return "SYNTHETIC_SIGNAL";}
void WriteEntryDiagnostic(const ArmedSignal&,string event){lastReason=event;}
void WriteAuditRow(string event,string,string,double,double,double,double,double){lastReason=event;}
void SyncAccountingState(bool=false){gCallTrace.push_back("accounting");}
void UpdateMAEMFE(){gCallTrace.push_back("excursion");}
void ProcessEOD(int){gCallTrace.push_back("EOD");}
void ManageBreakEven(){gCallTrace.push_back("BE");}
void ReconcileBreakEvenProofs(){++proofs;gCallTrace.push_back("BE_PROOF");}
void DailyReset(){gCallTrace.push_back("daily_reset");}
bool PreparePendingExec(int,string,string,double,double,double,double){++preparations;gPendingExec.active=true;return true;}
bool MarkRequestDispatchPossible(bool){++barriers;gCallTrace.push_back("barrier");return true;}
void ResetPendingExec(){gPendingExec.active=false;}
void CompletePendingExec(bool,uint,ulong,ulong,uint){inFlight=true;}
int RememberEntryDispatch(){return 0;}
void BindEntryDispatch(int,ulong,ulong,uint){}
double ComputeLotsForEntry(int,double,double){return 1;}
'''
SETUP=r'''
MqlTick tick(long ms,double p){auto t=make_tick(ms,p);t.ask=p;t.bid=p-5;return t;}
void fresh(){
 gNow=32460;gLatest=tick(32460001,1100);gHistory.clear();gCallTrace.clear();
 gTickSize=5;gBandMultiplier=.8;gABS_MinDisplPts=60;gCONT_MinDisplPts=50;
 Inp_FeedMaxGapSec=1000;Inp_BandsWarmupSec=0;Inp_BandsMinSigmaTicks=.1;
 Inp_DataChunksPerTimer=16;inFlight=position=gAccountingUnresolved=dailyRiskBlocked=false;
 sends=barriers=preparations=proofs=0;sentAtMsc=0;gPendingExec.active=false;
 OMReset();gOMSessionOpen=32400;gOMSessionEnd=61200;gOMCursor=32400000;gOMAttachMsc=1;
 gOMWaves.count=3;for(int i=0;i<3;i++)gOMWaves.closedVolume[i]=1;
 gHistory={tick(32400001,800),tick(32459999,1100)};
 require(OMReadChunk(32460000));gHistory.push_back(gLatest);
 ZeroMemory(armed);ZeroMemory(gObjectiveArmed);gObjectiveAttachBar=0;gLastMatrixEvalBar=0;
 gObjectiveObservedBar=0;gFinancialTimerDue=32461;gDayKey=1970000;
}
void arm(){fresh();OnTick();require(armed.active,"closed M1 did not arm");require(armed.entry.trigger==1275);}
void event(long ms,double p){gLatest=tick(ms,p);gNow=ms/1000;gHistory.push_back(gLatest);}
int main(int argc,char**argv){try{
 string name=argc>1?argv[1]:"";
 if(name=="transient_opportunity_before_timer"){
  arm();event(32460250,1280);OnTick();require(sends==1&&sentAtMsc==32460250);
  event(32460750,1100);OnTick();require(sends==1);
  std::cout<<"synthetic_api_attempt_delay_ms=0; first_timer_delay_ms=750; actual_fill=UNTESTED\n";
 }else if(name=="legacy_timer_misses_same_transient"){
  arm();event(32460250,1280);OnTickLegacy();require(sends==0);
  event(32460750,1100);OnTickLegacy();gNow=32461;OnTimer();require(sends==0);
  std::cout<<"legacy_synthetic_missed_opportunities=1\n";
 }else if(name=="financial_protection_precedes_bounded_live_query"){
  arm();gCallTrace.clear();event(32460250,1280);OnTick();
  auto be=std::find(gCallTrace.begin(),gCallTrace.end(),"BE");
  auto data=std::find(gCallTrace.begin(),gCallTrace.end(),"history_live");
  require(be!=gCallTrace.end()&&data!=gCallTrace.end()&&be<data);
  auto barrier=std::find(gCallTrace.begin(),gCallTrace.end(),"barrier");
  auto api=std::find(gCallTrace.begin(),gCallTrace.end(),"PositionOpen");require(barrier<api&&preparations==1&&barriers==1);
 }else if(name=="overshoot_never_becomes_late_retracement_entry"){
  arm();event(32460250,1400);OnTick();require(!armed.active&&sends==0);
  event(32460750,1280);OnTick();require(sends==0);
 }else if(name=="dense_flow_cannot_force_partial_or_retrospective_confirmation"){
  arm();for(int i=0;i<300;i++)gHistory.push_back(tick(32460250,1280));
  gLatest=gHistory.back();OnTick();require(sends==0);
  event(32460750,1100);OnTick();gNow=32461;OnTimer();require(sends==0);
 }else if(name=="uncertain_request_still_owns_recovery"){
  arm();inFlight=true;auto epoch=gOMEpoch;OMFail("FEED_COVERAGE_GAP",true);
  require(gOMEpoch>epoch);event(32460250,1280);OnTick();require(sends==0&&armed.active&&inFlight);
 }else if(name=="epoch_invalidates_only_unowned_armed_signal"){
  arm();OMFail("FEED_COVERAGE_GAP",true);event(32460250,1280);OnTick();require(!armed.active&&sends==0);
 }else if(name=="quote_changes_during_dispatch_guards"){
  arm();event(32460250,1280);gQuoteReadCount=0;
  gReplacementTick=tick(32460260,1100);gReplaceAtRead=6;
  OnTick();require(sends==0&&preparations==0&&barriers==0);
  gReplaceAtRead=0;OnTick();require(sends==0);
 }else if(name=="financial_timer_cadence_preserved"){
  fresh();gTester=true;gFinancialTimerDue=32520;gNow=32461;OnTimer();require(proofs==0);
  gNow=32520;OnTimer();require(proofs==1&&gFinancialTimerDue==32580);
 }else return 2;
 return 0;
 }catch(const std::exception&e){std::cerr<<e.what();return 1;}}
'''
class ExecutionIntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  source=(ROOT/'RemoraScalper_MatrizObjetiva.mq5').read_text();f=functions(source)
  structs='\n'.join(declaration(source,k,n)+';' for k,n in [('enum','ENTRY_PHASE'),('struct','EntryTriggerState'),('struct','ArmedSignal'),('enum','EXIT_MODE')])
  globals_='\nArmedSignal armed;EXIT_MODE Inp_ExitMode=PROGRESSIVE_NO_TP;\n'
  names=['DirStr','NormPriceDigits','RoundUpTick','RoundDownTick','EntryGridValid','EntryTimeoutExpired','InitSignalCloseTrigger','EntryRealTrade','ObserveEntryTrade','ValidateEntryDispatch','ClaimEntryDispatch','NormEntrySL','NormEntryTP','ArmedTriggerReady','ArmedTriggerPrice','ObjectiveContInsideB3','ResetArmedSignal','ObjectiveRevalidate','EntryDispatchGuard','SpreadOk','EntryTPValid','SendOrder','EvaluateMatrix','ProcessArmedSignal','ObjectiveDecisionCycle','OnTick','OnTimer']
  body='\n'.join(f[n] for n in names)
  fixture=ROOT/'tests/fixtures/OnTick_54fbc54.mql'
  assert hashlib.sha256(fixture.read_bytes()).hexdigest()=='5012a5c56575a32ad07a50acc79b012823b05d7649267425026c5b61cc038c3e'
  legacy=fixture.read_text()
  old=functions(legacy)['OnTick'].replace('void OnTick()','void OnTickLegacy()',1)
  cls.temp=tempfile.TemporaryDirectory(prefix='remora-callbacks-')
  cls.binary=compile_harness(structs+globals_+SHIMS+translate_engine(body)+old+SETUP,Path(cls.temp.name),'callbacks')
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def run_case(self,name):
  r=subprocess.run([str(self.binary),name],text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stderr)
  if r.stdout:print(r.stdout.strip())
for name in ['transient_opportunity_before_timer','legacy_timer_misses_same_transient','financial_protection_precedes_bounded_live_query','overshoot_never_becomes_late_retracement_entry','dense_flow_cannot_force_partial_or_retrospective_confirmation','uncertain_request_still_owns_recovery','epoch_invalidates_only_unowned_armed_signal','financial_timer_cadence_preserved','quote_changes_during_dispatch_guards']:
 setattr(ExecutionIntegrationTests,'test_'+name,lambda self,n=name:self.run_case(n))
