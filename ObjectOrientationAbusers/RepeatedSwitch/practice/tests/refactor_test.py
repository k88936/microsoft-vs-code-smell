import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from test_utils import (  # noqa: E402
    collect_attr_acc_from_func_def,
    collect_class_def_from_module,
    collect_func_def_from_module,
    collect_method_from_class_in_module,
    collect_str_constants_from_func_def,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"

BASE_CLASS = "GenerationTool"

TOOL_NAMES = {
    "ImageGenTool": "image-gen",
    "EditImageTool": "edit-image",
    "VideoGenTool": "video-gen",
}

ENTRY_POINTS = ("get_system_prompt", "on_tool_call")


def class_string_attributes(cls_node: ast.ClassDef) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for node in cls_node.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value.value, str):
                    attributes[target.id] = node.value.value
    return attributes


def compares_with_a_string_literal(test: ast.expr) -> bool:
    for node in ast.walk(test):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        if any(isinstance(operand, ast.Constant) and isinstance(operand.value, str) for operand in operands):
            return True
    return False


def branches_on_a_string_literal(node: ast.AST) -> int:
    return sum(
        1
        for child in ast.walk(node)
        if isinstance(child, ast.If) and compares_with_a_string_literal(child.test)
    )


def module_string_literals(module: ast.Module) -> list[str]:
    return [
        node.value
        for node in ast.walk(module)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


class TaskSourceTest(unittest.TestCase):
    source_text: str
    module: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)


class ToolHierarchyTest(TaskSourceTest):
    """Every generation kind must be a class behind one shared abstraction."""

    def test_generation_tool_declares_the_hooks_as_abstract(self) -> None:
        classes = collect_class_def_from_module(self.module)
        base = classes.get(BASE_CLASS)
        self.assertIsNotNone(base, f'Expected the shared abstraction "{BASE_CLASS}" to exist')

        base_names = {name.id for name in base.bases if isinstance(name, ast.Name)}
        self.assertIn("ABC", base_names, f'"{BASE_CLASS}" must stay an ABC')

        methods = collect_method_from_class_in_module(self.module, class_name=BASE_CLASS)
        for hook in ("validate_arg", "execute"):
            with self.subTest(hook=hook):
                self.assertIn(hook, methods, f'"{BASE_CLASS}" must declare "{hook}"')
                decorators = {ast.unparse(decorator) for decorator in methods[hook].decorator_list}
                self.assertIn("abstractmethod", decorators, f'"{hook}" must stay abstract')

    def test_every_tool_inherits_generation_tool(self) -> None:
        classes = collect_class_def_from_module(self.module)

        for tool in TOOL_NAMES:
            with self.subTest(tool=tool):
                cls = classes.get(tool)
                self.assertIsNotNone(cls, f'Expected "{tool}" to be its own class')
                base_names = {name.id for name in cls.bases if isinstance(name, ast.Name)}
                self.assertIn(
                    BASE_CLASS, base_names,
                    f'"{tool}" must inherit from {BASE_CLASS} instead of being switched on',
                )

    def test_every_tool_keeps_its_prompt_description(self) -> None:
        classes = collect_class_def_from_module(self.module)

        for tool in TOOL_NAMES:
            with self.subTest(tool=tool):
                cls = classes.get(tool)
                self.assertIsNotNone(cls, f'Expected "{tool}" to be its own class')
                self.assertTrue(
                    class_string_attributes(cls).get("desc"),
                    f'"{tool}" must keep its prompt description',
                )


class NoSwitchLeftTest(TaskSourceTest):
    """The conditional dispatch must be gone, not parked somewhere else."""

    def test_no_function_branches_on_a_string_literal(self) -> None:
        offenders = [
            node.name
            for node in ast.walk(self.module)
            if isinstance(node, ast.FunctionDef) and branches_on_a_string_literal(node)
        ]

        self.assertEqual(
            offenders, [],
            f"these functions still switch on a name: {offenders}",
        )

    def test_entry_points_do_not_know_tool_names(self) -> None:
        functions = collect_func_def_from_module(self.module)

        for entry_point in ENTRY_POINTS:
            with self.subTest(function=entry_point):
                func = functions.get(entry_point)
                self.assertIsNotNone(func, f'Expected the entry point "{entry_point}" to exist')
                literals = set(collect_str_constants_from_func_def(func))
                for tool, tool_name in TOOL_NAMES.items():
                    self.assertNotIn(
                        tool_name, literals,
                        f'"{entry_point}" must not special-case "{tool}"',
                    )

    def test_each_tool_name_is_declared_only_once(self) -> None:
        literals = module_string_literals(self.module)

        for tool, tool_name in TOOL_NAMES.items():
            with self.subTest(tool=tool):
                self.assertEqual(
                    literals.count(tool_name), 1,
                    f'knowledge of "{tool_name}" is still duplicated across the module',
                )


class PolymorphicDispatchTest(TaskSourceTest):
    """The entry points must go through the abstraction, not around it."""

    def test_on_tool_call_delegates_to_the_tool(self) -> None:
        func = collect_func_def_from_module(self.module).get("on_tool_call")
        self.assertIsNotNone(func, 'Expected "on_tool_call" to exist')

        called_attributes = set(collect_attr_acc_from_func_def(func))
        self.assertIn("validate_arg", called_attributes, "on_tool_call must ask the tool to validate")
        self.assertIn("execute", called_attributes, "on_tool_call must ask the tool to run")

    def test_system_prompt_asks_each_tool_to_describe_itself(self) -> None:
        func = collect_func_def_from_module(self.module).get("get_system_prompt")
        self.assertIsNotNone(func, 'Expected "get_system_prompt" to exist')

        self.assertIn(
            "describe", set(collect_attr_acc_from_func_def(func)),
            "the prompt must come from the tools, not from a switch",
        )


if __name__ == "__main__":
    unittest.main()
