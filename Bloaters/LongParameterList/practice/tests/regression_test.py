import unittest

from Bloaters.LongParameterList.practice.task import Achievement, print_achievement
from test_utils import call_and_capture_stdout


class RegressionTest(unittest.TestCase):
    def test_print_achievement_output_format(self):
        achievement = Achievement(home_lawn_security=True, roll_some_heads=False, sunny_days=True)
        output = call_and_capture_stdout(print_achievement, "Crazy Dave", achievement)
        self.assertIn("Crazy Dave", output)
        self.assertIn("True", output)
        self.assertIn("score 5", output)
