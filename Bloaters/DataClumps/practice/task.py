from dataclasses import dataclass
from math import sqrt

@dataclass
class Coordinates:
    x_coordinate: float
    y_coordinate: float
    z_coordinate: float


def l2_norm(coord: Coordinates) -> float:
    return sqrt(coord.x_coordinate ** 2 + coord.y_coordinate ** 2 + coord.z_coordinate ** 2)

def l1_norm(coord: Coordinates) -> float:
    return abs(coord.x_coordinate) + abs(coord.y_coordinate) + abs(coord.z_coordinate)


if __name__ == "__main__":
    x_coordinate = 4
    y_coordinate = -7
    z_coordinate = 43
    coordinates = Coordinates(x_coordinate,y_coordinate,z_coordinate)
    print(l1_norm(coordinates))
    print(l2_norm(coordinates))
