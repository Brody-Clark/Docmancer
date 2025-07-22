from docmancer.parser.parser_base import ParserBase
from docmancer.parser.python_parser import PythonParser
from docmancer.parser.csharp_parser import CSharpParser


class ParserFactory:

    def get_parser(self, language: str) -> ParserBase:
        if language == "python":
            return PythonParser()
        if language == "csharp":
            return CSharpParser()
        else:
            return None
