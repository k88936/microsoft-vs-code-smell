import unittest
from Minigames.Loops.practice.task import compute_damage_from_sunshine

class RegressionTest(unittest.TestCase):
    def test(self):
        example_sunshine_input = [12.5, 25, 100, 200, 200, 25]
        result= compute_damage_from_sunshine(example_sunshine_input)
        self.assertEqual(result, 48)
