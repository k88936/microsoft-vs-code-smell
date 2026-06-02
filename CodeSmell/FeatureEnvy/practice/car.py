class Car:
    def __init__(self, gears_number: int) -> None:
        self._gears_number = gears_number
        self.engine_started = False
        self._gear = 0
        self.brake = True

    @property
    def gear(self) -> int:
        return self._gear

    @gear.setter
    def gear(self, value: int) -> None:
        if value > self._gears_number or value < 0:
            raise RuntimeError("Invalid gear")
        self._gear = value


    def start(self) -> None:
        self.engine_started = True
        self.brake = False
        self.gear = 1

    def stop(self) -> None:
        self.gear = 0
        self.brake = True
        self.engine_started = False
