import unittest
from unittest.mock import patch, MagicMock
from docnsrt.formatter.csharp_formatters import CSharpXmlFormatter
from docnsrt.core.models import (
    FunctionContextModel,
    FormattedDocstringModel,
    DocstringTemplateModel,
    ParameterModel,
    DocstringModel,
)


class TestCsharpXmlFormatter(unittest.TestCase):
    @patch("docnsrt.formatter.csharp_formatters.fu.get_line_text_offset_spaces")
    def test_get_formatted_documentation(self, mock_line_offset: MagicMock):

        mock_line_offset.return_value = 4

        formatter = CSharpXmlFormatter()
        test_func_context = FunctionContextModel(
            qualified_name="test.class.DoubleNum",
            signature="int DoubleNum(int input)",
            parameters=[
                ParameterModel(name="input", type="int", desc="number to multiply by 2")
            ],
            docstring=DocstringModel(lines=[], start_line=0),
            start_line=1,
            return_type="void",
        )

        test_param_1 = ParameterModel(
            name="input", type="int", desc="number to multiply by 2"
        )
        test_func_summary = DocstringTemplateModel(
            summary="this is a test function",
            return_description="returns input times 2",
            parameters=[test_param_1],
        )
        test_doc_model: FormattedDocstringModel = formatter.get_formatted_docstring(
            file_path="test_file.cs",
            func_context=test_func_context,
            template_values=test_func_summary,
        )

        expected_docstring = [
            "/// <summary>\n",
            "/// this is a test function\n",
            "/// </summary>\n",
            "/// <param name=\"input\">number to multiply by 2</param>\n",
            "/// <returns>returns input times 2</returns>\n",
        ]

        assert (
            test_doc_model.offset_spaces == 4
        )  # should be same offset as function declaration
        assert (
            test_doc_model.start_line == 1
        )  # XML comments go right above the signature so start_line is the same as the signature
        assert test_doc_model.formatted_documentation == expected_docstring

    @patch("docnsrt.formatter.csharp_formatters.fu.get_line_text_offset_spaces")
    def test_basic_summary_and_params(self, mock_offset):
        mock_offset.return_value = 4
        formatter = CSharpXmlFormatter()
        func_context = FunctionContextModel(
            qualified_name="TestClass.TestMethod",
            signature="int TestMethod(int x, int y)",
            parameters=[
                ParameterModel(name="x", type="int", desc="first number"),
                ParameterModel(name="y", type="int", desc="second number"),
            ],
            start_line=10,
            docstring=DocstringModel(lines=[], start_line=0),
            return_type="void",
        )
        param1 = ParameterModel(name="x", type="int", desc="first number")
        param2 = ParameterModel(name="y", type="int", desc="second number")
        func_summary = DocstringTemplateModel(
            summary="Adds two numbers.",
            return_description="The sum of x and y.",
            parameters=[param1, param2],
        )
        doc_model = formatter.get_formatted_docstring(
            file_path="test_file.cs",
            func_context=func_context,
            template_values=func_summary,
        )
        expected_lines = [
            "/// <summary>\n",
            "/// Adds two numbers.\n",
            "/// </summary>\n",
            "/// <param name=\"x\">first number</param>\n",
            "/// <param name=\"y\">second number</param>\n",
            "/// <returns>The sum of x and y.</returns>\n",
        ]
        assert doc_model.formatted_documentation == expected_lines
        assert doc_model.offset_spaces == 4
        assert doc_model.start_line == 10  # start_line is the same as the signature

    @patch("docnsrt.formatter.csharp_formatters.fu.get_line_text_offset_spaces")
    def test_no_params(self, mock_offset):
        mock_offset.return_value = 2
        formatter = CSharpXmlFormatter()
        func_context = FunctionContextModel(
            qualified_name="TestClass.NoParamMethod",
            signature="void NoParamMethod()",
            parameters=[],
            start_line=5,
            docstring=DocstringModel(lines=[], start_line=0),
            return_type="void",
        )
        func_summary = DocstringTemplateModel(
            summary="Prints Hello.",
            return_description="None.",
            parameters=[],
        )
        doc_model = formatter.get_formatted_docstring(
            file_path="test_file.cs",
            func_context=func_context,
            template_values=func_summary,
        )
        expected_lines = [
            "/// <summary>\n",
            "/// Prints Hello.\n",
            "/// </summary>\n",
            "/// <returns>None.</returns>\n",
        ]
        assert doc_model.formatted_documentation == expected_lines
        assert doc_model.offset_spaces == 2

    @patch("docnsrt.formatter.csharp_formatters.fu.get_line_text_offset_spaces")
    def test_offset_negative_raises(self, mock_offset):
        mock_offset.return_value = -1
        formatter = CSharpXmlFormatter()
        func_context = FunctionContextModel(
            qualified_name="TestClass.BadOffset",
            signature="void BadOffset()",
            parameters=[],
            start_line=1,
            docstring=DocstringModel(lines=[], start_line=0),
            return_type="void",
        )
        func_summary = DocstringTemplateModel(
            summary="Bad offset test.",
            return_description="None.",
            parameters=[],
            return_type="void",
        )
        with self.assertRaises(ValueError):
            formatter.get_formatted_docstring(
                file_path="test_file.cs",
                func_context=func_context,
                template_values=func_summary,
            )
