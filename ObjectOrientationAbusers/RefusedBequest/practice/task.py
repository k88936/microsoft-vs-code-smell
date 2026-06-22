from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import product
from typing import override


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)


def draw_pixel(pix_pos:Vec2, color: int):
    print(f"draw pixel({pix_pos.x},{pix_pos.y}):{color}")


class Resizeable(ABC):
    @abstractmethod
    def resize(self, new_size: Vec2):
        pass


class Scalable(ABC):
    @abstractmethod
    def scale(self, new_scale: float):
        pass


class Choppable(ABC):
    @abstractmethod
    def chop(self, view_left_top: Vec2, view_right_bottom: Vec2):
        pass


class Element(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def move(self, new_pos: Vec2):
        pass



class Rectangle(Element, Resizeable):
    pos: Vec2
    size: Vec2
    color: int

    @override
    def draw(self):
        for (i, j) in product(range(self.size.x), range(self.size.y)):
            pix_pos = self.pos + Vec2(i, j)
            draw_pixel(pix_pos, self.color)

    @override
    def move(self, new_pos: Vec2):
        self.pos = new_pos

    @override
    def resize(self, new_size: Vec2):
        self.size = new_size




class Image(Element, Scalable, Choppable):
    pos: Vec2
    scale: float
    data: list[list[int]]

    view_left_top: Vec2
    view_right_bottom: Vec2

    @override
    def move(self, new_pos: Vec2):
        self.pos = new_pos



    @override
    def scale(self, new_scale: float):
        self.scale = new_scale

    @override
    def chop(self, view_left_top: Vec2, view_right_bottom: Vec2):
        assert view_left_top.x <= view_right_bottom.x and view_left_top.y <= view_right_bottom.y
        self.view_left_top = view_left_top
        self.view_right_bottom = view_right_bottom

    @override
    def draw(self):
        for (i, j) in product(range(self.view_left_top.x, self.view_right_bottom.x), range(self.view_left_top.y, self.view_right_bottom.y)):
            color = self.data[i][j]
            pix_pos = self.pos + Vec2(int(i*self.scale), int(j*self.scale))
            draw_pixel(pix_pos,color)
