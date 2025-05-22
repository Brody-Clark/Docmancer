from docmancer.formatter.formatter_base import FormatterBase
from docmancer.formatter.py_docstring_formatter import PyDocstringFormatter
from docmancer.core.styles import DocstringStyle
from docmancer.core.languages import Languages


class FormatterFactory:
    def __init__(self):
        pass

    def get_formatter(self, style: str, language: str) -> FormatterBase:
        if language == Languages.PYTHON.value:
            if style == DocstringStyle.PEP.value:
                return PyDocstringFormatter()
