from typing import List
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser
from docmancer.parser.base_parser import BaseParser
from docmancer.models.function_context import FunctionContextModel


class CSharpParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self._language = Language(tscsharp.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
        method_declaration
            name: (identifier) @func.name
        )
        """

    def extract_function_contexts(
        self, root_node, source_code, module_name
    ) -> List[FunctionContextModel]:
        lines = source_code.splitlines()

        contexts = []
        node_stack = [(root_node, [])]  # (node, scope_stack)

        while node_stack:
            node, scope = node_stack.pop()

            if node.type == "method_declaration":
                name_node = node.child_by_field_name("identifier")
                name = self.get_node_text(name_node, source_code=source_code)

                parameters_node = node.child_by_field_name("parameter_list")
                signature = f"FUNC {name}{self.get_node_text(parameters_node, source_code=source_code)}"

            else:
                for child in reversed(node.children):
                    node_stack.append((child, scope))
