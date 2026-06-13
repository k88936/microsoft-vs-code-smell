from typing import List
from functools import reduce

example_sunshine_input = [12.5, 25, 100, 200, 200, 25]


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
    assert isinstance(sunshine, SunShine)
    if sunshine.num >= 100:
        return Peanut()
    else:
        return None


def peanut_to_fireball(peanut: Peanut) -> Fireball:
    assert isinstance(peanut, Peanut)
    return Fireball()


def fireball_to_damage(fireball: Fireball) -> Damage:
    assert isinstance(fireball, Fireball)
    return Damage(16)


class Stream:
    def __init__(self, iterable):
        self._iter = iter(iterable)

    def map(self, func):
        """
        apply func to each element of the stream
        """
        self._iter = map(func, self._iter)
        return self

    def reduce(self, func, initial):
        """
        reduce the stream to a single value,
        it works like:
        foreach:
            {accumulated} = func({accumulated}, [i])
        specially {accumulated} is the initial value at the beginning
        example:
            func: (acc,x) => acc + x, initial: 0 means: sum all elements
        """
        return reduce(func, self._iter, initial)

    def filter(self, func):
        """
        keep only elements that satisfy the condition
        """
        self._iter = filter(func, self._iter)
        return self

    def collect(self):
        """
        compute and return a normal list from the stream
        """
        return list(self._iter)

    def __iter__(self):
        return self._iter


def compute_damage_from_sunshine(sunshine_history: List[float]) -> float:
    return (Stream(sunshine_history)
            .map(lambda x: SunShine(x))
            .map(sunshine_to_peanut)
            .filter(lambda x: x is not None)
            .map(peanut_to_fireball)
            .map(fireball_to_damage)
            .reduce(lambda acc, x: acc + x.value, 0))


if __name__ == '__main__':
    result = compute_damage_from_sunshine(example_sunshine_input)
    print(result)
