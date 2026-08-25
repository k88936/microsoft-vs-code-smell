from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from observer import Observer, Subject


class PlantType(Enum):
    POTATO_MINE = auto()
    PEASHOOTER = auto()


@dataclass(frozen=True)
class Plant:
    plant_type: PlantType
    damage: int


@dataclass
class Zombie:
    name: str
    health: int

@dataclass(frozen=True)
class ZombieDefeated:
    source: Plant
    target: Zombie

class AchievementSystem(Observer[ZombieDefeated]):
    SPUDOW = "Spudow!"

    def __init__(self) -> None:
        self._unlocked: set[str] = set()

    def on_notify(self, event: ZombieDefeated) -> None:
        if event.source.plant_type is PlantType.POTATO_MINE:
            self._unlocked.add(self.SPUDOW)

    def is_unlocked(self, name: str) -> bool:
        return name in self._unlocked


@dataclass(frozen=True)
class HitEvent:
    source: Plant
    target: Zombie


class PhysicsSystem:
    def __init__(self) -> None:
        self._hit_events: deque[HitEvent] = deque()
        self.zombie_defeated = Subject[ZombieDefeated]()

    def queue_hit(self, event: HitEvent) -> None:
        self._hit_events.append(event)

    def resolve_hit_events(self) -> None:
        def apply_damage(event: HitEvent) -> None:
            was_alive = event.target.health > 0
            event.target.health = max(0, event.target.health - event.source.damage)
            if was_alive and event.target.health == 0:
                self.zombie_defeated.notify(
                    ZombieDefeated(source=event.source, target=event.target)
                )

        while self._hit_events:
            apply_damage(self._hit_events.popleft())


def main() -> None:
    achievement = AchievementSystem()
    physics = PhysicsSystem()
    physics.zombie_defeated.add_observer(achievement)
    potato_mine = Plant(PlantType.POTATO_MINE, damage=1800)
    zombie = Zombie("Basic Zombie", health=200)

    physics.queue_hit(HitEvent(source=potato_mine, target=zombie))
    physics.resolve_hit_events()

    if achievement.is_unlocked(AchievementSystem.SPUDOW):
        print(f"Achievement unlocked: {AchievementSystem.SPUDOW}")


if __name__ == "__main__":
    main()
