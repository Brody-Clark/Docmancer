"""Parser for the C# language."""

from typing import List
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser
from docnsrt.parsers.parser_base import ParserBase
from docnsrt.core.models import ParameterModel, DocstringModel, FunctionContextModel


class CSharpParser(ParserBase):
    """Parser for C# code.

    Args:
        ParserBase (ParserBase): Base parser class.
    """

    def __init__(self):
        ParserBase.__init__(self)
        self._language = Language(tscsharp.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
            [
                (method_declaration
                    name: (identifier) @func.name
                )
                (local_function_statement
                    name: (identifier) @func.name
                )
            ]
        )
        """

    def get_enclosing_class_name(self, node, source_code):
        """Get the name of the class enclosing the given node.

        Args:
            node (tree_sitter.Node): The node to check.
            source_code (str): The source code being parsed.

        Returns:
            str: The name of the enclosing class, or None if not found.
        """
        parent = node.parent
        while parent is not None:
            if parent.type == "class_declaration":
                # The class name is usually an 'identifier' child of the class_declaration
                for child in parent.children:
                    if child.type == "identifier":
                        return source_code[child.start_byte : child.end_byte]
            parent = parent.parent
        return None

    def get_parameters(self, parameters_node, source_code) -> List[ParameterModel]:
        """Extract parameters from a parameter list node.

        Args:
            parameters_node (tree_sitter.Node): The start of the parameter tree
            source_code (str): The source code being parsed

        Returns:
            List[ParameterModel]: A list of extracted parameters
        """
        parameters = []
        for child in parameters_node.children:
            if child.type == "parameter":
                param_name = self.get_node_text(
                    child.child_by_field_name("name"), source_code
                )
                param_type = self.get_node_text(
                    child.child_by_field_name("type"), source_code
                )
                parameters.append(ParameterModel(name=param_name, type=param_type))
        return parameters

    def extract_function_context(
        self, root_node, source_code, module_name
    ) -> FunctionContextModel:

        return_type = None
        identifiers = []
        modifiers = []
        parameters_node = None
        for child_node in root_node.children:
            if child_node.type == "modifier":
                modifiers.append(
                    self.get_node_text(child_node, source_code=source_code)
                )
            elif child_node.type == "parameter_list":
                parameters_node = child_node
            elif child_node.type == "predefined_type":
                return_type = self.get_node_text(child_node, source_code=source_code)
            elif child_node.type == "identifier":
                identifier = self.get_node_text(child_node, source_code=source_code)

                # Custom return types are labeled as identifiers.
                if return_type is None:
                    return_type = identifier
                else:
                    identifiers.append(identifier)

        docstring = self.get_docstring(root_node, source_code)

        modifiers_str = " ".join(modifiers) if modifiers else ""
        identifiers_str = " ".join(identifiers) if identifiers else ""
        return_type = return_type if return_type is not None else ""
        parameters_str = (
            self.get_node_text(parameters_node, source_code=source_code)
            if parameters_node
            else ""
        )
        parameters = (
            self.get_parameters(parameters_node, source_code) if parameters_node else []
        )

        return FunctionContextModel(
            qualified_name=module_name
            + "."
            + self.get_qualified_name(root_node, source_code=source_code),
            signature=f"{modifiers_str} {return_type} {identifiers_str}{parameters_str}",
            parameters=parameters,
            docstring=docstring,
            start_line=root_node.range.start_point.row,
            return_type=return_type,
        )

    def get_docstring(self, node, source_code: str) -> DocstringModel:
        """Extracts the docstring from a method_declaration node.

        Args:
            node (tree_sitter.Node): The method_declaration node.
            source_code (str): The source code as a string.
        Returns:
            DocstringModel: The extracted docstring model, or None if not found.
        """
        # In C#, docstrings are XML comments preceding the method declaration
        # Look for preceding sibling nodes that are documentation comments
        docstring_lines = []
        start_line = node.start_point.row

        # Global functions have an extra parent node before accessing a comment node
        if node.type == "local_function_statement":
            current_node = node.parent.prev_sibling if node.parent else None
        else:
            current_node = node.prev_sibling

        if not current_node or current_node.type != "comment":
            return None

        comment_text = self.get_node_text(current_node, source_code=source_code)

        # Mulit-line comment blocks using /**/ are captured in a single node
        # with the newlines included
        if comment_text.startswith("/*"):
            for line in comment_text.splitlines():
                docstring_lines.append(line.strip())
        else:
            # Multi-line comments using // need to be found by walking upwards
            docstring_lines.insert(0, comment_text)
            prev_line = current_node.start_point.row
            current_node = current_node.prev_sibling
            while (
                current_node is not None
                and current_node.type == "comment"
                and current_node.start_point.row == prev_line - 1
            ):
                comment_text = self.get_node_text(current_node, source_code=source_code)

                docstring_lines.insert(0, comment_text)
                current_node = current_node.prev_sibling
                prev_line = prev_line - 1

        if docstring_lines:
            return DocstringModel(
                lines=docstring_lines, start_line=start_line - len(docstring_lines)
            )
        return None

    def get_qualified_name(self, node, source_code: str) -> str:
        """Get the qualified name of the function, including class and module names.

        Args:
            node (tree_sitter.Node): The function definition node.
            source_code (str): The source code as a string.
        Returns:

            str: The qualified name of the function.
        """
        qualified_name = self.get_node_text(
            node.child_by_field_name("name"), source_code=source_code
        )
        parent = node.parent
        while parent is not None:
            if parent.type == "class_declaration":
                class_name_node = parent.child_by_field_name("name")
                if not class_name_node:
                    continue
                class_name = self.get_node_text(
                    class_name_node, source_code=source_code
                )
                qualified_name = (
                    f"{class_name}.{qualified_name}" if qualified_name else class_name
                )
            parent = parent.parent
        return qualified_name
