import unittest

from Bloaters.DataClumps.practice.task import *

class RegressionTest(unittest.TestCase):
    def test_l1_norm_with_coordinates(self):
        coord = Coordinates(4, -7, 43)
        self.assertEqual(l1_norm(coord), 54)

    def test_l2_norm_with_coordinates(self):
        coord = Coordinates(4, -7, 43)
        self.assertAlmostEqual(l2_norm(coord), 43.75, places=2)

    def test_l1_norm_with_zeros(self):
        coord = Coordinates(0, 0, 0)
        self.assertEqual(l1_norm(coord), 0)

    def test_l2_norm_with_zeros(self):
        coord = Coordinates(0, 0, 0)
        self.assertEqual(l2_norm(coord), 0.0)

    def test_l1_norm_with_negative_values(self):
        coord = Coordinates(-1, -2, -3)
        self.assertEqual(l1_norm(coord), 6)

    def test_l2_norm_with_negative_values(self):
        coord = Coordinates(-1, -2, -3)
        self.assertAlmostEqual(l2_norm(coord), 3.74, places=2)
