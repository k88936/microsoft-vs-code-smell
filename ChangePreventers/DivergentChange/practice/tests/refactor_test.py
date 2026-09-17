import ast
import sys
import unittest
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from test_utils import (
    collect_attr_acc_from_func_def,
    collect_class_def_from_module,
    collect_method_from_class_in_module,
    get_class_fields,
)

from ChangePreventers.DivergentChange.practice.task import (  # noqa: E402
    Bounds,
    CameraManager,
    Node,
    Tree,
    UIEditor,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"

CAMERA_COMMANDS = ("delta_pos", "factor_zoom", "fit_to_bounds")

UI_EDITOR_ENTRY_POINTS = {
    "on_pan_gesture": ("self", "dx", "dy"),
    "on_zoom_gesture": ("self", "factor"),
    "fit_to_window": ("self", "window_size"),
}

CAMERA_STATE_MOVED_BY_COMMAND = {
    "delta_pos": {"self.camera_pos"},
    "factor_zoom": {"self.camera_zoom"},
    "fit_to_bounds": {"self.camera_pos", "self.camera_zoom"},
}


def _attribute_chains(node: ast.AST) -> set[str]:
    """Every dotted expression inside `node`, e.g. {"self.camera_manager"}."""
    return {
        ast.unparse(item)
        for item in ast.walk(node)
        if isinstance(item, ast.Attribute)
    }


def _param_names(function: ast.FunctionDef) -> list[str]:
    return [argument.arg for argument in function.args.args]


class DivergentChangeRefactorTest(unittest.TestCase):
    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def _class(self, name: str) -> ast.ClassDef:
        node = collect_class_def_from_module(self.module).get(name)

        self.assertIsNotNone(node, f"'{name}' must stay a module level class")
        return node

    def _ui_editor_method(self, name: str) -> ast.FunctionDef:
        method = collect_method_from_class_in_module(self.module, "UIEditor", name)

        self.assertIsNotNone(method, f"UIEditor.{name} must keep its name and stay on UIEditor")
        return method

    def _camera_manager_method(self, name: str) -> ast.FunctionDef:
        method = collect_method_from_class_in_module(self.module, "CameraManager", name)

        self.assertIsNotNone(method, f"CameraManager.{name} is missing")
        return method

    # the extracted module
    def test_camera_manager_owns_the_camera_state(self) -> None:
        fields = [name for name, _ in get_class_fields(self._class("CameraManager"))]

        self.assertIn("camera_pos", fields, "CameraManager must hold the camera position")
        self.assertIn("camera_zoom", fields, "CameraManager must hold the camera zoom")

    def test_camera_manager_owns_its_own_lock(self) -> None:
        fields = [name for name, _ in get_class_fields(self._class("CameraManager"))]

        self.assertIn("mutex", fields, "the camera must own a lock of its own")
        for command in CAMERA_COMMANDS:
            with self.subTest(command=command):
                chains = _attribute_chains(self._camera_manager_method(command))

                self.assertIn(
                    "self.mutex",
                    chains,
                    f"CameraManager.{command} must take the camera lock",
                )

    def test_camera_gestures_do_not_take_the_editor_lock(self) -> None:
        for entry_point in ("on_pan_gesture", "on_zoom_gesture"):
            with self.subTest(entry_point=entry_point):
                chains = _attribute_chains(self._ui_editor_method(entry_point))

                self.assertNotIn(
                    "self.mutex",
                    chains,
                    f"UIEditor.{entry_point} must not hold the editor lock to touch the camera",
                )

    def test_fit_to_window_leaves_the_editor_lock_before_the_camera(self) -> None:
        method = self._ui_editor_method("fit_to_window")

        self.assertIn(
            "self.mutex",
            _attribute_chains(method),
            "reading the trees is editor work, so that read stays under the editor lock",
        )
        for node in ast.walk(method):
            if not isinstance(node, ast.With):
                continue
            held = {ast.unparse(item.context_expr) for item in node.items}
            if "self.mutex" not in held:
                continue
            under_editor_lock = _attribute_chains(node)
            for command in CAMERA_COMMANDS:
                with self.subTest(command=command):
                    self.assertNotIn(
                        f"self.camera_manager.{command}",
                        under_editor_lock,
                        "the camera call must happen after the editor lock is released",
                    )

    def test_ui_editor_keeps_only_the_camera_manager(self) -> None:
        fields = get_class_fields(self._class("UIEditor"))
        names = [name for name, _ in fields]

        self.assertIn(("camera_manager", "CameraManager"), fields, "UIEditor must reach the camera through CameraManager")
        self.assertNotIn("camera_pos", names, "the raw camera_pos field belongs to CameraManager now")
        self.assertNotIn("camera_zoom", names, "the raw camera_zoom field belongs to CameraManager now")

    def test_ui_editor_keeps_its_own_editor_state(self) -> None:
        names = [name for name, _ in get_class_fields(self._class("UIEditor"))]

        for field in ("ui_trees", "spirits", "selected_node", "mutex"):
            with self.subTest(field=field):
                self.assertIn(
                    field,
                    names,
                    f"UIEditor must still own {field}; only the camera moved out",
                )

    def test_camera_manager_implements_every_camera_command(self) -> None:
        for command in CAMERA_COMMANDS:
            with self.subTest(command=command):
                self.assertIsNotNone(
                    collect_method_from_class_in_module(self.module, "CameraManager", command),
                    f"CameraManager.{command} must exist",
                )

    def test_camera_manager_stays_out_of_the_ui_trees(self) -> None:
        for name, method in collect_method_from_class_in_module(self.module, "CameraManager").items():
            for chain in _attribute_chains(method):
                for foreign in (".ui_trees", ".spirits", ".children"):
                    with self.subTest(method=name, chain=chain):
                        self.assertNotIn(
                            foreign,
                            chain,
                            f"CameraManager.{name} must not reach the editor through {chain}",
                        )

    # the delegating entry points

    def test_ui_editor_delegates_every_camera_command(self) -> None:
        delegation = {
            "on_pan_gesture": "delta_pos",
            "on_zoom_gesture": "factor_zoom",
            "fit_to_window": "fit_to_bounds",
        }

        for entry_point, command in delegation.items():
            with self.subTest(entry_point=entry_point):
                calls = collect_attr_acc_from_func_def(self._ui_editor_method(entry_point))

                self.assertIn(
                    command,
                    calls,
                    f"UIEditor.{entry_point} must delegate to CameraManager.{command}",
                )
    def test_ui_editor_keeps_no_camera_state_of_its_own(self) -> None:
        for name, method in collect_method_from_class_in_module(self.module, "UIEditor").items():
            chains = _attribute_chains(method)
            for stray in ("self.camera_pos", "self.camera_zoom"):
                with self.subTest(method=name):
                    self.assertNotIn(
                        stray,
                        chains,
                        f"UIEditor.{name} still reaches into {stray}",
                    )


def make_node(left: int, top: int, width: int, height: int) -> Node:
    return Node(uuid.uuid4(), [], [], (left, top), (width, height))


class CameraManagerContractTest(unittest.TestCase):
    """The extracted module keeps its guards, stays a command, and owns its lock."""

    def test_fit_to_bounds_rejects_empty_bounds(self) -> None:
        with self.assertRaises(ValueError) as caught:
            CameraManager().fit_to_bounds((400, 200), [])

        self.assertIn(
            "bounds",
            str(caught.exception),
            "empty bounds must fail with a message about bounds, not a raw min() error",
        )

    def test_fit_to_bounds_is_a_command(self) -> None:
        self.assertIsNone(
            CameraManager().fit_to_bounds((400, 200), [Bounds(0, 0, 100, 50)]),
            "fit_to_bounds is a command, not a query",
        )

    def test_camera_lock_is_not_the_editor_lock(self) -> None:
        first = CameraManager()
        second = CameraManager()
        editor = UIEditor([Tree(make_node(0, 0, 10, 10))], [])

        self.assertIsNot(first.mutex, second.mutex, "every camera manager must own its own lock")
        self.assertIsNot(
            editor.mutex,
            editor.camera_manager.mutex,
            "the editor lock must not be the camera lock",
        )


if __name__ == "__main__":
    unittest.main()
