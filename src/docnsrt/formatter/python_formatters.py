"""Formatters for Python code."""

from typing import List
from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.core.models import (
    DocstringLocation,
    FormattedDocstringModel,
    DocstringTemplateModel,
    FunctionContextModel,
)
import docnsrt.utils.file_utils as fu

INDENT_SPACES = 4
TAB = "    "


def _get_docstring_model(
    lines: List[str], func_context: FunctionContextModel, file_path: str
) -> FormattedDocstringModel:

    function_signature_offset = fu.get_line_text_offset_spaces(
        file_path, func_context.start_line
    )

    if function_signature_offset >= 0:
        offset = function_signature_offset + INDENT_SPACES
    else:
        raise ValueError(
            f"Unable to read start line {func_context.start_line} from file {file_path}"
        )

    return FormattedDocstringModel(
        formatted_documentation=lines,
        start_line=func_context.start_line
        + 1,  # Python docstrings go right below the signature
        offset_spaces=offset,
        docstring_location=DocstringLocation.BELOW,
    )


class PythonPepFormatter(FormatterBase):
    """
    Formats Python docstrings according to PEP 257.
    """

    def get_formatted_docstring(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        template_values: DocstringTemplateModel,
    ) -> FormattedDocstringModel:

        lines = ['"""', template_values.summary, ""]

        if template_values.parameters:
            lines.append("Args:")
            for param in template_values.parameters:
                lines.append(f"{TAB}{param.name} ({param.type}): {param.desc}")

        if template_values.return_description:
            lines.append("")
            lines.append("Returns:")
            lines.append(
                f"{TAB}{template_values.return_type}: {template_values.return_description}"
            )

        lines.append('"""')

        lines = [line + "\n" for line in lines]

        return _get_docstring_model(lines, func_context, file_path)


class PythonNumpyFormatter(FormatterBase):
    """
    Formats Python docstrings according to Numpy.
    """

    def get_formatted_docstring(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        template_values: DocstringTemplateModel,
    ) -> FormattedDocstringModel:

        lines = ['"""', template_values.summary, ""]

        lines.append("Parameters")
        lines.append("----------")

        if template_values.parameters:
            for param in template_values.parameters:
                lines.append(f"{param.name} : ({param.type})")
                lines.append(f"{TAB}{param.desc}")
        lines.append("")

        if template_values.return_description:
            lines.append("Returns")
            lines.append("-------")
            if template_values.return_type:
                lines.append(template_values.return_type)
            lines.append(f"{TAB}{template_values.return_description}")
            lines.append("")

        lines.append("Examples")
        lines.append("--------")
        lines.append("")
        lines.append('"""')

        lines = [line + "\n" for line in lines]

        return _get_docstring_model(lines, func_context, file_path)
