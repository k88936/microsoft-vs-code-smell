import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_class_def_from_module,
    collect_method_from_class_in_module,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


class RefusedBequestRefactorTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")


    def test_resizeable_abc_exists(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        self.assertIn(
            "Resizeable", classes,
            'Expected extracted ABC "Resizeable" to exist',
        )

    def test_scalable_abc_exists(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        self.assertIn(
            "Scalable", classes,
            'Expected extracted ABC "Scalable" to exist',
        )

    def test_choppable_abc_exists(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        self.assertIn(
            "Choppable", classes,
            'Expected extracted ABC "Choppable" to exist',
        )

    def test_element_has_only_common_methods(self):
        tree = ast.parse(self.source_text)
        methods = collect_method_from_class_in_module(tree, class_name="Element")
        self.assertIn("draw", methods, '"draw" should remain in Element')
        self.assertIn("move", methods, '"move" should remain in Element')
        self.assertNotIn(
            "resize", methods,
            '"resize" should be extracted out of Element (Refused Bequest)',
        )
        self.assertNotIn(
            "scale", methods,
            '"scale" should be extracted out of Element (Refused Bequest)',
        )
        self.assertNotIn(
            "chop", methods,
            '"chop" should be extracted out of Element (Refused Bequest)',
        )

    def test_rectangle_inherits_element_and_resizeable(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        rect = classes.get("Rectangle")
        self.assertIsNotNone(rect, 'Expected "Rectangle" class')
        base_names = {b.id for b in rect.bases if isinstance(b, ast.Name)}
        self.assertIn("Element", base_names, msg='"Rectangle" should inherit from Element')
        self.assertIn("Resizeable", base_names, msg='"Rectangle" should inherit from Resizeable')

    def test_rectangle_does_not_inherit_unused_abcs(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        rect = classes.get("Rectangle")
        self.assertIsNotNone(rect, 'Expected "Rectangle" class')
        base_names = {b.id for b in rect.bases if isinstance(b, ast.Name)}
        self.assertNotIn(
            "Scalable", base_names,
            '"Rectangle" should NOT inherit Scalable (Refused Bequest)',
        )
        self.assertNotIn(
            "Choppable", base_names,
            '"Rectangle" should NOT inherit Choppable (Refused Bequest)',
        )

    def test_rectangle_has_resize_method(self):
        tree = ast.parse(self.source_text)
        methods = collect_method_from_class_in_module(tree, class_name="Rectangle")
        self.assertIn("resize", methods, '"Rectangle" should implement resize')


    def test_image_inherits_element_scalable_choppable(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        img = classes.get("Image")
        self.assertIsNotNone(img, 'Expected "Image" class')
        base_names = {b.id for b in img.bases if isinstance(b, ast.Name)}
        self.assertIn("Element", base_names, msg='"Image" should inherit from Element')
        self.assertIn("Scalable", base_names, msg='"Image" should inherit from Scalable')
        self.assertIn("Choppable", base_names, msg='"Image" should inherit from Choppable')

    def test_image_does_not_inherit_resizeable(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)
        img = classes.get("Image")
        self.assertIsNotNone(img, 'Expected "Image" class')
        base_names = {b.id for b in img.bases if isinstance(b, ast.Name)}
        self.assertNotIn(
            "Resizeable", base_names,
            '"Image" should NOT inherit Resizeable (Refused Bequest)',
        )

    def test_image_has_scale_and_chop_methods(self):
        tree = ast.parse(self.source_text)
        methods = collect_method_from_class_in_module(tree, class_name="Image")
        self.assertIn("scale", methods, '"Image" should implement scale')
        self.assertIn("chop", methods, '"Image" should implement chop')

    def test_image_does_not_have_resize_method(self):
        tree = ast.parse(self.source_text)
        methods = collect_method_from_class_in_module(tree, class_name="Image")
        self.assertNotIn(
            "resize", methods,
            '"Image" should NOT implement resize (Refused Bequest)',
        )
