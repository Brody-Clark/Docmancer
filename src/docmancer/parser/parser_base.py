from abc import ABC, abstractmethod
from typing import List
import os
import fnmatch
import docmancer.utils.file_utils as fu
from docmancer.models.function_context import FunctionContextModel


class ParserBase(ABC):
    def __init__(self):
        self._language = None
        self._parser = None
        self._query_str = None

    def get_function_nodes(self, tree):
        query = self._language.query(self._query_str)
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

    def filter_functions(
        self,
        tree,
        source_code: bytes,
        include_pattern: List[str],
        ignore_patterns: List[str],
    ) -> List[any]:
        """Locates functions from source code based on include/ignore filters.

        Args:
            tree (Tree): tree-sitter tree
            source_code (bytes): raw source code as bytes
            include_pattern (List[str]): list of glob patterns to filter in
            ignore_patterns (List[str]): list of glob patterns to filter out

        Returns:
            List[any]: List of function nodes that pass the filters
        """
        captures = self.get_function_nodes(tree)
        matches = []
        func_nodes = self.get_function_names(
            captures=captures, source_code=source_code
        ).items()
        for node, func_name in func_nodes:
            # skip functions that dont match any include patterns
            if not any(
                fnmatch.fnmatch(func_name, pattern) for pattern in include_pattern
            ):
                continue

            # skip functions that match any ignore patterns
            if any(fnmatch.fnmatch(func_name, pattern) for pattern in ignore_patterns):
                continue

            matches.append(node.parent)  # node.parent is the full function node

        return matches

    def parse(
        self, file: str, include_patterns: List[str], ignore_patterns: List[str]
    ) -> List[FunctionContextModel]:
        try:
            code = fu.read_file_to_bytes(file.absolute())
            module_name = os.path.splitext(os.path.basename(file.absolute()))[0]
        except OSError as e:
            print(e)
            return None
        tree = self._parser.parse(code)
        nodes = self.filter_functions(tree, code, include_patterns, ignore_patterns)
        function_nodes = set()
        function_nodes.update(nodes)
        functions = {}
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

    @abstractmethod
    def extract_function_contexts(
        self, root_node, source_code: str, module_name
    ) -> List[FunctionContextModel]:
        pass
