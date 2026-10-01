import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from Bloaters.LongFunction.practice.task import statement

test_plays = {
    "hamlet": {"name": "Hamlet", "type": "tragedy"},
    "as-like": {"name": "As You Like It", "type": "comedy"},
    "othello": {"name": "Othello", "type": "tragedy"},
}

test_invoices = [
    {
        "customer": "BigCo",
        "performances": [
            {"playID": "hamlet", "audience": 55},
            {"playID": "as-like", "audience": 35},
            {"playID": "othello", "audience": 40},
        ],
    }
]


class RegressionTest(unittest.TestCase):
    def test_regression(self):
        result = statement(test_invoices[0], test_plays)
        """
                Statement for BigCo
                  Hamlet: $650.00 (55 seats)
                  As You Like It: $580.00 (35 seats)
                  Othello: $500.00 (40 seats)
                Amount owed is $1730.00
                You earned 47 credits
        """
        self.assertIn("BigCo", result)
        self.assertIn("650", result)
        self.assertIn("55", result)
        self.assertIn("580", result)
        self.assertIn("35", result)
        self.assertIn("1730", result)
        self.assertIn("47", result)
