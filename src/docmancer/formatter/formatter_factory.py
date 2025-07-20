from docmancer.formatter.formatter_base import FormatterBase
from docmancer.formatter.python_formatters import pythonPepFormatter
from docmancer.formatter.csharp_formatters import csharpXmlFormatter
from docmancer.core.styles import DocstringStyle
from docmancer.core.languages import Languages


class FormatterFactory:
    def __init__(self):
        pass

    def get_formatter(self, style: str, language: str) -> FormatterBase:
        if language == Languages.PYTHON.value:
            if style.lower() == DocstringStyle.PEP.lower():
                return pythonPepFormatter()
        if language == Languages.CSHARP.value:
            if style.lower == DocstringStyle.XML.lower():
                return csharpXmlFormatter()
        return None
