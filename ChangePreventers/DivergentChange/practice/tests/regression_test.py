import json
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ChangePreventers.DivergentChange.practice.task import (  # noqa: E402
    CAMERA_MAX_ZOOM,
    CAMERA_MIN_ZOOM,
    Node,
    Tree,
    UIEditor,
)


def make_node(left: int, top: int, width: int, height: int) -> Node:
    return Node(uuid.uuid4(), [], [], (left, top), (width, height))


def make_editor(*roots: Node) -> UIEditor:
    return UIEditor([Tree(root) for root in roots], [])


class ErrorHandlingTest(unittest.TestCase):
    """Splitting the class must not change how it fails."""

    def test_fit_rejects_non_positive_window_size(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))

        for window_size in ((0, 200), (400, 0), (-400, 200)):
            with self.subTest(window_size=window_size):
                with self.assertRaises(ValueError):
                    editor.fit_to_window(window_size)

    def test_fit_rejects_empty_editor(self) -> None:
        editor = make_editor()

        with self.assertRaises(ValueError):
            editor.fit_to_window((400, 200))

    def test_fit_rejects_root_without_size(self) -> None:
        editor = make_editor(make_node(10, 10, 0, 0))

        with self.assertRaises(ValueError):
            editor.fit_to_window((400, 200))

    def test_fit_operations_do_not_return_the_camera(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))

        self.assertIsNone(editor.fit_to_window((400, 200)), "fit_to_window is a command, not a query")

    def test_zoom_gesture_rejects_non_positive_factor(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))

        for factor in (0, -1.5):
            with self.subTest(factor=factor):
                with self.assertRaises(ValueError):
                    editor.on_zoom_gesture(factor)

    def test_select_unknown_node_raises_key_error(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))

        with self.assertRaises(KeyError):
            editor.on_select_node(uuid.uuid4())

    def test_delete_unknown_node_reports_false(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))

        self.assertFalse(editor.on_del_node(uuid.uuid4()))


class ExportEndToEndTest(unittest.TestCase):
    """What the editor exports must match what the user did on screen."""

    def export_document(self, editor: UIEditor) -> dict:
        exported = editor.export_to_json()

        self.assertIsInstance(exported, str, "export_to_json must hand back the document as a string")
        return json.loads(exported)

    def test_export_reflects_pan_and_zoom(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50))
        editor.on_pan_gesture(12.5, -3.5)
        editor.on_zoom_gesture(1.5)

        document = self.export_document(editor)

        self.assertEqual(document["camera_pos"], [12.5, -3.5])
        self.assertEqual(document["camera_zoom"], 1.5)

    def test_export_reflects_camera_after_fit_to_window(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50), make_node(100, 50, 100, 50))
        editor.on_pan_gesture(999, 999)
        editor.fit_to_window((400, 200))

        document = self.export_document(editor)

        self.assertEqual(document["camera_pos"], [100.0, 50.0])
        self.assertEqual(document["camera_zoom"], 2.0)

    def test_export_reflects_zoom_clamped_by_fit_from_below(self) -> None:
        editor = make_editor(make_node(0, 0, 10_000, 10_000))
        editor.fit_to_window((10, 10))

        document = self.export_document(editor)

        self.assertEqual(
            document["camera_zoom"],
            CAMERA_MIN_ZOOM,
            "fit_to_window must respect the camera zoom limits",
        )

    def test_export_reflects_zoom_clamped_by_fit_from_above(self) -> None:
        editor = make_editor(make_node(0, 0, 10, 10))
        editor.fit_to_window((10_000, 10_000))

        document = self.export_document(editor)

        self.assertEqual(
            document["camera_zoom"],
            CAMERA_MAX_ZOOM,
            "fit_to_window must respect the camera zoom limits",
        )

    def test_export_reflects_collection_counts(self) -> None:
        editor = make_editor(make_node(0, 0, 100, 50), make_node(0, 0, 10, 10))
        editor.import_spirit("dorm.png")
        editor.import_spirit("swim.png")

        document = self.export_document(editor)

        self.assertEqual(document["tree_count"], 2)
        self.assertEqual(document["spirit_count"], 2)


if __name__ == "__main__":
    unittest.main()
