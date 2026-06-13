import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_class_def_from_module,
    collect_func_def_from_module,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _get_func_params(func: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in func.args.args]


class EncapsulateDataClumpsRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def test_coordinates_class_exists(self):
        cls_node = collect_class_def_from_module(self.module).get("Coordinates")
        self.assertIsNotNone(cls_node)

    def test_l2_norm_takes_single_parameter(self):
        func = collect_func_def_from_module(self.module).get("l2_norm")
        self.assertIsNotNone(func)
        params = _get_func_params(func)
        self.assertEqual(len(params), 1, "l2_norm should take a single coord parameter")
        self.assertEqual(params[0], "coord")

    def test_l1_norm_takes_single_parameter(self):
        func = collect_func_def_from_module(self.module).get("l1_norm")
        self.assertIsNotNone(func)
        params = _get_func_params(func)
        self.assertEqual(len(params), 1, "l1_norm should take a single coord parameter")
        self.assertEqual(params[0], "coord")