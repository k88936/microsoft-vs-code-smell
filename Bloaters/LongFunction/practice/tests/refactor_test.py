import ast
import sys
import unittest
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from test_utils import (
    collect_class_def_from_module,
    collect_func_def_from_module,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _get_nested_class(cls_node: ast.ClassDef, name: str) -> Optional[ast.ClassDef]:
    for node in cls_node.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _get_func_params(func: ast.FunctionDef) -> List[str]:
    return [arg.arg for arg in func.args.args]


def _get_return_annotation(func: ast.FunctionDef) -> Optional[str]:
    if func.returns and isinstance(func.returns, ast.Name):
        return func.returns.id
    return None


def _has_return_call_chain(func: ast.FunctionDef, outer: str, inner: str) -> bool:
    if not (isinstance(func.body[-1], ast.Return) and isinstance(func.body[-1].value, ast.Call)):
        return False
    outer_call = func.body[-1].value
    if not (isinstance(outer_call.func, ast.Name) and outer_call.func.id == outer):
        return False
    if not outer_call.args:
        return False
    inner_call = outer_call.args[0]
    return (
        isinstance(inner_call, ast.Call)
        and isinstance(inner_call.func, ast.Name)
        and inner_call.func.id == inner
    )


class StatementExtractionRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def test_statement_delegates_to_render_plain_text_and_compute_statement_data(self):
        func = collect_func_def_from_module(self.module).get("statement")
        self.assertIsNotNone(func)
        self.assertTrue(_has_return_call_chain(func, "render_plain_text", "compute_statement_data"))

    def test_statement_has_correct_parameters(self):
        func = collect_func_def_from_module(self.module).get("statement")
        self.assertEqual(_get_func_params(func), ["invoice", "plays"])

    def test_compute_statement_data_exists(self):
        self.assertIsNotNone(collect_func_def_from_module(self.module).get("compute_statement_data"))

    def test_compute_statement_data_has_correct_parameters(self):
        func = collect_func_def_from_module(self.module).get("compute_statement_data")
        self.assertEqual(_get_func_params(func), ["invoice", "plays"])

    def test_compute_statement_data_returns_statement_data(self):
        func = collect_func_def_from_module(self.module).get("compute_statement_data")
        self.assertEqual(_get_return_annotation(func), "StatementData")

    def test_render_plain_text_exists(self):
        self.assertIsNotNone(collect_func_def_from_module(self.module).get("render_plain_text"))

    def test_render_plain_text_has_correct_parameters(self):
        func = collect_func_def_from_module(self.module).get("render_plain_text")
        self.assertEqual(_get_func_params(func), ["statement_data"])


    def test_statement_data_class_exists(self):
        cls_node = collect_class_def_from_module(self.module).get("StatementData")
        self.assertIsNotNone(cls_node)