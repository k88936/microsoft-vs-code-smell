import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from Couplers.FeatureEnvy.practice.car import Car


class RegressionTest(unittest.TestCase):
    def test_car_status(self):
        car = Car(5)
        self.assertTrue(car.brake, "car brake should be on before drive")
        self.assertFalse(car.engine_started, "car engine should be off before drive")
        self.assertEqual(car.gear, 0, "car gear should be 0 before drive")
        car.start()
        self.assertFalse(car.brake, "car brake should be off when drive")
        self.assertTrue(car.engine_started, "car engine should be on when drive")
        self.assertGreater(car.gear, 0, "car gear should greater than 0 when drive")
        car.stop()
        self.assertTrue(car.brake, "car brake should be on after drive")
        self.assertFalse(car.engine_started, "car engine should be off after drive")
        self.assertEqual(car.gear, 0, "car gear should be 0 after drive")
