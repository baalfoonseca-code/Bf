"""Adversarial tests of the numeric kernel actually shipped in ObjectiveMatrix.mqh.

The kernel is copied verbatim between its markers and compiled with a tiny C++
shim for MQL numeric builtins. This is NOT MetaEditor compilation, MT5 replay,
broker connectivity, or empirical validation of a trading edge.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "include" / "ObjectiveMatrix.mqh"

SHIM = r"""
#include <algorithm>
#include <cfloat>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using ulong=unsigned long;
using uint=unsigned int;
constexpr double EMPTY_VALUE=DBL_MAX;
bool MathIsValidNumber(double x){return std::isfinite(x);}
double MathAbs(double x){return std::abs(x);}
double MathSqrt(double x){return std::sqrt(x);}
double MathRound(double x){return std::round(x);}
double MathFloor(double x){return std::floor(x);}
double MathCeil(double x){return std::ceil(x);}
template<class A,class B> double MathMax(A a,B b){return std::max(double(a),double(b));}
template<class A,class B> double MathMin(A a,B b){return std::min(double(a),double(b));}
template<class T> void ZeroMemory(T &x){std::memset(&x,0,sizeof(x));}
"""

CASES = r"""
#define CHECK(cond) do{if(!(cond)) throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#cond);}while(0)
void near(double actual,double expected,double tolerance=1e-10){
    if(!std::isfinite(actual)||std::abs(actual-expected)>tolerance)
        throw std::runtime_error("actual="+std::to_string(actual)+" expected="+std::to_string(expected));
}
OMConfig config(){
    OMConfig c; ZeroMemory(c);
    c.tick=1; c.reversal=4; c.eventStep=2;
    c.absEffort=1.5; c.contEffort=1.5;
    c.minCont=4; c.minAbs=2; c.contEfficiency=.60;
    c.absEfficiency=.30; c.minRejection=.35; c.minWaves=3;
    return c;
}
OMBands map(){
    OMWeighted w; OMWeightedReset(w);
    CHECK(OMWeightedAdd(w,90,1)); CHECK(OMWeightedAdd(w,110,1));
    OMBands b; CHECK(OMBuildBands(w,1,1000,b)); return b;
}
void seed(OMWaveBook &b,double volume=10){
    OMWaveReset(b); b.count=3; b.next=3;
    for(int i=0;i<3;i++) b.closedVolume[i]=volume;
}
OMDecision decision(const std::vector<double>&prices,const std::vector<double>&volumes,
                    OMConfig c,OMWaveBook *retained=nullptr){
    CHECK(prices.size()==volumes.size());
    OMWaveBook b; seed(b); OMBands bands=map();
    for(size_t i=0;i<prices.size();i++)
        CHECK(OMWavePush(b,prices[i],volumes[i],1000+long(i)*1000,c.reversal,c.eventStep,bands));
    OMDecision d; OMClassify(b,prices.back(),1000+long(prices.size())*1000,c,d);
    if(retained) *retained=b;
    return d;
}
void weighted_pair(){
    OMWeighted w; OMWeightedReset(w);
    CHECK(OMWeightedAdd(w,100,1)); CHECK(OMWeightedAdd(w,110,1));
    OMBands b; CHECK(OMBuildBands(w,.8,2000,b));
    near(b.vwap,105); near(b.sigma,5); near(b.width,4);
    near(b.upper1,109);near(b.upper2,113);near(b.upper3,117);
    near(b.lower1,101);near(b.lower2,97);near(b.lower3,93);
    CHECK(b.trades==2);near(b.weight,2);
    const double before=(110-b.vwap)/b.sigma;
    CHECK(OMWeightedAdd(w,110,98)); CHECK(OMBuildBands(w,.8,3000,b));
    near(b.vwap,109.9);near(b.sigma,std::sqrt(.99));
    CHECK((110-b.vwap)/b.sigma<before/5);
}
void weighted_reference(){
    OMWeighted w;OMWeightedReset(w);
    std::vector<long double> p,v;
    long double weight=0,sum=0;
    for(int i=0;i<8192;i++){
        long double price=125000.L+(i%137)*5.L;
        long double volume=1+(i*17)%997;
        p.push_back(price);v.push_back(volume);weight+=volume;sum+=price*volume;
        CHECK(OMWeightedAdd(w,double(price),double(volume)));
    }
    long double mean=sum/weight,variance=0;
    for(size_t i=0;i<p.size();i++)variance+=v[i]*(p[i]-mean)*(p[i]-mean);
    variance/=weight;
    OMBands b;CHECK(OMBuildBands(w,.8,100000,b));
    near(b.vwap,double(mean),1e-7);near(b.sigma,double(std::sqrt(variance)),1e-7);
    std::cout<<"mean_error_ticks="<<std::setprecision(17)<<std::abs(b.vwap-double(mean))/5
             <<" sigma_error_ticks="<<std::abs(b.sigma-double(std::sqrt(variance)))/5<<"\n";
}
void invalid_data(){
    OMWeighted w;OMWeightedReset(w);CHECK(OMWeightedAdd(w,100,1));
    auto before=w;
    CHECK(!OMWeightedAdd(w,std::numeric_limits<double>::quiet_NaN(),1));
    CHECK(!OMWeightedAdd(w,100,0));CHECK(!OMWeightedAdd(w,100,-1));
    CHECK(!OMWeightedAdd(w,100,std::numeric_limits<double>::infinity()));
    near(w.weight,before.weight);near(w.mean,before.mean);near(w.m2,before.m2);
    CHECK(w.trades==before.trades);
    OMBands b;
    CHECK(!OMBuildBands(w,0,1000,b));CHECK(!OMBuildBands(w,-1,1000,b));
}
void weighted_fragmentation(){
    OMWeighted a,b;OMWeightedReset(a);OMWeightedReset(b);
    for(int i=0;i<100;i++){
        double price=100+(i%13),vol=1+(i%7);
        CHECK(OMWeightedAdd(a,price,vol));
        for(int j=0;j<4;j++)CHECK(OMWeightedAdd(b,price,vol/4));
    }
    near(a.weight,b.weight);near(a.mean,b.mean,1e-10);near(a.m2,b.m2,1e-8);
}
void band_policy(){
    auto b=map();
    // CONT classification is independent; geographic eligibility is a second step.
    CHECK(OMLocationEligible(1,b.upper1,b));CHECK(OMLocationEligible(1,b.upper2,b));
    CHECK(!OMLocationEligible(1,b.upper2+1,b));CHECK(!OMLocationEligible(1,b.upper3,b));
    CHECK(OMLocationEligible(2,b.lower1,b));CHECK(OMLocationEligible(2,b.lower2,b));
    CHECK(!OMLocationEligible(2,b.lower2-1,b));
    CHECK(!OMLocationEligible(2,b.upper1,b));CHECK(!OMLocationEligible(1,b.lower1,b));
    for(int cls=1;cls<=4;cls++)CHECK(!OMLocationEligible(cls,b.vwap,b));
    for(double level:{b.upper1,b.upper2,b.upper3,b.upper3+10})CHECK(OMLocationEligible(4,level,b));
    for(double level:{b.lower1,b.lower2,b.lower3,b.lower3-10})CHECK(OMLocationEligible(3,level,b));
    CHECK(OMInsideB3(1,b.upper3-1,b));CHECK(!OMInsideB3(1,b.upper3,b));
    CHECK(!OMInsideB3(1,b.upper3+1,b));CHECK(OMInsideB3(-1,b.lower3+1,b));
    CHECK(!OMInsideB3(-1,b.lower3,b));CHECK(!OMInsideB3(-1,b.lower3-1,b));
    auto frozen=b; b.upper3+=100;b.lower3-=100;
    CHECK(!OMInsideB3(1,frozen.upper3,frozen));CHECK(OMInsideB3(1,frozen.upper3,b));
}
void stationary_and_monotonic(){
    OMConfig c=config();
    auto still=decision({100,100,100},{10,10,10},c);
    CHECK(still.classification==0);near(still.grossPath,0);
    auto up=decision({100,104,108},{10,10,10},c);
    CHECK(up.classification!=3 && up.classification!=4);
    CHECK(up.netProgress>0);CHECK(up.eventPath>0);
    CHECK(up.pathEfficiency>=.6 && up.pathEfficiency<=1);
    auto down=decision({108,104,100},{10,10,10},c);
    CHECK(down.classification!=3 && down.classification!=4);
    CHECK(down.netProgress>0);CHECK(down.pathEfficiency>=.6);
}
void baseline_unavailable(){
    OMConfig c=config();OMWaveBook b;OMWaveReset(b);OMBands bands=map();
    CHECK(OMWavePush(b,100,100,1000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,104,100,2000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,108,100,3000,c.reversal,c.eventStep,bands));
    OMDecision d;OMClassify(b,108,4000,c,d);CHECK(d.classification==0);
}
void noise_refutation(){
    OMConfig c=config();
    auto coarse=decision({100,104,108},{10,10,10},c);
    std::vector<double> prices{100},volumes{10};
    for(int i=0;i<20;i++){prices.push_back(101);prices.push_back(100);volumes.push_back(.01);volumes.push_back(.01);}
    prices.push_back(104);prices.push_back(108);volumes.push_back(10);volumes.push_back(10);
    auto noisy=decision(prices,volumes,c);
    const double rawCoarse=coarse.netProgress/coarse.grossPath;
    const double rawNoisy=noisy.netProgress/noisy.grossPath;
    CHECK(rawCoarse>=.60);CHECK(rawNoisy<=.30);
    near(noisy.pathEfficiency,coarse.pathEfficiency);
    near(noisy.eventPath,coarse.eventPath);
    std::cout<<"raw_coarse="<<rawCoarse<<" raw_bounce="<<rawNoisy
             <<" event_coarse="<<coarse.pathEfficiency<<" event_bounce="<<noisy.pathEfficiency<<"\n";
}
void wave_print_fragmentation(){
    OMConfig c=config(); OMWaveBook a,b;seed(a);seed(b);OMBands bands=map();
    const double prices[]={100,104,108};
    for(int i=0;i<3;i++){
        CHECK(OMWavePush(a,prices[i],10,1000+i*1000,c.reversal,c.eventStep,bands));
        for(int j=0;j<4;j++)CHECK(OMWavePush(b,prices[i],2.5,1000+i*1000,c.reversal,c.eventStep,bands));
    }
    OMDecision x,y;OMClassify(a,108,4000,c,x);OMClassify(b,108,4000,c,y);
    CHECK(x.classification==y.classification);near(x.netProgress,y.netProgress);
    near(x.grossPath,y.grossPath);near(x.eventPath,y.eventPath);near(x.effort,y.effort);
}
void no_future_reversal(){
    OMConfig c=config(); OMWaveBook b;seed(b);OMBands bands=map();
    CHECK(OMWavePush(b,100,10,1000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,104,10,2000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,108,10,3000,c.reversal,c.eventStep,bands));
    auto prefix=b;
    // A retreat smaller than the observed reversal distance cannot close a wave.
    CHECK(OMWavePush(b,107,1,4000,c.reversal,c.eventStep,bands));CHECK(b.count==prefix.count);
    CHECK(OMWavePush(b,104,1,5000,c.reversal,c.eventStep,bands));CHECK(b.count==prefix.count+1);
    OMDecision old,newer;OMClassify(prefix,108,3500,c,old);OMClassify(b,104,5500,c,newer);
    CHECK(old.evidenceMsc<=3500);CHECK(newer.evidenceMsc<=5500);
    CHECK(old.classification!=3 && old.classification!=4);
}
void absorption_needs_original_inefficiency_and_later_rejection(){
    OMConfig c=config();
    const std::vector<double> effortTest={100,104,102,104,102,104,102,105};
    const std::vector<double> volumes(effortTest.size(),10);
    auto unconfirmed=decision(effortTest,volumes,c);
    CHECK(unconfirmed.classification!=3 && unconfirmed.classification!=4);
    auto rejected=effortTest;rejected.push_back(103);
    auto rejectedVolumes=volumes;rejectedVolumes.push_back(10);
    auto confirmed=decision(rejected,rejectedVolumes,c);
    CHECK(confirmed.classification==4);
    CHECK(confirmed.rejection>0);CHECK(confirmed.pathEfficiency<=c.absEfficiency);
    auto mirror=effortTest;for(double &p:mirror)p=210-p;
    mirror.push_back(107);
    auto buy=decision(mirror,rejectedVolumes,c);CHECK(buy.classification==3);
    CHECK(buy.rejection>0);
}
void frozen_baseline(){
    OMConfig c=config();OMWaveBook b;seed(b);OMBands bands=map();
    CHECK(OMWavePush(b,100,10,1000,c.reversal,c.eventStep,bands));
    for(int i=0;i<3;i++)b.closedVolume[i]=1000000;
    CHECK(OMWavePush(b,104,10,2000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,108,10,3000,c.reversal,c.eventStep,bands));
    near(b.active.baseline,10);CHECK(b.active.baselineCount==3);
    OMDecision d;OMClassify(b,108,4000,c,d);near(d.effort,3);
}
void invalid_wave_and_past_snapshot(){
    OMConfig c=config();OMWaveBook b;seed(b);OMBands bands=map();
    CHECK(OMWavePush(b,100,10,1000,c.reversal,c.eventStep,bands));
    CHECK(OMWavePush(b,102,10,2000,c.reversal,c.eventStep,bands));
    CHECK(b.active.dir==0);CHECK(b.active.recognitionMsc==0);
    CHECK(OMWavePush(b,104,10,3000,c.reversal,c.eventStep,bands));
    CHECK(b.active.dir==1);CHECK(b.active.recognitionMsc==3000);
    auto old=b.active;
    CHECK(!OMWavePush(b,108,10,2999,c.reversal,c.eventStep,bands));
    CHECK(!OMWavePush(b,108,0,4000,c.reversal,c.eventStep,bands));
    CHECK(!OMWavePush(b,NAN,10,4000,c.reversal,c.eventStep,bands));
    near(b.active.last,old.last);near(b.active.volume,old.volume);
    CHECK(b.active.lastMsc==old.lastMsc);
    OMDecision d;OMClassify(b,104,2500,c,d);CHECK(d.classification==0);
}
void concurrent_theses_conflict(){
    OMConfig c=config();
    // Original inefficient up attempt confirms ABS_SELL, while the newly
    // recognized efficient down wave can separately satisfy CONT_SELL.
    std::vector<double> p={100,104,102,104,102,104,102,105,100,96};
    std::vector<double> v(p.size(),10);v.back()=100;
    auto d=decision(p,v,c);
    CHECK(d.classification==0);CHECK(d.reasonCode==4);
}
int main(int argc,char **argv){
    try{
        CHECK(argc==2);std::string name=argv[1];
        if(name=="weighted_pair")weighted_pair();
        else if(name=="weighted_reference")weighted_reference();
        else if(name=="invalid_data")invalid_data();
        else if(name=="weighted_fragmentation")weighted_fragmentation();
        else if(name=="band_policy")band_policy();
        else if(name=="stationary_and_monotonic")stationary_and_monotonic();
        else if(name=="baseline_unavailable")baseline_unavailable();
        else if(name=="noise_refutation")noise_refutation();
        else if(name=="wave_print_fragmentation")wave_print_fragmentation();
        else if(name=="no_future_reversal")no_future_reversal();
        else if(name=="absorption")absorption_needs_original_inefficiency_and_later_rejection();
        else if(name=="frozen_baseline")frozen_baseline();
        else if(name=="invalid_wave")invalid_wave_and_past_snapshot();
        else if(name=="conflict")concurrent_theses_conflict();
        else throw std::runtime_error("unknown case");
        std::cout<<"PASS "<<name<<"\n";return 0;
    }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
"""


class ObjectiveKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ENGINE.read_text(encoding="utf-8")
        begin, end = "// OM_KERNEL_BEGIN", "// OM_KERNEL_END"
        if source.count(begin) != 1 or source.count(end) != 1:
            raise AssertionError("Expected exactly one shipped numeric kernel")
        kernel = source.split(begin, 1)[1].split(end, 1)[0]
        if not kernel.strip():
            raise AssertionError("Empty kernel cannot validate the EA")
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("g++ is required for the common-source numeric checks")
        cls.temp = tempfile.TemporaryDirectory(prefix="remora-objective-tests-")
        cls.addClassCleanup(cls.temp.cleanup)
        cpp = Path(cls.temp.name) / "objective_kernel.cpp"
        cls.binary = Path(cls.temp.name) / "objective_kernel"
        cpp.write_text(SHIM + "\n" + kernel + "\n" + CASES, encoding="utf-8")
        result = subprocess.run(
            [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic", str(cpp), "-o", str(cls.binary)],
            text=True, capture_output=True, timeout=60,
        )
        if result.returncode:
            raise AssertionError("Common-source harness failed to compile:\n" + result.stdout + result.stderr)
        cls.kernel_sha256 = hashlib.sha256(kernel.encode()).hexdigest()

    def run_case(self, name):
        result = subprocess.run([str(self.binary), name], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS " + name, result.stdout)

    def test_weighted_pair_and_dilution(self): self.run_case("weighted_pair")
    def test_incremental_against_independent_two_pass(self): self.run_case("weighted_reference")
    def test_invalid_inputs_fail_closed(self): self.run_case("invalid_data")
    def test_vwap_invariant_to_volume_fragmentation(self): self.run_case("weighted_fragmentation")
    def test_b2_inclusive_b3_exclusive_and_frozen(self): self.run_case("band_policy")
    def test_stationary_not_abs_and_progress_without_rejection_not_abs(self): self.run_case("stationary_and_monotonic")
    def test_missing_closed_wave_baseline_does_not_invent_effort(self): self.run_case("baseline_unavailable")
    def test_raw_path_refuted_by_bounce_event_path_is_stable_for_case(self): self.run_case("noise_refutation")
    def test_wave_same_price_print_fragmentation(self): self.run_case("wave_print_fragmentation")
    def test_observed_reversal_and_prefix_causality(self): self.run_case("no_future_reversal")
    def test_absorption_can_be_confirmed_only_after_original_test_and_later_rejection(self): self.run_case("absorption")
    def test_active_wave_uses_prior_frozen_volume_baseline(self): self.run_case("frozen_baseline")
    def test_invalid_wave_records_and_past_snapshot_fail_closed(self): self.run_case("invalid_wave")
    def test_competing_abs_and_cont_theses_stay_neutral(self): self.run_case("conflict")


class ObjectiveWholeModuleSmokeTest(unittest.TestCase):
    def test_whole_module_with_simulated_terminal_compiles_and_validates_defaults(self):
        from mql_engine_harness import compile_harness
        with tempfile.TemporaryDirectory(prefix="remora-full-engine-") as temp:
            binary = compile_harness("int main(){return OMValidateInputs()?0:1;}", Path(temp))
            result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
