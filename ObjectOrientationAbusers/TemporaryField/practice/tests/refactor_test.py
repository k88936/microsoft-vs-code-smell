import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from test_utils import (
    collect_class_def_from_module,
    collect_func_calls_from_func_def,
    collect_func_def_from_module,
    get_class_field_annotations,
    get_module_level_assignment,
    get_union_member_names,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"

# The concrete structs the nullable DTO mirror must be replaced by.
CONCRETE_STRUCTS = {
    "ImageResource": [
        ("resource_id", "str"),
        ("width", "int"),
        ("height", "int"),
        ("object_key", "str"),
    ],
    "VideoResource": [
        ("resource_id", "str"),
        ("width", "int"),
        ("height", "int"),
        ("object_key", "str"),
        ("duration_ms", "int"),
    ],
    "ImageSequenceResource": [
        ("resource_id", "str"),
        ("width", "int"),
        ("height", "int"),
        ("image_sequence", "Frame"),
        ("duration_ms", "int"),
    ],
}

UNION_MEMBERS = ["ImageResource", "VideoResource", "ImageSequenceResource"]

# The DTO keeps carrying every field as nullable; that is the boundary we convert at.
DTO_NULLABLE_FIELDS = ("object_key", "width", "height", "duration_ms", "image_sequence")


class CanvaResourceUnionRefactorTest(unittest.TestCase):
    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def _class(self, name: str) -> ast.ClassDef:
        node = collect_class_def_from_module(self.module).get(name)

        self.assertIsNotNone(node, f"{name} must be a module level class")
        return node

    def _function(self, name: str) -> ast.FunctionDef:
        node = collect_func_def_from_module(self.module).get(name)

        self.assertIsNotNone(node, f"{name} must stay a module level function")
        return node

    def _union_value(self) -> ast.expr:
        node = get_module_level_assignment(self.module, "CanvaResource")

        self.assertIsNotNone(node, "CanvaResource must be a module level type alias")
        return node

    # the nullable mirror is gone

    def test_canva_resource_is_a_union_alias_not_a_mirrored_class(self) -> None:
        self.assertNotIn(
            "CanvaResource",
            collect_class_def_from_module(self.module),
            "the nullable CanvaResource mirror must not survive as a class",
        )
        self.assertEqual(
            get_union_member_names(self._union_value()),
            UNION_MEMBERS,
            "CanvaResource must alias the three concrete structs",
        )

    # each kind is a concrete, non-nullable, frozen struct

    def test_every_kind_gets_its_own_frozen_struct(self) -> None:
        for name in CONCRETE_STRUCTS:
            with self.subTest(struct=name):
                decorators = [ast.unparse(item) for item in self._class(name).decorator_list]

                self.assertEqual(decorators, ["dataclass(frozen=True)"])

    def test_each_struct_declares_exactly_its_own_fields(self) -> None:
        for name, expected in CONCRETE_STRUCTS.items():
            with self.subTest(struct=name):
                self.assertEqual(get_class_field_annotations(self._class(name)), expected)

    def test_no_concrete_struct_field_is_nullable(self) -> None:
        for name in CONCRETE_STRUCTS:
            for field_name, annotation in get_class_field_annotations(self._class(name)):
                with self.subTest(struct=name, field=field_name):
                    self.assertNotIn(
                        "None",
                        annotation,
                        f"{name}.{field_name} must not stay nullable",
                    )

    def test_an_image_sequence_needs_no_object_key(self) -> None:
        fields = [name for name, _ in get_class_field_annotations(self._class("ImageSequenceResource"))]

        self.assertNotIn("object_key", fields, "an image sequence has no object_key field")

    def test_the_dto_stays_the_nullable_boundary(self) -> None:
        annotations = dict(get_class_field_annotations(self._class("CanvaResourceDTO")))

        for field_name in DTO_NULLABLE_FIELDS:
            with self.subTest(field=field_name):
                self.assertIn("None", annotations[field_name], f"the DTO must keep {field_name} nullable")

    # the conversion happens once, per kind

    def test_to_canva_resource_keeps_its_signature(self) -> None:
        function = self._function("to_canva_resource")
        first_parameter = function.args.args[0]

        self.assertEqual([argument.arg for argument in function.args.args], ["dto"])
        self.assertIsNotNone(first_parameter.annotation)
        self.assertEqual(ast.unparse(first_parameter.annotation), "CanvaResourceDTO")
        self.assertIsNotNone(function.returns)
        self.assertEqual(ast.unparse(function.returns), "CanvaResource")

    def test_to_canva_resource_builds_every_concrete_struct(self) -> None:
        calls = collect_func_calls_from_func_def(self._function("to_canva_resource"))

        for name in CONCRETE_STRUCTS:
            with self.subTest(struct=name):
                self.assertIn(name, calls, f"to_canva_resource must build a {name}")

    def test_to_canva_resource_does_not_rebuild_the_mirror(self) -> None:
        calls = collect_func_calls_from_func_def(self._function("to_canva_resource"))

        self.assertNotIn("CanvaResource", calls, "the converter must not construct the old mirror")

    # the state exposes the concrete structs, not the DTO shape

    def test_refresh_converts_through_to_canva_resource(self) -> None:
        calls = collect_func_calls_from_func_def(self._function("refresh_canva_resources"))

        self.assertIn("to_canva_resource", calls, "refresh must convert through to_canva_resource")
        self.assertNotIn("CanvaResource", calls, "refresh must not build the old mirror")


if __name__ == "__main__":
    unittest.main()
