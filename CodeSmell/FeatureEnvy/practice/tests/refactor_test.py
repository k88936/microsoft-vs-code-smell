import ast
import unittest
from pathlib import Path

from test_utils import collect_method_from_class_in_module

CAR_SOURCE_PATH = Path(__file__).resolve().parents[1] / "car.py"
DRIVER_SOURCE_PATH = Path(__file__).resolve().parents[1] / "driver.py"


class FindMoreAppropriateClassesForMethodsTest(unittest.TestCase):
    car_source_text: str
    driver_source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.car_source_text = CAR_SOURCE_PATH.read_text(encoding="utf-8")
        cls.driver_source_text = DRIVER_SOURCE_PATH.read_text(encoding="utf-8")

    def test_start_method_moved_to_car_class(self):
        car_tree = ast.parse(self.car_source_text)
        driver_tree = ast.parse(self.driver_source_text)

        assert collect_method_from_class_in_module(car_tree, "Car", "start") is not None, (
            'Please, move the "start" method to Car class'
        )
        assert collect_method_from_class_in_module(driver_tree, "Driver", "_start") is None, (
            'Please, remove the "_start" method from Driver class'
        )

    def test_stop_method_moved_to_car_class(self):
        car_tree = ast.parse(self.car_source_text)
        driver_tree = ast.parse(self.driver_source_text)

        assert collect_method_from_class_in_module(car_tree, "Car", "stop") is not None, (
            'Please, move the "stop" method to Car class'
        )
        assert collect_method_from_class_in_module(driver_tree, "Driver", "_stop") is None, (
            'Please, remove the "_stop" method from Driver class'
        )
