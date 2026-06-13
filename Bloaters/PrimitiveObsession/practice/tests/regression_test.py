from unittest import TestCase

from Bloaters.PrimitiveObsession.practice.task import main
from test_utils import call_and_capture_stdout


class RegressionTest(TestCase):
    def test(self):
        output = call_and_capture_stdout(main)
        self.assertIn("27", output)
