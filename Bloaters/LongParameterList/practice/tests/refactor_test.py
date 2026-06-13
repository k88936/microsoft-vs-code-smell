import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_class_def_from_module,
    collect_func_def_from_module,
    collect_func_calls_from_func_def,
    get_attribute_accesses,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _get_func_params(func: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in func.args.args]


def _get_func_param_annotations(func: ast.FunctionDef) -> list[tuple[str, str | None]]:
    annotations: list[tuple[str, str | None]] = []
    for arg in func.args.args:
        ann_name = arg.annotation.id if isinstance(arg.annotation, ast.Name) else None
        annotations.append((arg.arg, ann_name))
    return annotations


def _get_return_annotation(func: ast.FunctionDef) -> str | None:
    if func.returns and isinstance(func.returns, ast.Name):
        return func.returns.id
    return None


class LongParameterListRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def test_achievement_class_exists(self):
        cls_node = collect_class_def_from_module(self.module).get("Achievement")
        self.assertIsNotNone(cls_node)

    def test_print_achievement_parameters(self):
        func = collect_func_def_from_module(self.module).get("print_achievement")
        self.assertIsNotNone(func)
        params = _get_func_params(func)
        self.assertIn("user_name", params,
                      "print_achievement's should have user_name param")
        self.assertNotIn("achievement_score", params,
                         "achievement_score should be removed and replaced with a query")
        self.assertNotIn("score", params,
                         "score should be removed and replaced with a query")

    def test_print_achievement_calls_evaluate_achievement(self):
        func = collect_func_def_from_module(self.module).get("print_achievement")
        self.assertIsNotNone(func)
        calls = collect_func_calls_from_func_def(func)
        self.assertIn("evaluate_achievement", calls,
                      "print_achievement should call evaluate_achievement (replace score param with query)")

    def test_evaluate_achievement_takes_single_parameter(self):
        func = collect_func_def_from_module(self.module).get("evaluate_achievement")
        self.assertIsNotNone(func)
        params = _get_func_params(func)
        self.assertEqual(len(params), 1, "evaluate_achievement should take a single achievement parameter")
        self.assertEqual(params[0], "achievement")
