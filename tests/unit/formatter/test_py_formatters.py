import unittest
from unittest.mock import patch
from docnsrt.formatter.python_formatters import PythonPepFormatter, PythonNumpyFormatter
from docnsrt.core.models import (
    DocstringTemplateModel,
    DocstringModel,
    FunctionContextModel,
    ParameterModel,
)


class TestPepFormatter(unittest.TestCase):

    @patch("docnsrt.formatter.python_formatters.fu.get_line_text_offset_spaces")
    def test_get_formatted_documentation(self, mock_get_line_text_offset_spaces):

        # mock return 4 spaces (tab)
        mock_get_line_text_offset_spaces.return_value = 4

        formatter = PythonPepFormatter()
        test_func_context = FunctionContextModel(
            qualified_name="test.class.func",
            signature="def func()",
            parameters=[ParameterModel("param", "any", "_desc_")],
            start_line=1,
            docstring=DocstringModel(lines=[], start_line=2),
            return_type="str",
        )
        test_func_summary = DocstringTemplateModel(
            summary="_summary_",
            return_description="_desc_",
            parameters=[ParameterModel("param", "any", "_desc_")],
            return_type="str",
        )
        test_doc_model = formatter.get_formatted_docstring(
            file_path="test_file.py",
            func_context=test_func_context,
            template_values=test_func_summary,
        )

        expected_docstring = [
            '"""\n',
            "_summary_\n",
            "\n",
            "Args:\n",
            "    param (any): _desc_\n",
            "\n",
            "Returns:\n",
            "    str: _desc_\n",
            '"""\n',
        ]

        assert (
            test_doc_model.offset_spaces == 8
        )  # must be a tab (4) added to existing (provided by mock)
        assert (
            test_doc_model.start_line == 2
        )  # pep docstrings go right below the signature
        assert test_doc_model.formatted_documentation == expected_docstring


class TestNumpyFormatter(unittest.TestCase):
    @patch("docnsrt.formatter.python_formatters.fu.get_line_text_offset_spaces")
    def test_get_formatted_documentation(self, mock_get_line_text_offset_spaces):

        # mock return 4 spaces (tab)
        mock_get_line_text_offset_spaces.return_value = 4

        formatter = PythonNumpyFormatter()
        test_func_context = FunctionContextModel(
            qualified_name="test.class.func",
            signature="def func()",
            parameters=[ParameterModel("param", "any", "_desc_")],
            start_line=1,
            docstring=DocstringModel(lines=[], start_line=2),
            return_type="str",
        )
        test_func_summary = DocstringTemplateModel(
            summary="_summary_",
            return_description="_desc_",
            parameters=[ParameterModel("param", "any", "_desc_")],
            return_type="str",
        )
        test_doc_model = formatter.get_formatted_docstring(
            file_path="test_file.py",
            func_context=test_func_context,
            template_values=test_func_summary,
        )

        expected_docstring = [
            '"""\n',
            "_summary_\n",
            "\n",
            "Parameters\n",
            "----------\n",
            "param : (any)\n",
            "    _desc_\n",
            "\n",
            "Returns\n",
            "-------\n",
            "str\n",
            "    _desc_\n",
            "\n",
            "Examples\n",
            "--------\n",
            "\n",
            '"""\n',
        ]

        assert (
            test_doc_model.offset_spaces == 8
        )  # must be a tab (4) added to existing (provided by mock)
        assert (
            test_doc_model.start_line == 2
        )  # pep docstrings go right below the signature
        assert test_doc_model.formatted_documentation == expected_docstring
