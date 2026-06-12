import unittest

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
        assert "BigCo" in result
        assert "650" in result
        assert "55" in result
        assert "580" in result
        assert "35" in result
        assert "1730" in result
        assert "47" in result
