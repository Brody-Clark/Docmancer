from typing import List
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from docmancer.parser.base_parser import BaseParser
from docmancer.models.function_context import FunctionContextModel


class PythonParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
        function_definition
            name: (identifier) @func.name
        )
        """

    def extract_function_contexts(
        self, root_node, source_code: str, module_name
    ) -> List[FunctionContextModel]:
        lines = source_code.splitlines()

        contexts = []
        node_stack = [(root_node, [])]  # (node, scope_stack)

        while node_stack:
            node, scope = node_stack.pop()

            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                name = self.get_node_text(name_node, source_code=source_code)
                new_scope = scope + [name]
                qualified_name = ".".join([module_name] + new_scope)

                parameters_node = node.child_by_field_name("parameters")
                signature = f"def {name}{self.get_node_text(parameters_node, source_code=source_code)}"

                block_node = node.child_by_field_name("body")
                body = self.get_node_text(block_node, source_code=source_code)

                # Gather comments above the function
                start_line = node.start_point[0]
                comment_lines = []
                for i in range(start_line - 1, -1, -1):
                    line = lines[i].strip()
                    if line.startswith(b"#"):
                        comment_lines.insert(0, line.decode("utf8"))
                    elif line == "":
                        continue
                    else:
                        break

                context = FunctionContextModel(
                    qualified_name=qualified_name,
                    signature=signature,
                    body=body,
                    comments="\n".join(comment_lines),
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
                contexts.append(context)

                # Add block contents to stack with updated scope
                for child in reversed(node.children):
                    if child.type == "block":
                        node_stack.append((child, new_scope))

            elif node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                class_name = self.get_node_text(name_node, source_code=source_code)
                new_scope = scope + [class_name]
                for child in reversed(node.children):
                    if child.type == "block":
                        node_stack.append((child, new_scope))

            else:
                # Add children to stack (depth-first traversal)
                for child in reversed(node.children):
                    node_stack.append((child, scope))

        return contexts
