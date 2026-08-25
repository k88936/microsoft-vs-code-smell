import ast
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from test_utils import (  # noqa: E402
    collect_class_def_from_module,
    collect_method_from_class_in_module,
    get_class_fields,
)


SOURCE_PATH = Path(__file__).resolve().parents[1] / "task.py"


def _base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Subscript):
        return _base_name(base.value)
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def _callable_name(callable_node: ast.expr) -> str | None:
    if isinstance(callable_node, ast.Name):
        return callable_node.id
    if isinstance(callable_node, ast.Subscript):
        return _callable_name(callable_node.value)
    if isinstance(callable_node, ast.Attribute):
        return callable_node.attr
    return None


def _referenced_names(node: ast.AST) -> set[str]:
    names = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
    names.update(
        child.attr for child in ast.walk(node) if isinstance(child, ast.Attribute)
    )
    return names


def _called_names(node: ast.AST) -> list[str]:
    return [
        name
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
        for name in [_callable_name(child.func)]
        if name is not None
    ]


class ObserverRefactorTest(unittest.TestCase):
    source_text: str
    module: ast.Module
    classes: dict[str, ast.ClassDef]

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")
        cls.module = ast.parse(cls.source_text)
        cls.classes = collect_class_def_from_module(cls.module)

    def _require_class(self, class_name: str) -> ast.ClassDef:
        class_node = self.classes.get(class_name)
        self.assertIsNotNone(
            class_node,
            f'Expected a "{class_name}" class in task.py.',
        )
        return class_node

    def _require_method(self, class_name: str, method_name: str) -> ast.FunctionDef:
        method = collect_method_from_class_in_module(
            self.module,
            class_name=class_name,
            method_name=method_name,
        )
        self.assertIsNotNone(
            method,
            f'Expected "{class_name}.{method_name}" to be defined.',
        )
        return method

    def test_zombie_defeated_event_carries_source_and_target(self) -> None:
        event_class = self._require_class("ZombieDefeated")
        field_names = {name for name, _ in get_class_fields(event_class)}

        self.assertIn(
            "source",
            field_names,
            'ZombieDefeated should have a "source" field for the attacking plant.',
        )
        self.assertIn(
            "target",
            field_names,
            'ZombieDefeated should have a "target" field for the defeated zombie.',
        )

    def test_achievement_system_is_a_zombie_defeated_observer(self) -> None:
        achievement_class = self._require_class("AchievementSystem")
        observer_bases = [
            base
            for base in achievement_class.bases
            if isinstance(base, ast.Subscript)
            and _base_name(base.value) == "Observer"
            and isinstance(base.slice, ast.Name)
            and base.slice.id == "ZombieDefeated"
        ]

        self.assertTrue(
            observer_bases,
            "AchievementSystem should inherit from Observer[ZombieDefeated] so its "
            "event contract is explicit.",
        )

    def test_achievement_reacts_to_defeat_in_on_notify(self) -> None:
        on_notify = self._require_method("AchievementSystem", "on_notify")
        parameter_names = [argument.arg for argument in on_notify.args.args]
        referenced = _referenced_names(on_notify)
        called = _called_names(on_notify)

        self.assertEqual(
            parameter_names,
            ["self", "event"],
            "AchievementSystem.on_notify should accept exactly self and the defeat event.",
        )
        self.assertIn(
            "POTATO_MINE",
            referenced,
            "AchievementSystem.on_notify should decide whether the defeat was caused by "
            "a potato mine.",
        )
        self.assertIn(
            "SPUDOW",
            referenced,
            'AchievementSystem.on_notify should unlock the "Spudow!" achievement.',
        )
        self.assertIn(
            "add",
            called,
            "AchievementSystem.on_notify should add the unlocked achievement to its set.",
        )

    def test_old_unlock_command_is_removed(self) -> None:
        methods = collect_method_from_class_in_module(
            self.module,
            class_name="AchievementSystem",
        )

        self.assertNotIn(
            "unlock",
            methods,
            "Remove AchievementSystem.unlock; the observer's on_notify method should own "
            "the achievement reaction.",
        )

    def test_physics_constructor_has_no_achievement_dependency(self) -> None:
        constructor = self._require_method("PhysicsSystem", "__init__")
        parameters = [argument.arg for argument in constructor.args.args]

        self.assertEqual(
            parameters,
            ["self"],
            "PhysicsSystem.__init__ should not receive AchievementSystem; construct physics "
            "independently and subscribe observers from main().",
        )
        self.assertNotIn(
            "_achievement",
            _referenced_names(constructor),
            "PhysicsSystem should not store an AchievementSystem reference.",
        )

    def test_physics_exposes_a_zombie_defeated_subject(self) -> None:
        constructor = self._require_method("PhysicsSystem", "__init__")
        subject_assignments = []
        for assignment in ast.walk(constructor):
            if not isinstance(assignment, (ast.Assign, ast.AnnAssign)):
                continue
            targets = (
                assignment.targets
                if isinstance(assignment, ast.Assign)
                else [assignment.target]
            )
            value = assignment.value
            for target in targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                    and target.attr == "zombie_defeated"
                    and isinstance(value, ast.Call)
                    and _callable_name(value.func) == "Subject"
                ):
                    subject_assignments.append(assignment)

        self.assertTrue(
            subject_assignments,
            "PhysicsSystem.__init__ should expose a zombie_defeated Subject so observers "
            "can subscribe without coupling physics to achievements.",
        )

    def test_resolve_hit_events_publishes_zombie_defeated(self) -> None:
        resolve = self._require_method("PhysicsSystem", "resolve_hit_events")
        defeat_notifications = [
            call
            for call in ast.walk(resolve)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "notify"
            and isinstance(call.func.value, ast.Attribute)
            and call.func.value.attr == "zombie_defeated"
            and isinstance(call.func.value.value, ast.Name)
            and call.func.value.value.id == "self"
            and len(call.args) == 1
            and isinstance(call.args[0], ast.Call)
            and _callable_name(call.args[0].func) == "ZombieDefeated"
        ]

        self.assertTrue(
            defeat_notifications,
            "When a zombie's health first reaches zero, publish the event with "
            "self.zombie_defeated.notify(ZombieDefeated(...)).",
        )

    def test_physics_contains_no_achievement_policy(self) -> None:
        resolve = self._require_method("PhysicsSystem", "resolve_hit_events")
        referenced = _referenced_names(resolve)

        for forbidden_name in (
            "AchievementSystem",
            "SPUDOW",
            "POTATO_MINE",
            "_achievement",
        ):
            self.assertNotIn(
                forbidden_name,
                referenced,
                f'PhysicsSystem.resolve_hit_events still references "{forbidden_name}". '
                "Move achievement-specific decisions to AchievementSystem.on_notify.",
            )

    def test_main_subscribes_achievement_to_physics(self) -> None:
        main = next(
            (
                node
                for node in self.module.body
                if isinstance(node, ast.FunctionDef) and node.name == "main"
            ),
            None,
        )
        self.assertIsNotNone(main, 'Expected a top-level "main" function.')

        subscription_calls = [
            call
            for call in ast.walk(main)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "add_observer"
            and isinstance(call.func.value, ast.Attribute)
            and call.func.value.attr == "zombie_defeated"
            and isinstance(call.func.value.value, ast.Name)
            and call.func.value.value.id == "physics"
            and len(call.args) == 1
            and isinstance(call.args[0], ast.Name)
            and call.args[0].id == "achievement"
        ]
        self.assertTrue(
            subscription_calls,
            "main() should connect the systems by subscribing AchievementSystem to "
            "PhysicsSystem with physics.zombie_defeated.add_observer(achievement).",
        )
