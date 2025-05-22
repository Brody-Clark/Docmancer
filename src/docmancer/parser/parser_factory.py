from docmancer.parser.base_parser import BaseParser
from docmancer.parser.python_parser import PythonParser


class ParserFactory:

    def get_parser(self, language: str) -> BaseParser:
        if language == "python":
            return PythonParser()
        else:
            return None
