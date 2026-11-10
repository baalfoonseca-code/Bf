"""Execute the actual entry kernel as C++; this is not a native MQL5 build.

The EA's functions are extracted unchanged. The harness supplies only terminal
types and elementary math/string operations, so a Python replica cannot hide
an incorrect trigger, timestamp or dispatch predicate in the delivered source.
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "RemoraScalper_MatrizObjetiva.mq5"


def function_source(text: str, name: str) -> str:
    """Read one complete global function, ignoring braces in comments/literals."""
    match = re.search(r"^\s*(?:bool|int|double|void)\s+" + re.escape(name)
                      + r"\s*\([^;{}]*\)\s*\{", text, re.M)
    if not match:
        raise AssertionError(f"Required delivered function missing: {name}")
    start = text.index("{", match.start())
    state, depth, pos = "code", 0, start
    while pos < len(text):
        char, two = text[pos], text[pos:pos + 2]
        if state == "code":
            if two in ("//", "/*"):
                state = "line" if two == "//" else "block"
                pos += 2
                continue
            if char in ("\"", "'"):
                state = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[match.start():pos + 1]
        elif state == "line":
            if char == "\n":
                state = "code"
        elif state == "block":
            if two == "*/":
                state = "code"
                pos += 2
                continue
        elif char == "\\":
            pos += 2
            continue
        elif char == state:
            state = "code"
        pos += 1
    raise AssertionError(f"Unterminated delivered function: {name}")


SCENARIOS = {
    "win_trigger_margin": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        require(e.signalReferencePrice==100000 && e.trigger==100175);
        require(InitSignalCloseTrigger(e,-1,100000,175,1000000,reason));
        require(e.trigger==99825);
    """,
    "wdo_trigger_margin": r"""
        gTickSize=.5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,5000,3.5,1000000,reason));
        require(e.trigger==5003.5);
        require(InitSignalCloseTrigger(e,-1,5000,3.5,1000000,reason));
        require(e.trigger==4996.5);
    """,
    "invalid_reference_no_fallback": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(!InitSignalCloseTrigger(e,1,100001,175,1000000,reason));
        require(!e.enabled && !e.triggerReady);
        require(!InitSignalCloseTrigger(e,1,NAN,175,1000000,reason));
        require(!InitSignalCloseTrigger(e,0,100000,175,1000000,reason));
        require(!InitSignalCloseTrigger(e,1,100000,0,1000000,reason));
    """,
    "trade_must_follow_thesis": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        auto tk=tick(1000000,100175,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==0);
        require(!ValidateEntryDispatch(e,tk,reason));
        tk=tick(1000001,100175,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==1);
        require(ValidateEntryDispatch(e,tk,reason));
    """,
    "same_ms_is_not_second_confirmation": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        auto tk=tick(1000001,100170,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==0);
        tk.last=100175;
        require(ObserveEntryTrade(e,tk,reason)==0);
        require(!ValidateEntryDispatch(e,tk,reason));
        tk=tick(1000002,100175,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==1);
    """,
    "new_trade_loses_trigger": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        auto tk=tick(1000001,100175,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==1);
        tk=tick(1000002,100170,100175,100170);
        require(!ValidateEntryDispatch(e,tk,reason));
        require(e.phase==ENTRY_WAIT_CONFIRMATION && e.confirmationMsc==0);
        require(e.signalReferencePrice==100000 && e.trigger==100175);
    """,
    "quote_cannot_invent_last_confirmation": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        auto tk=tick(1000001,100175,100175,100170); tk.flags=0;
        require(ObserveEntryTrade(e,tk,reason)==0);
        require(!ValidateEntryDispatch(e,tk,reason));
        tk.flags=TICK_FLAG_LAST; require(ObserveEntryTrade(e,tk,reason)==1);
        tk=tick(1000002,100175,100175,100170); tk.flags=0;
        require(ValidateEntryDispatch(e,tk,reason));
        tk.last=100180; require(!ValidateEntryDispatch(e,tk,reason));
    """,
    "invalid_quotes_and_clock": r"""
        gTickSize=.5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,-1,5000,3.5,1000000,reason));
        auto tk=tick(1000001,4996.5,4997,4996.5);
        require(ObserveEntryTrade(e,tk,reason)==1);
        require(ValidateEntryDispatch(e,tk,reason));
        tk.bid=4997.5; require(!ValidateEntryDispatch(e,tk,reason));
        tk.bid=4996.5; tk.time=0; require(!ValidateEntryDispatch(e,tk,reason));
        tk.time=1000; tk.ask=NAN; require(!ValidateEntryDispatch(e,tk,reason));
    """,
    "one_dispatch_claim": r"""
        gTickSize=5; EntryTriggerState e; string reason;
        require(InitSignalCloseTrigger(e,1,100000,175,1000000,reason));
        require(!ClaimEntryDispatch(e));
        auto tk=tick(1000001,100175,100175,100170);
        require(ObserveEntryTrade(e,tk,reason)==1);
        require(ClaimEntryDispatch(e)); require(!ClaimEntryDispatch(e));
        require(!ValidateEntryDispatch(e,tk,reason));
        tk.time_msc++; require(ObserveEntryTrade(e,tk,reason)==0);
    """,
    "timeout_exact_boundary": r"""
        require(!EntryTimeoutExpired(1000,1299,300));
        require(EntryTimeoutExpired(1000,1300,300));
        require(EntryTimeoutExpired(1000,1301,300));
        require(!EntryTimeoutExpired(1000,999,300));
        require(!EntryTimeoutExpired(0,1300,300));
    """,
    "b3_strict_frozen_boundary": r"""
        OMBands b{}; b.ready=true; b.upper3=100300; b.lower3=99700;
        require(ObjectiveContInsideB3(1,100295,b));
        require(!ObjectiveContInsideB3(1,100300,b));
        require(!ObjectiveContInsideB3(1,100305,b));
        require(ObjectiveContInsideB3(-1,99705,b));
        require(!ObjectiveContInsideB3(-1,99700,b));
        require(!ObjectiveContInsideB3(-1,99695,b));
        require(!ObjectiveContInsideB3(1,NAN,b));
        require(!ObjectiveContInsideB3(0,100000,b));
        b.ready=false; require(!ObjectiveContInsideB3(1,100295,b));
    """,
}


class EntryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("g++"):
            raise unittest.SkipTest("g++ unavailable; native MQL5 also not tested here")
        text = CANDIDATE.read_text(encoding="utf-8")
        types = text.split("// ENTRY_TYPES_BEGIN", 1)[1].split("// ENTRY_TYPES_END", 1)[0]
        names = ["RoundUpTick", "RoundDownTick", "EntryGridValid",
                 "EntryTimeoutExpired", "InitSignalCloseTrigger", "EntryRealTrade",
                 "ObserveEntryTrade", "ValidateEntryDispatch", "ClaimEntryDispatch",
                 "ObjectiveContInsideB3"]
        functions = "\n".join(function_source(text, name) for name in names)
        prelude = r"""
#include <cmath>
#include <string>
#include <iostream>
#include <stdexcept>
using string=std::string;
using datetime=long long;
using uint=unsigned int;
double gTickSize=5;
double MathAbs(double n){return std::abs(n);}
double MathRound(double n){return std::round(n);}
double MathCeil(double n){return std::ceil(n);}
double MathFloor(double n){return std::floor(n);}
bool MathIsValidNumber(double n){return std::isfinite(n);}
double NormPriceDigits(double n){return n;}
template<class T> void ZeroMemory(T &value){value=T{};}
constexpr uint TICK_FLAG_LAST=8,TICK_FLAG_VOLUME=16,TICK_FLAG_BUY=32,TICK_FLAG_SELL=64;
struct MqlTick {datetime time; long time_msc; double last,ask,bid,volume_real; unsigned long volume; uint flags;};
struct OMBands {bool ready; long asofMsc; double vwap,sigma,weight,width,upper1,upper2,upper3,lower1,lower2,lower3; long trades;};
void require(bool value){if(!value) throw std::runtime_error("assertion failed");}
MqlTick tick(long t,double last,double ask,double bid){
 return MqlTick{t/1000,t,last,ask,bid,1.0,1,TICK_FLAG_LAST|TICK_FLAG_VOLUME};
}
"""
        cases = "\n".join(f'if(name=="{name}"){{{body}\nreturn 0;}}'
                          for name, body in SCENARIOS.items())
        cls.temp = tempfile.TemporaryDirectory(prefix="remora-entry-")
        cls.binary = Path(cls.temp.name) / "entry_contract"
        source = Path(cls.temp.name) / "entry_contract.cpp"
        source.write_text(prelude + types + functions + '\nint main(int argc,char**argv){'
                          'try{string name=argc>1?argv[1]:"";' + cases
                          + 'return 2;}catch(const std::exception&e){std::cerr<<e.what();return 1;}}')
        compile_result = subprocess.run(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra",
                                         str(source), "-o", str(cls.binary)],
                                        text=True, capture_output=True)
        if compile_result.returncode:
            cls.temp.cleanup()
            raise AssertionError("Extracted entry kernel did not compile:\n" + compile_result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_scenario(self, name):
        result = subprocess.run([str(self.binary), name], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


def _scenario_test(name):
    def test(self):
        self.run_scenario(name)
    return test


for _name in SCENARIOS:
    setattr(EntryContractTest, "test_" + _name, _scenario_test(_name))


if __name__ == "__main__":
    unittest.main()
