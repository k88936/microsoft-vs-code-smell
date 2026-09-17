import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from test_utils import (  # noqa: E402
    collect_assigned_attribute_values,
    collect_attribute_chains,
    collect_class_def_from_module,
    collect_decorator_names,
    collect_func_def_from_module,
    collect_global_declared_names,
    collect_method_from_class_in_module,
    collect_module_level_bound_names,
    collect_param_names,
    collect_raised_exception_names,
    get_class_fields,
    has_return_attribute_in_func_def,
    has_with_item_over_attribute,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"

CAMERA_SINGLETON = "camera_manager"
CAMERA_FIELDS = ("_camera_pos", "_camera_zoom", "_mutex")
MODULE_LEVEL_STATE = ("camera_pos", "camera_zoom", "camera_mutex")
READ_ACCESSORS = {"camera_pos": "_camera_pos", "camera_zoom": "_camera_zoom"}
CAMERA_COMMANDS = {"delta_pos": "delta", "factor_zoom": "factor"}


class EncapsulateGlobalDataRefactorTest(unittest.TestCase):
    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)

    def _camera_manager(self) -> ast.ClassDef:
        node = collect_class_def_from_module(self.module).get("CameraManager")

        self.assertIsNotNone(node, "'CameraManager' must be a module level class")
        return node

    def _method(self, name: str) -> ast.FunctionDef:
        method = collect_method_from_class_in_module(self.module, "CameraManager", name)

        self.assertIsNotNone(
            method,
            f"CameraManager.{name} must keep its name and stay on CameraManager",
        )
        return method

    # the camera owns its state

    def test_the_camera_state_is_encapsulated_in_one_class(self) -> None:
        fields = [name for name, _ in get_class_fields(self._camera_manager())]

        for field in CAMERA_FIELDS:
            with self.subTest(field=field):
                self.assertIn(
                    field,
                    fields,
                    f"the camera must live in the private field {field}",
                )

    def test_no_camera_state_stays_public(self) -> None:
        fields = [name for name, _ in get_class_fields(self._camera_manager())]

        for name in MODULE_LEVEL_STATE:
            with self.subTest(field=name):
                self.assertNotIn(
                    name,
                    fields,
                    f"{name} must not be a public field: the outside world uses the accessors",
                )

    def test_every_camera_builds_its_own_state(self) -> None:
        assigned = collect_assigned_attribute_values(self._method("__init__"), "self")

        self.assertEqual(assigned.get("_camera_pos"), "(0.0, 0.0)")
        self.assertEqual(assigned.get("_camera_zoom"), "1.0")
        self.assertEqual(
            assigned.get("_mutex"),
            "threading.Lock()",
            "each camera must own a lock of its own",
        )

    def test_the_state_is_readable_but_not_writable(self) -> None:
        for accessor, field in READ_ACCESSORS.items():
            with self.subTest(accessor=accessor):
                method = self._method(accessor)

                self.assertEqual(
                    collect_decorator_names(method),
                    ["property"],
                    f"{accessor} must be a read only property",
                )
                self.assertTrue(
                    has_return_attribute_in_func_def(method, field, "self"),
                    f"{accessor} must read the private state",
                )
                self.assertTrue(
                    has_with_item_over_attribute(method, "_mutex", "self"),
                    f"{accessor} must read the state under the camera lock",
                )

    # the global data is gone
    def test_no_camera_state_stays_at_module_level(self) -> None:
        bound = collect_module_level_bound_names(self.module)

        for name in MODULE_LEVEL_STATE:
            with self.subTest(name=name):
                self.assertNotIn(
                    name,
                    bound,
                    f"{name} must not be a module level variable any more",
                )

    def test_no_function_declares_a_global_any_more(self) -> None:
        declared = collect_global_declared_names(self.module)

        self.assertEqual(
            declared,
            set(),
            f"no 'global' statement may survive the refactor: {sorted(declared)}",
        )

    def test_the_clamp_helper_moved_into_the_class(self) -> None:
        self.assertNotIn(
            "_clamp_zoom",
            collect_func_def_from_module(self.module),
            "_clamp_zoom must not stay a module level function",
        )
        self.assertIn(
            "staticmethod",
            collect_decorator_names(self._method("_clamp_zoom")),
            "the clamp belongs to the camera, not to the module",
        )

    def test_the_zoom_uses_the_camera_clamp(self) -> None:
        self.assertIn(
            "self._clamp_zoom",
            collect_attribute_chains(self._method("factor_zoom")),
            "factor_zoom must clamp through CameraManager._clamp_zoom",
        )

    # every caller goes through the camera

    def test_the_module_hands_out_one_camera(self) -> None:
        self.assertIn(
            CAMERA_SINGLETON,
            collect_module_level_bound_names(self.module),
            "the module must still publish its single camera_manager",
        )

    def test_every_camera_command_keeps_its_signature(self) -> None:
        for command, argument in CAMERA_COMMANDS.items():
            with self.subTest(command=command):
                self.assertEqual(
                    collect_param_names(self._method(command)),
                    ["self", argument],
                    f"CameraManager.{command} must keep the arguments the callers use",
                )

    def test_every_camera_command_takes_the_camera_lock(self) -> None:
        for command in CAMERA_COMMANDS:
            with self.subTest(command=command):
                self.assertTrue(
                    has_with_item_over_attribute(self._method(command), "_mutex", "self"),
                    f"CameraManager.{command} must run under the camera lock",
                )

    def test_the_zoom_guard_survived_the_move(self) -> None:
        self.assertIn(
            "ValueError",
            collect_raised_exception_names(self._method("factor_zoom")),
            "factor_zoom must still reject a non positive factor",
        )

    def test_the_demo_calls_the_camera_instead_of_the_globals(self) -> None:
        chains = collect_attribute_chains(self.module)

        for command in CAMERA_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(
                    f"{CAMERA_SINGLETON}.{command}",
                    chains,
                    f"the threads must call {CAMERA_SINGLETON}.{command}(...)",
                )
        for accessor in READ_ACCESSORS:
            with self.subTest(accessor=accessor):
                self.assertIn(
                    f"{CAMERA_SINGLETON}.{accessor}",
                    chains,
                    f"reading the camera must go through {CAMERA_SINGLETON}.{accessor}",
                )

    def test_nothing_reaches_into_the_private_camera_state(self) -> None:
        for chain in collect_attribute_chains(self.module):
            if not chain.startswith(f"{CAMERA_SINGLETON}._"):
                continue
            with self.subTest(chain=chain):
                self.fail(f"{chain} reaches into the private camera state")


if __name__ == "__main__":
    unittest.main()
