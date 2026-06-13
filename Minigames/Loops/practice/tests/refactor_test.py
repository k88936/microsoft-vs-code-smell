import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_func_def_from_module,
    collect_method_from_class_in_module,
    collect_attr_acc_from_func_def,
    has_variable_assignment_in_func_def,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


class LoopsToStreamsRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def _get_stream_method(self, method_name: str) -> ast.FunctionDef | None:
        return collect_method_from_class_in_module(self.module, "Stream", method_name)

    def test_filter_method_uses_builtin_filter(self) -> None:
        filter_method = self._get_stream_method("filter")
        self.assertIsNotNone(filter_method, "Stream.filter method not found")
        names_in_method = {
            node.id
            for node in ast.walk(filter_method)
            if isinstance(node, ast.Name)
        }
        self.assertIn("filter", names_in_method,
                      "Stream.filter must call the built-in filter() function")

    def test_compute_damage_from_sunshine_no_for_loop(self) -> None:
        """The function must not contain for-loops (they should be replaced with stream operations)."""
        func = collect_func_def_from_module(self.module).get("compute_damage_from_sunshine")
        self.assertIsNotNone(func, "compute_damage_from_sunshine not found")

        for node in ast.walk(func):
            if isinstance(node, ast.For):
                self.fail("compute_damage_from_sunshine should not contain a for loop; "
                          "use Stream API (map/filter/reduce) instead")

    def test_compute_damage_from_sunshine_no_total_variable(self) -> None:
        """The function must not assign 'total' (the accumulator from the loop version)."""
        func = collect_func_def_from_module(self.module).get("compute_damage_from_sunshine")
        self.assertIsNotNone(func, "compute_damage_from_sunshine not found")

        self.assertFalse(
            has_variable_assignment_in_func_def(func, "total"),
            "compute_damage_from_sunshine should not assign 'total'; use reduce() instead",
        )

    def test_compute_damage_from_sunshine_uses_stream_operations(self) -> None:
        """The function must use .map(), .filter() and .reduce() on a Stream."""
        func = collect_func_def_from_module(self.module).get("compute_damage_from_sunshine")
        self.assertIsNotNone(func, "compute_damage_from_sunshine not found")

        attrs = collect_attr_acc_from_func_def(func)
        for required_attr in ("map", "filter", "reduce"):
            self.assertIn(required_attr, attrs,
                          f"compute_damage_from_sunshine should call .{required_attr}()")

    def test_compute_damage_from_sunshine_uses_conversion_funcs(self) -> None:
        """The function must reference the conversion functions (passed to .map())."""
        func = collect_func_def_from_module(self.module).get("compute_damage_from_sunshine")
        self.assertIsNotNone(func, "compute_damage_from_sunshine not found")

        names_in_func = {
            node.id
            for node in ast.walk(func)
            if isinstance(node, ast.Name)
        }
        for required_name in ("sunshine_to_peanut", "peanut_to_fireball", "fireball_to_damage"):
            self.assertIn(required_name, names_in_func,
                          f"compute_damage_from_sunshine should reference {required_name}")

    def test_stream_map_method_exists(self) -> None:
        """Stream.map method must exist."""
        self.assertIsNotNone(self._get_stream_method("map"), "Stream.map method not found")

    def test_stream_reduce_method_exists(self) -> None:
        """Stream.reduce method must exist."""
        self.assertIsNotNone(self._get_stream_method("reduce"), "Stream.reduce method not found")

    def test_stream_filter_method_exists(self) -> None:
        """Stream.filter method must exist."""
        self.assertIsNotNone(self._get_stream_method("filter"), "Stream.filter method not found")
