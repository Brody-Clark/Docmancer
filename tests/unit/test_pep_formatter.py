import unittest
from unittest.mock import patch, MagicMock
from docmancer.formatter.py_docstring_formatter import PyDocstringFormatter
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.documentation_model import DocumentationModel
import textwrap


class TestPepFormatter(unittest.TestCase):

    @patch("docmancer.formatter.py_docstring_formatter.fu.get_line_text_offset_spaces")
    def test_get_formatted_docuemntation(self, mock_get_line_text_offset_spaces):

        # mock return 4 spaces (tab)
        mock_get_line_text_offset_spaces.return_value = 4

        formatter = PyDocstringFormatter()
        test_func_context = FunctionContextModel(
            qualified_name="test.class.func",
            signature="def func()",
            body="" "pass" "",
            start_line=1,
            end_line=3,
            comments=["# this is a test"],
        )
        test_func_summary = FunctionSummaryModel(
            summary="this is a test function",
            return_description="returns nothing",
            parameters=[],
        )
        test_doc_model = formatter.get_formatted_documentation(
            func_context=test_func_context,
            func_summary=test_func_summary,
            file_path="test\\path",
        )

        expected_docstring = [
            '"""\n',
            "this is a test function\n",
            "\n",
            "\n",
            "Returns:\n",
            "    returns nothing\n",
            '"""\n',
        ]

        assert test_doc_model.file_path == "test\\path"
        assert (
            test_doc_model.offset_spaces == 8
        )  # must be a tab (4) added to existing (provided by mock)
        assert test_doc_model.start_line == 1
        assert test_doc_model.signature == "def func()"
        assert test_doc_model.formatted_documentation == expected_docstring
