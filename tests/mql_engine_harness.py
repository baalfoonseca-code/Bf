"""Portable harness for the exact MQL engine, with deterministic terminal stubs.

Only surface syntax (dynamic arrays, input declaration and numeric-to-string
casts) is translated. The collector, classification and arithmetic bodies are
retained. This provides simulated-service evidence, never native MT5 evidence.
"""
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "include" / "ObjectiveMatrix.mqh"

PRELUDE = r"""
#include <algorithm>
#include <cfloat>
#include <cmath>
#include <cstring>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using string=std::string;
using ulong=unsigned long;
using uint=unsigned int;
using datetime=long;
using ENUM_DAY_OF_WEEK=int;
constexpr double EMPTY_VALUE=DBL_MAX;
constexpr int INVALID_HANDLE=-1;
constexpr int FILE_WRITE=1,FILE_READ=2,FILE_TXT=4,FILE_ANSI=8,FILE_SHARE_READ=16;
constexpr int TERMINAL_CONNECTED=1,MQL_TESTER=2,SERIES_SYNCHRONIZED=3,COPY_TICKS_TRADE=4;
constexpr uint TICK_FLAG_LAST=8,TICK_FLAG_VOLUME=16,TICK_FLAG_BUY=32,TICK_FLAG_SELL=64;
bool MathIsValidNumber(double x){return std::isfinite(x);}
double MathAbs(double x){return std::abs(x);}
double MathSqrt(double x){return std::sqrt(x);}
double MathRound(double x){return std::round(x);}
double MathFloor(double x){return std::floor(x);}
double MathCeil(double x){return std::ceil(x);}
template<class A,class B> double MathMax(A a,B b){return std::max(double(a),double(b));}
template<class A,class B> double MathMin(A a,B b){return std::min(double(a),double(b));}
template<class T> void ZeroMemory(T &x){x=T{};}
template<class T> int ArrayResize(std::vector<T>&v,int n){
    if(n<0){return -1;}
    try{v.resize(size_t(n));return n;}catch(...){return -1;}
}
template<class T> int ArraySize(const std::vector<T>&v){return int(v.size());}
template<class T,size_t N> int ArraySize(const T(&)[N]){return int(N);}
template<class T,class V,size_t N> void ArrayInitialize(T(&a)[N],V value){std::fill(a,a+N,T(value));}
template<class T,class V> void ArrayInitialize(std::vector<T>&a,V value){std::fill(a.begin(),a.end(),T(value));}
template<class T> void ArraySort(std::vector<T>&a){std::sort(a.begin(),a.end());}
template<class T> string mqlstr(T value){return std::to_string(value);}
string mqlstr(const string&value){return value;}
string DoubleToString(double value,int precision){std::ostringstream s;s<<std::fixed<<std::setprecision(precision)<<value;return s.str();}

struct MqlTick {datetime time=0;double bid=0,ask=0,last=0;ulong volume=0;long time_msc=0;uint flags=0;double volume_real=0;};
struct MqlDateTime {int year=0,mon=0,day=0,hour=0,min=0,sec=0,day_of_week=0,day_of_year=0;};
struct MqlRates {datetime time=0;long real_volume=0;double high=0,low=0;};
std::vector<MqlTick> gHistory;
int gCopyCalls=0,gRangeCalls=0,gMaxCountRequest=0;
bool gRatesUnavailable=false;
long gExpectedBarVolume=-1;
std::vector<string> gCallTrace;
MqlTick gLatest,gReplacementTick;
int gQuoteReadCount=0,gReplaceAtRead=0;
datetime gNow=32401;
int gCopyError=0,gLastError=0;
bool gConnected=true,gTester=false,gSymbolSynchronized=true,gSeriesSynchronized=true;
int gSessionCount=1;
datetime gSessionStartSec=9*3600,gSessionEndSec=17*3600;
std::vector<string> gWritten;
bool gIsIndexFamily=true;
double gTickSize=1,gBandMultiplier=.8,gABS_MinDisplPts=2,gCONT_MinDisplPts=4;
double Inp_ABS_Effort=1.5,Inp_CONT_Effort=1.5;
bool Inp_EnableAbsorption=true,Inp_EnableContinuation=true;
int Inp_ContextTF=300,Inp_SignalTF=60;
string Symbol(){return "WIN_TEST";}
bool SymbolInfoTick(const string&,MqlTick&t){
 ++gQuoteReadCount;
 if(gReplaceAtRead>0 && gQuoteReadCount==gReplaceAtRead){gLatest=gReplacementTick;gHistory.push_back(gLatest);}
 t=gLatest;return t.time_msc>0;
}
datetime TimeTradeServer(){return gNow;}
datetime TimeLocal(){return gNow;}
void TimeToStruct(datetime value,MqlDateTime&d){
    std::time_t t=value;std::tm*x=std::gmtime(&t);
    if(!x){d=MqlDateTime{};return;}
    d.year=x->tm_year+1900;d.mon=x->tm_mon+1;d.day=x->tm_mday;
    d.hour=x->tm_hour;d.min=x->tm_min;d.sec=x->tm_sec;
    d.day_of_week=x->tm_wday;d.day_of_year=x->tm_yday;
}
datetime StructToTime(const MqlDateTime&d){
    std::tm t{};t.tm_year=d.year-1900;t.tm_mon=d.mon-1;t.tm_mday=d.day;
    t.tm_hour=d.hour;t.tm_min=d.min;t.tm_sec=d.sec;return long(timegm(&t));
}
long TerminalInfoInteger(int){return gConnected?1:0;}
long MQLInfoInteger(int){return gTester?1:0;}
bool SymbolIsSynchronized(const string&){return gSymbolSynchronized;}
long SeriesInfoInteger(const string&,int,int){return gSeriesSynchronized?1:0;}
int PeriodSeconds(int tf){return tf;}
bool SymbolInfoSessionTrade(const string&,ENUM_DAY_OF_WEEK,uint index,datetime&from,datetime&to){
    if(int(index)>=gSessionCount){return false;}
    from=gSessionStartSec;to=gSessionEndSec;return true;
}
void ResetLastError(){gLastError=0;}
int GetLastError(){return gLastError;}
int CopyTicksRange(const string&,std::vector<MqlTick>&out,int,ulong from,ulong to){
    ++gRangeCalls;gCallTrace.push_back("history_range");out.clear();if(gCopyError){gLastError=gCopyError;return -1;}
    if(from>to){gLastError=1;return -1;}
    for(const auto&t:gHistory)if(ulong(t.time_msc)>=from&&ulong(t.time_msc)<=to)out.push_back(t);
    return int(out.size());
}
int CopyTicks(const string&,std::vector<MqlTick>&out,int,ulong from,uint maximum){
    ++gCopyCalls;gCallTrace.push_back("history_live");
    gMaxCountRequest=std::max(gMaxCountRequest,int(maximum));out.clear();
    if(gCopyError){gLastError=gCopyError;return -1;}
    for(const auto&t:gHistory)if(ulong(t.time_msc)>=from){
        if(out.size()>=maximum)break;out.push_back(t);
    }
    return int(out.size());
}
int CopyRates(const string&,int,datetime from,datetime to,std::vector<MqlRates>&out){
    out.clear();if(gRatesUnavailable){gLastError=1;return -1;}
    double total=0;bool any=false;
    for(const auto&t:gHistory)if(t.time>=from&&t.time<=to){
        total+=t.volume_real>0?t.volume_real:double(t.volume);any=true;
    }
    if(gExpectedBarVolume>=0){total=gExpectedBarVolume;any=total>0;}
    if(any){MqlRates r;r.time=from;r.real_volume=long(total);out.push_back(r);}
    return int(out.size());
}
ulong GetMicrosecondCount(){static ulong sequence=0;return ++sequence;}
int FileOpen(const string&,int){return 1;}
void FileFlush(int){}
void FileClose(int){}
uint FileWriteString(int,const string&row){gWritten.push_back(row);return uint(row.size());}
MqlTick make_tick(long msc,double price,double volume=1,bool real=true){
    MqlTick t;t.time=msc/1000;t.time_msc=msc;t.last=price;t.bid=price-1;t.ask=price+1;
    t.volume=ulong(volume);t.volume_real=real?volume:0;t.flags=TICK_FLAG_LAST|TICK_FLAG_VOLUME;return t;
}
void require(bool ok,const string&reason="assertion failed"){if(!ok)throw std::runtime_error(reason);}
"""


def translate_engine(source: str) -> str:
    """Translate mechanical MQL surface differences, preserving algorithms."""
    source = re.sub(r"\binput\s+", "", source)
    # MQL array reference parameters -> vector references.
    source = re.sub(r"\b(\w+)\s+&(\w+)\[\]", r"std::vector<\1> &\2", source)
    # MQL dynamic local/global declarations -> vectors; fixed arrays remain exact.
    source = re.sub(r"\b(\w+)\s+(\w+)\[\]\s*;", r"std::vector<\1> \2;", source)
    # This engine uses numeric casts only on identifiers/member names/calls.
    source = re.sub(
        r"\(string\)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\([^()]*\))?(?:\[[^\]]+\])?)",
        r"mqlstr(\1)", source,
    )
    if "(string)" in source:
        raise AssertionError("Untranslated MQL string cast; extend mechanical shim explicitly")
    # MQL resolves global functions regardless of declaration order; C++ needs
    # prototypes for the two forward calls introduced by boundary reconciliation.
    declarations = ("bool OMApplyBatch(std::vector<MqlTick> &ticks,int count,long from,long endExclusive);\n"
                    "void OMUpdateReadiness(long asof);\n"
                    "bool OMLiveReady(long tickMsc);\n")
    source = source.replace("bool OMClockHHMM(", declarations + "bool OMClockHHMM(", 1)
    return source


def compile_harness(trailer: str, directory: Path, name: str = "runtime") -> Path:
    compiler = shutil.which("g++")
    if not compiler:
        raise RuntimeError("g++ required for simulated-service source harness")
    directory.mkdir(parents=True, exist_ok=True)
    cpp = directory / (name + ".cpp")
    binary = directory / name
    cpp.write_text(PRELUDE + "\n" + translate_engine(ENGINE.read_text(encoding="utf-8"))
                   + "\n" + trailer, encoding="utf-8")
    result = subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", str(cpp),
                             "-o", str(binary)], text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise AssertionError("Simulated-service engine harness failed to compile:\n"
                             + result.stdout + result.stderr)
    return binary
