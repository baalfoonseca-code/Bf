"""Packaging equivalence of the actual modular and copy/paste MQL5 deliveries.

These are byte/text/structure checks, not native MQL5 compilation or broker
simulation. No financial or strategic function is rewritten by the builder.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

from test_financial_invariants import functions, inputs, lexical_mask


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("remora_delivery_builder", ROOT / "tools/build_consolidated.py")
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def ordered_inputs(source: str) -> list[tuple[str, str, str]]:
    # Type, identifier and literal expression are checked in declaration order.
    return [
        (match.group(1), match.group(2), re.sub(r"\s+", "", match.group(3)))
        for match in re.finditer(r"^input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);", source, re.M)
    ]


class ConsolidatedDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (ROOT / BUILDER.MAIN_NAME).read_bytes().decode("utf-8")
        cls.module = (ROOT / "include/ObjectiveMatrix.mqh").read_bytes().decode("utf-8")
        cls.complete = (ROOT / BUILDER.OUTPUT_NAME).read_bytes().decode("utf-8")

    def test_file_is_exact_current_generated_delivery(self):
        self.assertTrue(self.complete == BUILDER.render(), "Consolidated file is not the current exact expansion")

    def test_independent_literal_expansion_matches_generated_body(self):
        # Independently replace the actual include statement; do not trust the
        # builder's traversal as the sole proof of its own correctness.
        statement = '#include "include/ObjectiveMatrix.mqh"'
        self.assertEqual(self.main.count(statement), 1)
        expected = self.main.replace(statement, self.module.rstrip("\n"), 1)
        actual = self.complete.split("// GENERATED_BODY_BEGIN\n", 1)[1]
        actual = re.sub(r"^// (?:BEGIN|END) EXACT PROJECT INCLUDE: [^\n]+\n", "", actual, flags=re.M)
        self.assertTrue(actual == expected, "Expanded body differs from the complete native inputs")

    def test_every_actual_function_body_is_identical(self):
        original = functions(self.main + "\n" + self.module)
        consolidated = functions(self.complete)
        self.assertEqual(set(original), set(consolidated))
        for name in sorted(original):
            with self.subTest(function=name):
                self.assertTrue(original[name] == consolidated[name], "Function changed during packaging: " + name)

    def test_input_order_types_and_defaults_are_identical(self):
        expanded, _ = BUILDER.expand_sources()
        original = ordered_inputs(expanded)
        actual = ordered_inputs(self.complete)
        self.assertEqual(len(original), 65)
        self.assertEqual(len({name for _, name, _ in original}), 65)
        self.assertEqual(original, actual)
        self.assertEqual(inputs(expanded), inputs(self.complete))

    def test_only_the_two_original_standard_includes_remain(self):
        includes = re.findall(r"^\s*#include\s+([^\r\n]+)", self.complete, re.M)
        self.assertEqual(includes, ["<Trade\\Trade.mqh>", "<Trade\\PositionInfo.mqh>"])
        self.assertFalse(re.search(r"^\s*#import\b", self.complete, re.M))
        _, inventory = BUILDER.expand_sources()
        self.assertEqual([name for name, _ in inventory], [BUILDER.MAIN_NAME, "include/ObjectiveMatrix.mqh"])

    def test_module_is_included_once_and_generated_file_is_not_a_second_strategy(self):
        self.assertEqual(self.complete.count("// OM_KERNEL_BEGIN"), 1)
        self.assertEqual(self.complete.count("// OM_KERNEL_END"), 1)
        self.assertEqual(self.complete.count("#ifndef REMORA_OBJECTIVE_MATRIX_MQH"), 1)
        actual = functions(self.complete)  # The parser rejects duplicate function names.
        for name in ("OnInit", "OnTick", "OnTimer", "OnTradeTransaction", "OMService", "OMRevalidate"):
            self.assertIn(name, actual)
        self.assertEqual(self.complete.count('#property version "1.996"'), 1)

    def test_builder_is_deterministic_and_does_not_modify_native_inputs(self):
        paths = [ROOT / BUILDER.MAIN_NAME, ROOT / "include/ObjectiveMatrix.mqh", ROOT / "1995"]
        before = {path: path.read_bytes() for path in paths}
        first, second = BUILDER.render(), BUILDER.render()
        self.assertTrue(first == second)
        for path in paths:
            self.assertEqual(before[path], path.read_bytes())

    def test_missing_local_dependency_fails_instead_of_omitting_code(self):
        with tempfile.TemporaryDirectory(prefix="remora-delivery-missing-") as name:
            root = Path(name)
            (root / BUILDER.MAIN_NAME).write_text('#include "missing.mqh"\n')
            with self.assertRaises(FileNotFoundError):
                BUILDER.render(root)

    def test_include_escape_and_duplicate_include_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="remora-delivery-invalid-") as name:
            root = Path(name)
            main = root / BUILDER.MAIN_NAME
            main.write_text('#include "../unowned.mqh"\n')
            with self.assertRaises(ValueError):
                BUILDER.render(root)
            (root / "module.mqh").write_text("double example=1;\n")
            main.write_text('#include "module.mqh"\n#include "module.mqh"\n')
            with self.assertRaises(ValueError):
                BUILDER.render(root)

    def test_history_consolidated_and_original_are_not_builder_targets(self):
        self.assertEqual(BUILDER.OUTPUT_NAME, "RemoraScalper_1996_Completo.mq5")
        self.assertNotEqual(BUILDER.OUTPUT_NAME, "RemoraScalper_1996_CONSOLIDADO.mq5")
        self.assertNotEqual(BUILDER.OUTPUT_NAME, "1995")


if __name__ == "__main__":
    unittest.main()
