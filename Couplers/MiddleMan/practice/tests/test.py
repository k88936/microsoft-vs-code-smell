import ast
import unittest
from pathlib import Path

from test_utils import (
    collect_class_def_from_module,
    collect_method_from_class_in_module,
    has_return_attr_call_in_func_def,
)

SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "task.py"


class MiddleManCodeSmellTest(unittest.TestCase):
    source_text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_text = SOURCE_PATH.read_text(encoding="utf-8")

    def test_middle_man_class_removed(self):
        tree = ast.parse(self.source_text)
        classes = collect_class_def_from_module(tree)

        assert "MiddleMan" not in classes, 'Please, remove "MiddleMan" class'

    def test_client_uses_data_provider_directly(self):
        tree = ast.parse(self.source_text)
        process_data = collect_method_from_class_in_module(
            tree,
            class_name="Client",
            method_name="process_data",
        )

        assert process_data is not None, "Expected Client.process_data to be present."
        assert has_return_attr_call_in_func_def(
            process_data,
            attr_name="fetch_data",
            receiver_name="data_provider",
        ), 'Please, invoke "data_provider.fetch_data()" inside "Client.process_data" method.'
