import ast
import unittest
from pathlib import Path

from test_utils import collect_func_def_from_module, collect_func_calls_from_func_def

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def has_inline_file_check(function_node: ast.FunctionDef) -> bool:
    for node in ast.walk(function_node):
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.BoolOp)
                and isinstance(test.op, ast.Or)
                and len(test.values) == 2
            ):
                checks = []
                for value in test.values:
                    if (
                        isinstance(value, ast.UnaryOp)
                        and isinstance(value.op, ast.Not)
                        and isinstance(value.operand, ast.Call)
                        and isinstance(value.operand.func, ast.Attribute)
                        and value.operand.func.attr in {"exists", "is_file"}
                    ):
                        checks.append(value.operand.func.attr)
                if set(checks) == {"exists", "is_file"}:
                    return True
    return False

class ExtractTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")

    def test_extract_duplicated_validation(self):
        tree = ast.parse(self.source_text)
        functions = collect_func_def_from_module(tree)
        target_functions = {"word_count", "copy_file"}

        assert target_functions.issubset(functions), (
            "Expected both word_count and copy_file to be present."
        )

        helper_candidates = [
            fn
            for name, fn in functions.items()
            if name not in target_functions and has_inline_file_check(fn)
        ]
        assert len(helper_candidates) == 1, (
            "Please extract duplicated file validation into exactly one shared helper."
        )

        helper_name = helper_candidates[0].name
        for target_name in sorted(target_functions):
            target_fn = functions[target_name]
            assert helper_name in collect_func_calls_from_func_def(target_fn), (
                f"{target_name} must call {helper_name} after extraction."
            )
            assert not has_inline_file_check(target_fn), (
                f"Do not keep duplicated inline file validation in {target_name}."
            )