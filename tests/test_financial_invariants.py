"""Static regression against the untouched MQL5 baseline.

These checks prove source preservation, not native compilation or MT5 behavior.
Run: python3 -m unittest discover -s tests -p 'test_financial_invariants.py' -v
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "1995"
CANDIDATE = ROOT / "RemoraScalper_MatrizObjetiva.mq5"
BASE_SHA256 = "2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5"


def lexical_mask(source):
    """Preserve offsets/newlines while masking MQL strings and comments."""
    result = list(source)
    state = "code"
    index = 0
    while index < len(source):
        character = source[index]
        pair = source[index:index + 2]
        if state == "code":
            if pair in ("//", "/*"):
                result[index:index + 2] = "  "
                state = "line" if pair == "//" else "block"
                index += 2
                continue
            if character in ("\"", "'"):
                state = character
                result[index] = " "
        elif state == "line":
            if character == "\n":
                state = "code"
            else:
                result[index] = " "
        elif state == "block":
            if pair == "*/":
                result[index:index + 2] = "  "
                state = "code"
                index += 2
                continue
            if character != "\n":
                result[index] = " "
        elif character == "\\":
            result[index] = " "
            if index + 1 < len(source) and source[index + 1] != "\n":
                result[index + 1] = " "
            index += 2
            continue
        elif character == state:
            result[index] = " "
            state = "code"
        elif character != "\n":
            result[index] = " "
        index += 1
    if state not in ("code", "line"):
        raise ValueError("Unterminated literal/comment in source")
    return "".join(result)


def block_end(mask, opening):
    depth = 1
    position = opening + 1
    while position < len(mask) and depth:
        depth += (mask[position] == "{") - (mask[position] == "}")
        position += 1
    if depth:
        raise ValueError("Unterminated source block")
    return position


def functions(source):
    mask = lexical_mask(source)
    expression = re.compile(
        r"^[ \t]*(?:void|bool|int|long|ulong|uint|double|string|datetime|ENUM_MSS|ENUM_APS)"
        r"\s+(\w+)\s*\([^;{}]*\)\s*\{", re.MULTILINE
    )
    found = {}
    for match in expression.finditer(mask):
        name = match.group(1)
        if name in found:
            raise ValueError("Duplicate function: " + name)
        start = match.start()
        while source[start].isspace():
            start += 1
        end = block_end(mask, match.end() - 1)
        found[name] = source[start:end]
    return found


def declaration(source, kind, name):
    mask = lexical_mask(source)
    match = re.search(r"\b" + kind + r"\s+" + re.escape(name) + r"\s*\{", mask)
    if not match:
        raise AssertionError("Missing declaration: " + name)
    return source[match.start():block_end(mask, match.end() - 1)]


def inputs(source):
    return {
        match.group(2): (match.group(1), re.sub(r"\s+", "", match.group(3)))
        for match in re.finditer(
            r"^input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);", source, re.MULTILINE
        )
    }


# Each exception names an authorized strategic or diagnostic seam. Every other
# original function, including all financial recovery, is protected by default.
STRATEGY_SEAMS = {
    "PocStateStr", "MacroStatusStr", "MssStr", "GetD1SessionEndHHMM", "TickIndex",
    "ComputeTrigger", "ArmedTriggerReady", "ArmedTriggerPrice", "ArmedTriggerCell",
    "EntryDispatchGuard", "ResetMacroContext", "ResetPOCResult", "ResetMatrixSnapshot",
    "ResetArmedSignal", "ResetVwapCache", "UpdateVwapIncremental", "GetLiveVwapSnapshot",
    "ComputePOCWithTieCore", "ComputePOCWithTie", "RebuildWeisCache", "ComputeLiveWaveO1",
    "CalcD1Structure", "CalcSigmaHistory", "TryCalcD1", "ComputeMacroContext",
    "ComputeMatrixSnapshot", "HasHardDirectionalContradiction", "SnapshotForSignal",
    "EvaluateMatrix", "ProcessArmedSignal", "DailyReset", "Validate1995Inputs",
    "BootstrapCachesNoTrade", "OnInit", "OnDeinit", "ObserveAccountingBlockedMatrix",
    "OnTick", "OnTimer", "CsvMacroHeader", "CsvMacroRow", "CsvMatrixHeader",
    "CsvMatrixRow", "CsvArmedHeader", "CsvArmedRow", "CsvExecutionHeader",
    "CsvExecutionRow", "WriteAuditHeader", "WriteAuditRow", "WriteShadowHeader",
    "WriteShadowRow", "EntryDiagnosticHeader", "EntryDiagnosticsInit",
    "WriteEntryDiagnostic", "CsvConfigRow", "FAREvaluate", "FARAuditSchemaCompatible",
    "ComputeLotsForEntry", "ResetPerfStat", "RecordPerf",
}

REMOVABLE_INPUTS = {
    "Inp_ABSTriggerReference", "Inp_Region_Candles", "Inp_POC_WindowSec",
    "Inp_POC_FollowRatio", "Inp_RejectPOCTies", "Inp_ABS_MaxBodyPts_WIN",
    "Inp_ABS_MaxBodyPts_WDO", "Inp_Cont_RequireCandleDirection", "Inp_VWAP_Inner_Pct",
    "Inp_VWAP_Outer_Pct", "Inp_Rule_40_60", "Inp_C2_WIN", "Inp_C3_Min_WIN",
    "Inp_C3_Max_WIN", "Inp_C2_WDO", "Inp_C3_Min_WDO", "Inp_C3_Max_WDO",
    "SigmaLookbackDays", "Inp_SigmaFloor_WIN", "Inp_SigmaFloor_WDO",
    "Inp_EnableMacroDirectionGate", "Inp_EnableLateDirectionBlock",
    "Inp_TurboLotsMultiplier", "Inp_ABS_BreakoutEffort", "Inp_CONT_BreakoutEffort",
}


class FinancialInvariants(unittest.TestCase):
    maxDiff = 600

    @classmethod
    def setUpClass(cls):
        cls.base = BASELINE.read_text(encoding="utf-8")
        cls.new = CANDIDATE.read_text(encoding="utf-8")
        cls.base_functions = functions(cls.base)
        cls.new_functions = functions(cls.new)

    def test_baseline_is_the_verified_immutable_source(self):
        self.assertEqual(hashlib.sha256(BASELINE.read_bytes()).hexdigest(), BASE_SHA256)
        self.assertEqual(len(self.base_functions), 312)

    def test_every_function_outside_named_strategy_seams_is_byte_identical(self):
        protected = set(self.base_functions) - STRATEGY_SEAMS
        self.assertGreater(len(protected), 240)
        for name in sorted(protected):
            with self.subTest(function=name):
                self.assertTrue(name in self.new_functions, "Missing protected function: " + name)
                self.assertEqual(self.base_functions[name], self.new_functions[name])

    def test_financial_structs_and_dispatch_enums_are_byte_identical(self):
        for name in (
            "BreakEvenState", "TradeRecord", "PendingExecContext", "PendingExitIntent",
            "UnresolvedOrderContext", "OpenPositionInfo", "EntryTriggerState",
        ):
            with self.subTest(struct=name):
                self.assertEqual(declaration(self.base, "struct", name), declaration(self.new, "struct", name))
        for name in ("EXIT_MODE", "SIZING_MODE", "BE_STAGE", "PendingOrderNature", "ENUM_REQUEST_DISPATCH_PHASE", "ENTRY_PHASE", "FAR_MODE"):
            with self.subTest(enum=name):
                self.assertEqual(declaration(self.base, "enum", name), declaration(self.new, "enum", name))

    def test_financial_and_preserved_strategy_inputs_keep_type_and_default(self):
        original, candidate = inputs(self.base), inputs(self.new)
        for name, value in original.items():
            if name in REMOVABLE_INPUTS:
                continue
            with self.subTest(input=name):
                self.assertTrue(name in candidate, "Missing preserved input: " + name)
                self.assertEqual(value, candidate[name])

    def test_risk_percent_sizing_is_byte_identical(self):
        marker = "double profit=0.0;"
        base = self.base_functions["ComputeLotsForEntry"]
        candidate = self.new_functions["ComputeLotsForEntry"]
        self.assertIn(marker, candidate)
        self.assertEqual(base[base.index(marker):], candidate[candidate.index(marker):])

    def test_fixed_sizing_only_removes_turbo_multiplier(self):
        base = self.base_functions["ComputeLotsForEntry"]
        expected = base.replace(
            '      bool turbo=(armed.mode=="TURBO" || armed.mode=="TURBO_CONT");\n', ""
        ).replace(
            "double lots=Inp_FixedLots*(turbo?Inp_TurboLotsMultiplier:1.0);",
            "double lots=Inp_FixedLots;",
        )
        self.assertEqual(expected, self.new_functions["ComputeLotsForEntry"])

    def test_send_order_and_trade_transaction_are_byte_identical(self):
        for name in ("SendOrder", "OnTradeTransaction", "ProcessEOD"):
            with self.subTest(function=name):
                self.assertEqual(self.base_functions[name], self.new_functions[name])

    def test_history_recognizes_all_four_original_modes_without_parser_changes(self):
        for name in ("ParseScalperComment", "RJRoute", "LoadTradeMetadata", "Identify1995EntryDeal"):
            with self.subTest(parser=name):
                self.assertEqual(self.base_functions[name], self.new_functions[name])
        # Identity validation delegates to the exact unchanged parser. Its
        # string literals include the complete comment, not a bare mode token.
        parser = self.new_functions["ParseScalperComment"]
        for comment in ("S1995|ABS|BASE", "S1995|ABS|TURBO", "S1995|CONT|BASE_CONT", "S1995|CONT|TURBO_CONT"):
            self.assertIn('"' + comment + '"', parser)
        identity = self.new_functions["Identify1995EntryDeal"]
        self.assertIn("ParseScalperComment(comment,route,mode)", identity)

    def test_FAR_only_adds_unavailable_structure_guard_and_uses_actual_trigger(self):
        original = self.base_functions["FAREvaluate"]
        guard = (
            "   if(!armed.entry.enabled || !armed.entry.triggerReady ||\n"
            "      !FARPriceValid(armed.regionHigh) || !FARPriceValid(armed.regionLow) ||\n"
            "      armed.regionHigh<armed.regionLow)\n"
            '   { gFARReason="FAR_STRUCTURE_UNAVAILABLE"; return; }\n'
        )
        expected = original.replace("   ulong span=", guard + "   ulong span=", 1).replace(
            "double trigger=ComputeTrigger(armed.dir,armed.regionHigh,armed.regionLow);",
            "double trigger=armed.entry.trigger;",
        )
        self.assertEqual(expected, self.new_functions["FAREvaluate"])

    def test_financial_csv_schema_and_append_logic_are_byte_identical(self):
        for name in ("CsvConfigHeader", "CsvTradeHeader", "CsvTradeRow", "WriteTradeHeader", "WriteTradeRow", "InitializeTradeCsvIndex"):
            with self.subTest(function=name):
                self.assertEqual(self.base_functions[name], self.new_functions[name])
        row = self.new_functions["CsvConfigRow"]
        self.assertEqual(row.count("CsvAdd("), self.base_functions["CsvConfigRow"].count("CsvAdd("))
        self.assertIn('"S1995"', row)
        self.assertIn("Symbol()", row)
        self.assertIn("IntegerToString(gMagicCore)", row)

    def test_protection_runs_before_new_data_readiness(self):
        tick = self.new_functions["OnTick"]
        required = [tick.index(name + "(") for name in ("SyncAccountingState", "UpdateMAEMFE", "ProcessEOD", "ManageBreakEven")]
        self.assertEqual(required, sorted(required))
        # Initialization of experimental data may fail without skipping the
        # financial projection and stop manager above it.
        self.assertLess(required[-1], tick.index("// OBJECTIVE_DATA_AFTER_FINANCE"))

    def test_financial_timer_keeps_original_cadence(self):
        timer = self.new_functions["OnTimer"]
        masked = lexical_mask(timer)
        start = masked.index("if(financeDue)")
        opening = masked.index("{", start)
        finance = timer[opening:block_end(masked, opening)]
        self.assertIn("now>=gFinancialTimerDue", timer)
        self.assertIn("gFinancialTimerDue=now+(MQLInfoInteger(MQL_TESTER)!=0?60:1)", finance)
        for name in ("SyncAccountingState(true)", "ReconcileBreakEvenProofs()", "ProcessEOD(hhmm)"):
            self.assertIn(name, finance)
        self.assertNotIn("ManageBreakEven(", timer)
        self.assertLess(block_end(masked, opening), timer.index("OMService()"))
        self.assertIn(
            "gFinancialTimerDue=TimeTradeServer()+(MQLInfoInteger(MQL_TESTER)!=0?60:1)",
            self.new_functions["OnInit"],
        )

    def test_native_terminal_validation_is_not_falsely_claimed(self):
        self.assertIn("COMPILACAO_NATIVA_NAO_VERIFICADA", (ROOT / "REGRESSION_FINANCE.md").read_text())

    def test_actual_protection_kernel_at_exact_and_fractional_R_boundaries(self):
        """Execute the actual MQL numeric bodies with explicit C++ API shims.

        This is a portable numeric harness, not MetaEditor compilation. It
        exercises triggers/rounding without simulating a broker or journal.
        """
        compiler = shutil.which("g++")
        if compiler is None:
            self.skipTest("g++ unavailable; portable financial kernel not executed")
        prefix = r'''
#include <cassert>
#include <cmath>
#include <limits>
#include <string>
using string=std::string;
double gTickSize=5.0;
const int SYMBOL_DIGITS=0;
string Symbol() { return "HARNESS"; }
long SymbolInfoInteger(string,int) { return 8; }
bool MathIsValidNumber(double n) { return std::isfinite(n); }
double MathAbs(double n) { return std::abs(n); }
double MathRound(double n) { return std::round(n); }
double MathFloor(double n) { return std::floor(n); }
double MathCeil(double n) { return std::ceil(n); }
double NormalizeDouble(double n,int d) {
 const double scale=std::pow(10.0,d); return std::round(n*scale)/scale;
}
'''
        body = "\n".join(self.new_functions[name] for name in (
            "NormPriceDigits", "Positive", "BEPrice", "ProtectionPrice", "ProtectionEligibleLevel"
        ))
        checks = r'''
int main() {
 assert(ProtectionEligibleLevel(1,100,90,109.999999,5,true)==-1);
 assert(ProtectionEligibleLevel(1,100,90,110,5,true)==0);
 assert(ProtectionEligibleLevel(1,100,90,120,5,true)==1);
 assert(ProtectionEligibleLevel(1,100,90,160,5,true)==5);
 assert(ProtectionEligibleLevel(1,100,90,1000,5,true)==5);
 assert(ProtectionEligibleLevel(-1,100,110,90.000001,5,true)==-1);
 assert(ProtectionEligibleLevel(-1,100,110,90,5,true)==0);
 assert(ProtectionEligibleLevel(-1,100,110,80,5,true)==1);
 assert(ProtectionEligibleLevel(-1,100,110,40,5,true)==5);
 assert(ProtectionEligibleLevel(1,100,90,160,5,false)==0);
 assert(ProtectionPrice(1,100,90,5,false)==100);
 assert(ProtectionEligibleLevel(1,100,100,150,5,true)==-1);
 assert(ProtectionEligibleLevel(0,100,90,150,5,true)==-1);
 assert(ProtectionEligibleLevel(1,100,90,std::numeric_limits<double>::quiet_NaN(),5,true)==-1);
 assert(ProtectionEligibleLevel(1,100.25,90,110.499999,5,true)==-1);
 assert(ProtectionEligibleLevel(1,100.25,90,110.5,5,true)==0);
 assert(ProtectionEligibleLevel(1,100.25,90,120.75,5,true)==1);
 assert(ProtectionPrice(1,100.25,90,1,true)==110);
 assert(ProtectionPrice(-1,100.25,110,1,true)==95);
 gTickSize=0.5;
 assert(ProtectionPrice(1,100.25,90,1,true)==110.5);
 assert(ProtectionPrice(-1,100.25,110,1,true)==90.5);
}
'''
        with tempfile.TemporaryDirectory(prefix="remora-financial-kernel-") as temp:
            source = Path(temp) / "kernel.cpp"
            binary = Path(temp) / "kernel"
            source.write_text(prefix + body + checks)
            result = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            execution = subprocess.run([str(binary)], capture_output=True, text=True, check=False)
            self.assertEqual(execution.returncode, 0, execution.stderr)

    def test_actual_dispatch_and_armed_functions_preserve_terminal_overshoot(self):
        """Execute actual guard/armed bodies; isolate MT5 effects with named stubs."""
        compiler = shutil.which("g++")
        if compiler is None:
            self.skipTest("g++ unavailable; portable dispatch harness not executed")
        prefix = r'''
#include <cassert>
#include <cmath>
#include <string>
#include <algorithm>
using string=std::string;
using datetime=long long;
struct MqlTick { long time=2,time_msc=2000; double ask=1005,bid=1000,last=1000;
 unsigned flags=1; unsigned long volume=1; double volume_real=0; };
struct OMBands { bool ready=true; double upper3=1200,lower3=800; };
struct MqlDateTime { int hour=9,min=30; };
double gTickSize=5,gSpreadMaxPts=30,gMaxOvershoot=100,gLastBreakoutPrice=0,gOMLastPrice=1000;
int Inp_ArmedTimeoutSec=300,Inp_StopEntryHHMM=1530,Inp_MaxTradesDay=10,ordersEnteredToday=0;
const unsigned TICK_FLAG_LAST=1,TICK_FLAG_VOLUME=2,TICK_FLAG_BUY=4,TICK_FLAG_SELL=8;
bool gAccountingUnresolved=false,dailyRiskBlocked=false,inFlight=false,position=false,dataReady=true,thesisValid=true;
datetime nowValue=2;
int resets=0,sends=0,farCalls=0;
string lastReason;
MqlTick quote;
bool MathIsValidNumber(double n) { return std::isfinite(n); }
double MathAbs(double n) { return std::abs(n); }
double MathRound(double n) { return std::round(n); }
double MathMax(double a,double b) { return std::max(a,b); }
string Symbol() { return "HARNESS"; }
datetime TimeTradeServer() { return nowValue; }
void TimeToStruct(datetime,MqlDateTime &d) { d.hour=9;d.min=30; }
bool SymbolInfoTick(string,MqlTick &t) { t=quote; return true; }
bool HasExecutionInFlight() { return inFlight; }
bool HasOpenPosition() { return position; }
bool OMLiveReady(long) { return dataReady; }
bool ObjectiveRevalidate(string &reason) { reason="STUB_THESIS";return thesisValid; }
bool FARBeforeDecision() { ++farCalls;return false; }
bool SpreadOk() { return quote.ask-quote.bid<=gSpreadMaxPts; }
'''
        structs = "\n".join((
            declaration(self.new, "enum", "ENTRY_PHASE") + ";",
            declaration(self.new, "struct", "EntryTriggerState") + ";",
        ))
        shims = r'''
struct Armed { bool active=true; int dir=1; EntryTriggerState entry{};
 string route="ABS",mode="BASE",entryReason; datetime armedAt=1;
 double lots=1,activeSL_Pts=400,activeTP_Pts=2000,posRel=0,distD1=0,effort=2; } armed;
struct Objective { OMBands bands; } gObjectiveArmed;
void ResetArmedSignal() { ++resets;armed.active=false; }
void WriteAuditRow(string reason,string,string,double,double,double,double,double) { lastReason=reason; }
void WriteEntryDiagnostic(const Armed&,string) {}
bool SendOrder(int,double,string,double,double,double,double,double,double) {
 ++sends;armed.entry.dispatchAttempted=true;return true;
}
'''
        body = "\n".join(self.new_functions[name] for name in (
            "DirStr", "EntryGridValid", "EntryTimeoutExpired", "EntryRealTrade",
            "ObserveEntryTrade", "ValidateEntryDispatch", "ArmedTriggerReady",
            "ArmedTriggerPrice", "ObjectiveContInsideB3", "EntryDispatchGuard",
            "ProcessArmedSignal",
        ))
        checks = r'''
void fresh() {
 armed=Armed{}; armed.entry.enabled=true;armed.entry.triggerReady=true;
 armed.entry.dir=1;armed.entry.trigger=1000;armed.entry.thesisMsc=1000;
 armed.entry.phase=ENTRY_WAIT_CONFIRMATION;
 quote=MqlTick{};gOMLastPrice=quote.last;inFlight=position=gAccountingUnresolved=false;
 dataReady=thesisValid=true;nowValue=2;resets=sends=farCalls=0;lastReason="";
 gObjectiveArmed.bands=OMBands{};
}
void overshoot() { quote.last=1105;quote.ask=1110;quote.bid=1000; }
int main() {
 fresh();assert(EntryDispatchGuard(quote));assert(resets==0);
 fresh();quote.last=1100;quote.ask=1100;quote.bid=1095;gOMLastPrice=quote.last;
 assert(EntryDispatchGuard(quote));assert(resets==0);
 fresh();overshoot();dataReady=false;thesisValid=false;
 assert(!EntryDispatchGuard(quote));assert(resets==1);assert(lastReason=="OVERSHOOT_BLOCK");
 fresh();overshoot();inFlight=true;
 assert(!EntryDispatchGuard(quote));assert(resets==0);assert(armed.active);
 fresh();overshoot();position=true;
 assert(!EntryDispatchGuard(quote));assert(resets==0);assert(armed.active);
 fresh();overshoot();gAccountingUnresolved=true;
 assert(!EntryDispatchGuard(quote));assert(resets==0);assert(armed.active);
 fresh();overshoot();quote.flags=0;gOMLastPrice=quote.last;
 assert(!EntryDispatchGuard(quote));assert(resets==0);assert(lastReason=="HOLD_SPREAD");
 fresh();gOMLastPrice=995;
 assert(!EntryDispatchGuard(quote));assert(resets==0);assert(armed.active);
 fresh();armed.route="CONT";gObjectiveArmed.bands.upper3=1005;
 assert(!EntryDispatchGuard(quote));assert(resets==1);assert(lastReason=="CONT_EXEC_OUTSIDE_B3");
 fresh();nowValue=301;
 assert(!EntryDispatchGuard(quote));assert(resets==1);assert(lastReason=="TIMEOUT_ARMED");
 fresh();overshoot();dataReady=false;thesisValid=false;
 ProcessArmedSignal();assert(resets==1);assert(sends==0);assert(farCalls==0);
 assert(lastReason=="OVERSHOOT_BLOCK");
 fresh();overshoot();inFlight=true;
 ProcessArmedSignal();assert(resets==0);assert(sends==0);assert(armed.active);
 fresh();ProcessArmedSignal();assert(sends==1);assert(resets==1);
}
'''
        with tempfile.TemporaryDirectory(prefix="remora-dispatch-guard-") as temp:
            source = Path(temp) / "guard.cpp"
            binary = Path(temp) / "guard"
            source.write_text(prefix + structs + shims + body + checks)
            compilation = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(compilation.returncode, 0, compilation.stderr)
            execution = subprocess.run([str(binary)], capture_output=True, text=True, check=False)
            self.assertEqual(execution.returncode, 0, execution.stderr)


if __name__ == "__main__":
    unittest.main()
