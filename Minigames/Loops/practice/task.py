from typing import List
from functools import reduce


class SunShine:
    num: float
    def __init__(self, num: float):
        self.num = num

class Peanut:
    pass

class Fireball:
    pass

class Damage:
    value: int
    def __init__(self, value: int):
        self.value = value

def sunshine_to_peanut(sunshine: SunShine) -> Peanut | None:
    assert sunshine
    if sunshine.num >= 100:
        return Peanut()
    else:
        return None

def peanut_to_fireball(peanut: Peanut) -> Fireball:
    assert peanut
    return Fireball()


def fireball_to_damage(fireball: Fireball) -> Damage:
    assert fireball
    return Damage(16)


example_input = [12.5, 25, 100, 200, 200, 25]

class Stream:
    def __init__(self, iterable):
        self._iter = iter(iterable)

    def map(self, func):
        self._iter = map(func, self._iter)
        return self
    def reduce(self, func, initial):
        return reduce(func, self._iter,initial)

    def filter(self, func):
        self._iter = filter(func, self._iter)
        return self

    def collect(self):
        return list(self._iter)

    def __iter__(self):
        return self._iter

def compute_damage_from_sunshine(sunshine_history: List[float]) -> float:
    total = 0
    for sunshine_v in sunshine_history:
        sunshine = SunShine(sunshine_v)
        peanut = sunshine_to_peanut(sunshine)
        if not peanut:
            continue
        fireball = peanut_to_fireball(peanut)
        damage = fireball_to_damage(fireball)
        total += damage.value
    return total



if __name__ == '__main__':
    result = compute_damage_from_sunshine(example_input)
    stream = (Stream([1, 2, 3, 4, 5])
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * 10))

    # Consumes lazily
    print(stream.reduce(lambda acc,x: acc +x, 0))  # Output: 60 (20 + 40)
    print(result)
