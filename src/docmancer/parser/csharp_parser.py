from typing import List
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser
from docmancer.parser.parser_base import ParserBase
from docmancer.models.function_context import FunctionContextModel


class CSharpParser(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)
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

        function_contexts = []
        node_stack = [(root_node, [])]  # (node, scope_stack)

        while node_stack:
            node, scope = node_stack.pop()

            if node.type == "method_declaration":
                modifiers = []
                return_type = None
                identifiers = []
                parameters_node = None
                body = None
                for child_node in node.children:
                    if child_node.type == "identifier":
                        identifiers.append(
                            self.get_node_text(child_node, source_code=source_code)
                        )
                    elif child_node.type == "modifier":
                        modifiers.append(
                            self.get_node_text(child_node, source_code=source_code)
                        )
                    elif child_node.type == "predefined_type":
                        return_type = self.get_node_text(
                            child_node, source_code=source_code
                        )
                    elif child_node.type == "parameter_list":
                        parameters_node = child_node
                    elif child_node.type == "block":
                        body = self.get_node_text(child_node, source_code=source_code)

                comments = None
                prev_sibling = node.prev_sibling
                if prev_sibling is not None and prev_sibling.type == "comment":
                    comments = self.get_node_text(prev_sibling, source_code=source_code)

                modifiers_str = " ".join(modifiers)
                identifiers_str = " ".join(identifiers)
                return_type = f" {return_type} " if return_type is not None else ""
                signature = f"{modifiers_str}{return_type}{identifiers_str}{self.get_node_text(parameters_node, source_code=source_code)}"

                function_contexts.append(
                    FunctionContextModel(
                        qualified_name="",
                        signature=signature,
                        body=body,
                        comments=comments,
                        start_line=node.range.start_point.row,
                        end_line=node.range.end_point.row,
                    )
                )

            else:
                for child in reversed(node.children):
                    node_stack.append((child, scope))
