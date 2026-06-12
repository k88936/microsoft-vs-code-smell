import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_func_def_from_module,
    collect_func_calls_from_func_def,
    collect_str_constants_from_func_def,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "thu_info_cli.py"


class ThuInfoCliRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")

    def _assert_no_forbidden_strings(self, func_name: str) -> None:
        module = ast.parse(self.source_text)
        funcs = collect_func_def_from_module(module)
        func = funcs.get(func_name)
        self.assertIsNotNone(func, f"function '{func_name}' not found")
        for s in collect_str_constants_from_func_def(func):
            self.assertNotIn("宿舍", s, f"'{func_name}' contains hardcoded '宿舍'")
            self.assertNotIn("游泳", s, f"'{func_name}' contains hardcoded '游泳'")

    def _assert_calls_t(self, func_name: str) -> None:
        module = ast.parse(self.source_text)
        funcs = collect_func_def_from_module(module)
        func = funcs.get(func_name)
        self.assertIsNotNone(func, f"function '{func_name}' not found")
        calls = collect_func_calls_from_func_def(func)
        self.assertIn("t", calls, f"'{func_name}' does not call t()")

    def test_get_dorm_info_no_hardcoded_chinese(self) -> None:
        self._assert_no_forbidden_strings("get_dorm_info")

    def test_get_dorm_info_calls_t(self) -> None:
        self._assert_calls_t("get_dorm_info")

    def test_get_sports_info_no_hardcoded_chinese(self) -> None:
        self._assert_no_forbidden_strings("get_sports_info")

    def test_get_sports_info_calls_t(self) -> None:
        self._assert_calls_t("get_sports_info")
