import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_class_def_from_module,
    collect_func_def_from_module,
    get_attribute_accesses,
    get_class_fields,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _annotation_name(annotation: ast.expr | None) -> str | None:
    if isinstance(annotation, ast.Name):
        return annotation.id
    return None


def _function_calls_name(function: ast.FunctionDef, name: str) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
        for node in ast.walk(function)
    )


class PrimitiveObsessionRefactorTest(unittest.TestCase):
    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def test_generation_request_uses_typed_model_and_size(self):
        request = collect_class_def_from_module(self.module).get("GenerationRequest")

        self.assertIsNotNone(request)
        self.assertIn(("model", "GenerationModel"), get_class_fields(request))
        self.assertIn(("size", "GenerationSize"), get_class_fields(request))

    def test_generation_size_contains_typed_dimensions(self):
        size = collect_class_def_from_module(self.module).get("GenerationSize")

        self.assertIsNotNone(size)
        self.assertEqual(
            get_class_fields(size),
            [("width", "int"), ("height", "int")],
        )

    def test_typed_request_is_converted_at_the_provider_boundary(self):
        converter = collect_func_def_from_module(self.module).get(
            "to_external_generation_call_param"
        )
        handler = collect_func_def_from_module(self.module).get(
            "handle_generation_request"
        )

        self.assertIsNotNone(converter)
        self.assertEqual(len(converter.args.args), 1)
        self.assertEqual(
            _annotation_name(converter.args.args[0].annotation),
            "GenerationRequest",
        )
        self.assertEqual(
            _annotation_name(converter.returns),
            "ExternalGenerationCallParam",
        )
        self.assertIsNotNone(handler)
        self.assertTrue(_function_calls_name(handler, converter.name))

    def test_post_processing_uses_size_fields_without_parsing_a_string(self):
        post_process = collect_func_def_from_module(self.module).get(
            "do_some_crop_and_scaling"
        )

        self.assertIsNotNone(post_process)
        attributes = get_attribute_accesses(post_process)
        self.assertIn(("req", "size"), attributes)
        self.assertNotIn("split", [
            node.func.attr
            for node in ast.walk(post_process)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ])


if __name__ == "__main__":
    unittest.main()
