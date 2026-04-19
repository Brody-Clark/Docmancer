"""
Formatter factory for creating formatter instances.
"""

from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.formatter.python_formatters import PythonPepFormatter, PythonNumpyFormatter
from docnsrt.formatter.csharp_formatters import CSharpXmlFormatter
from docnsrt.core.styles import DocstringStyle
from docnsrt.core.languages import Languages


class FormatterFactory:
    """
    Factory class for creating formatters.
    """

    def get_formatter(self, style: str, language: str) -> FormatterBase:
        """
        Returns a formatter instance based on the specified style and language.

        Args:
            style (str): The docstring style to use.
            language (str): The programming language of the code.

        Returns:
            FormatterBase: An instance of a formatter for the specified style and language.
        """
        if not style or not language:
            raise ValueError("Both style and language must be specified.")

        if style == DocstringStyle.CUSTOM.value:
            raise NotImplementedError("Custom style is not implemented yet.")
        if language == Languages.PYTHON.value:
            if style.lower() == DocstringStyle.PEP.lower():
                return PythonPepFormatter()
            if style.lower() == DocstringStyle.NUMPY.lower():
                return PythonNumpyFormatter()
        if language == Languages.CSHARP.value:
            if style.lower() == DocstringStyle.XML.lower():
                return CSharpXmlFormatter()
        if language == Languages.JAVA.value:
                pass
        raise ValueError(f"Unsupported style '{style}' for language '{language}'")
