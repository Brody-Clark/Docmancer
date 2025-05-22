import tree_sitter_python as tspython
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser
from docmancer.parser.base_parser import BaseParser
from docmancer.models.function_context import FunctionContextModel
import docmancer.utils.file_utils as fu
from typing import List
import os
from pathlib import Path
import fnmatch


class PythonParser(BaseParser):
    def __init__(self):
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)

    def get_function_nodes(self, tree, source_code: bytes):
        query_str = """
        (
        function_definition
            name: (identifier) @func.name
        )
        """
        query = self._language.query(query_str)

        captures = query.captures(tree.root_node)
        return captures

    def get_function_names(self, captures, source_code: bytes) -> dict:
        func_nodes = {}
        for capture_name in captures:
            if capture_name == "func.name":
                for node in captures[capture_name]:
                    func_name = source_code[node.start_byte : node.end_byte].decode(
                        "utf-8"
                    )
                    func_nodes[node] = func_name
        return func_nodes

    def get_functions_by_name_pattern(
        self, tree, source_code: bytes, glob_pattern: str
    ) -> List[any]:
        captures = self.get_function_nodes(tree, source_code)
        matches = []
        for node, func_name in self.get_function_names(
            captures=captures, source_code=source_code
        ).items():
            if fnmatch.fnmatch(func_name, glob_pattern):
                matches.append(node.parent)  # node.parent is the full function node

        return matches

    def parse(
        self, file: str, function_patterns: List[str]
    ) -> List[FunctionContextModel]:
        # Parse all files and filter out function nodes based on filter glob patterns
        functions = {}
        function_nodes = set()
        try:
            code = fu.read_file_to_bytes(file.absolute())
            module_name = os.path.splitext(os.path.basename(file.absolute()))[0]
        except:
            # TODO: log error
            return None
        tree = self._parser.parse(code)
        for func_glob in function_patterns:
            nodes = self.get_functions_by_name_pattern(tree, code, func_glob)
            function_nodes.update(nodes)
        functions[module_name] = function_nodes

        # Parse each function root node and create function contexts
        function_contexts = []
        for name, function_nodes in functions.items():
            for node in function_nodes:
                function_contexts.append(
                    self.extract_function_contexts(node, code, name)
                )

        return function_contexts

    def get_node_text(self, node, source_code) -> str:
        return source_code[node.start_byte : node.end_byte].decode("utf-8")

    def extract_function_contexts(self, root_node, source_code: str, module_name):
        lines = source_code.splitlines()

        contexts = []
        node_stack = [(root_node, [])]  # Each item: (node, scope_stack)

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
