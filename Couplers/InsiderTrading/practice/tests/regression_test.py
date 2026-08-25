import inspect
import sys
import unittest
from pathlib import Path


PRACTICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_DIR))

from Couplers.InsiderTrading.practice.task import (  # noqa: E402
    AchievementSystem,
    HitEvent,
    PhysicsSystem,
    Plant,
    PlantType,
    Zombie,
)


class InsiderTradingRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.achievement = AchievementSystem()
        constructor_parameters = inspect.signature(PhysicsSystem).parameters

        if constructor_parameters:
            # The coupled starter injects AchievementSystem directly.
            self.physics = PhysicsSystem(self.achievement)
        else:
            # The refactored version connects the independent systems via a Subject.
            self.physics = PhysicsSystem()
            self.physics.zombie_defeated.add_observer(self.achievement)

    def test_lethal_potato_mine_hit_unlocks_spudow(self) -> None:
        potato_mine = Plant(PlantType.POTATO_MINE, damage=1800)
        zombie = Zombie("Basic Zombie", health=200)

        self.physics.queue_hit(HitEvent(source=potato_mine, target=zombie))
        self.physics.resolve_hit_events()

        self.assertEqual(
            zombie.health,
            0,
            "A lethal hit should reduce the zombie's health to zero.",
        )
        self.assertTrue(
            self.achievement.is_unlocked(AchievementSystem.SPUDOW),
            'A potato mine kill should unlock the "Spudow!" achievement.',
        )

    def test_nonlethal_hit_does_not_unlock_spudow(self) -> None:
        potato_mine = Plant(PlantType.POTATO_MINE, damage=50)
        zombie = Zombie("Armored Zombie", health=200)

        self.physics.queue_hit(HitEvent(source=potato_mine, target=zombie))
        self.physics.resolve_hit_events()

        self.assertEqual(
            zombie.health,
            150,
            "A nonlethal hit should subtract the plant's damage from zombie health.",
        )
        self.assertFalse(
            self.achievement.is_unlocked(AchievementSystem.SPUDOW),
            '"Spudow!" must remain locked until a potato mine defeats a zombie.',
        )

    def test_kill_by_another_plant_does_not_unlock_spudow(self) -> None:
        peashooter = Plant(PlantType.PEASHOOTER, damage=200)
        zombie = Zombie("Basic Zombie", health=200)

        self.physics.queue_hit(HitEvent(source=peashooter, target=zombie))
        self.physics.resolve_hit_events()

        self.assertEqual(zombie.health, 0, "The peashooter hit should still be resolved.")
        self.assertFalse(
            self.achievement.is_unlocked(AchievementSystem.SPUDOW),
            '"Spudow!" should only be unlocked by a potato mine kill.',
        )

if __name__ == "__main__":
    unittest.main()
