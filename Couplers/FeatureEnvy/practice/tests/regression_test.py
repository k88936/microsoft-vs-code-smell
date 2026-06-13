import unittest

from FeatureEnvy.practice.car import Car


class RegressionTest(unittest.TestCase):
    def test_car_status(self):
        car = Car(5)
        assert car.brake == True , "car brake should be on before drive"
        assert car.engine_started == False , "car engine should be off before drive"
        assert car.gear == 0 , "car gear should be 0 before drive"
        car.start()
        assert car.brake == False , "car brake should be off when drive"
        assert car.engine_started == True , "car engine should be on when drive"
        assert car.gear > 0 , "car gear should greater than 0 when drive"
        car.stop()
        assert car.brake == True , "car brake should be on after drive"
        assert car.engine_started == False , "car engine should be off after drive"
        assert car.gear == 0 , "car gear should be 0 after drive"

