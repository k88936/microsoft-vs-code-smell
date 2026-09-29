import ast
import sys
import unittest
from ast import AST, FunctionDef
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from test_utils import (  # noqa: E402
    collect_attr_acc_from_func_def,
    collect_attribute_chains,
    collect_method_from_class_in_module,
    collect_param_names,
    collect_str_constants_from_func_def,
    has_return_attribute_in_func_def,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _find_function(module: ast.Module, name: str) -> AST | FunctionDef | None:
    return next(
        (
            node
            for node in ast.walk(module)
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


class MessageChainRefactorTest(unittest.TestCase):
    """The draft should answer questions about itself, not hand out its inner route."""

    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def _require_draft_method(self, method_name: str) -> ast.FunctionDef:
        method = collect_method_from_class_in_module(
            self.module,
            class_name="Draft",
            method_name=method_name,
        )
        self.assertIsNotNone(
            method,
            f'Expected "Draft.{method_name}" to be defined.',
        )
        return method

    def test_is_empty_decides_from_the_draft_itself(self) -> None:
        is_empty = self._require_draft_method("is_empty")

        self.assertEqual(
            collect_param_names(is_empty),
            ["self"],
            'Draft.is_empty should decide from the draft it is called on, so it takes '
            "no draft as a parameter.",
        )
        chains = collect_attribute_chains(is_empty)
        for expected_chain in ("self.text.value.strip", "self.references"):
            self.assertIn(
                expected_chain,
                chains,
                f'Draft.is_empty should read "{expected_chain}": move the empty check '
                "into Draft without changing the rule it applies.",
            )
        self.assertIn(
            "",
            collect_str_constants_from_func_def(is_empty),
            'Draft.is_empty should still compare the text against "".',
        )
        self.assertIn(
            "strip",
            collect_attr_acc_from_func_def(is_empty),
            "Draft.is_empty should keep stripping the text before comparing it.",
        )

    def test_get_references_exposes_the_stored_references(self) -> None:
        get_references = self._require_draft_method("get_references")

        self.assertEqual(
            collect_param_names(get_references),
            ["self"],
            "Draft.get_references should read the references of the draft it belongs to.",
        )
        self.assertTrue(
            has_return_attribute_in_func_def(get_references, "references", "self"),
            "Draft.get_references should return self.references.",
        )
        self.assertIsInstance(
            get_references.returns,
            ast.Subscript,
            "Draft.get_references should keep its Iterable[Reference] return type.",
        )
        self.assertEqual(
            ast.unparse(get_references.returns),
            "Iterable[Reference]",
            "Draft.get_references should keep its Iterable[Reference] return type.",
        )
