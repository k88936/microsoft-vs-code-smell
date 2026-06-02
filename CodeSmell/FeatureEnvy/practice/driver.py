from car import Car


class Driver:
    def __init__(self, car: Car) -> None:
        self._car = car

    def change_car(self, car: Car) -> None:
        self._car = car

    def _driving(self, destination: str) -> None:
        print(f"The driver is coming to {destination}")

    def drive_to(self, destination: str) -> None:
        print("Start driving")
        self._car.start()
        self._driving(destination)
        self._car.stop()
        print("Arrived at destination")