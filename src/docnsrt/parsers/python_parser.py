"""Parser for Python code."""

import logging
from typing import List
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from docnsrt.core.models import ParameterModel, DocstringModel, FunctionContextModel
from docnsrt.parsers.parser_base import ParserBase

logger = logging.getLogger(__name__)


class PythonParser(ParserBase):
    """
    Parser for Python code.
    """

    def __init__(self):
        ParserBase.__init__(self)
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
        function_definition
            name: (identifier) @func.name
        )
        """

    def _get_list_splat_parameter(
        self, parameter_node: Node, source_code: str
    ) -> ParameterModel:
        name_node = self.get_first_child_of_type(parameter_node, "identifier")
        type_node = parameter_node.child_by_field_name("type")
        param_name = "*" + self.get_node_text(name_node, source_code)
        param_type = self.get_node_text(type_node, source_code) if type_node else "any"

        return ParameterModel(name=param_name, type=param_type, desc="")

    def _get_dictionary_splat_parameter(
        self, parameter_node: Node, source_code: str
    ) -> ParameterModel:
        name_node = self.get_first_child_of_type(parameter_node, "identifier")
        type_node = parameter_node.child_by_field_name("type")
        param_name = "**" + self.get_node_text(name_node, source_code)
        param_type = self.get_node_text(type_node, source_code) if type_node else "any"

        return ParameterModel(name=param_name, type=param_type, desc="")

    def _get_node_name_string(self, node: Node, source_code: str) -> str:
        name_node = node.child_by_field_name("name")
        return self.get_node_text(name_node, source_code) if name_node else ""

    def _get_node_type_string(self, node: Node, source_code: str) -> str:
        type_node = node.child_by_field_name("type")
        return self.get_node_text(type_node, source_code) if type_node else "any"

    def _get_parameters(self, parameters_node, source_code) -> List:
        """Extracts parameters from a function definition node.

        Args:
            parameters_node (tree_sitter.Node): The parameters node to extract information from.
            source_code (str): The source code as a string.

        Returns:
            List: A list of ParameterModel instances representing the function parameters.
        """
        parameters = []
        for child in parameters_node.children:
            if child.type in ["parameter", "identifier"]:
                param_name = self.get_node_text(child, source_code)
                if param_name != "self":
                    parameters.append(
                        ParameterModel(name=param_name, type="any", desc="")
                    )
                else:
                    parent = parameters_node.parent
                    while parent is not None:
                        if parent.type == "class_definition":
                            # Skip the 'self' parameter since it's a class method
                            break
                        elif parent.type == "module":
                            # Parameter is named 'self', but function is not within a class,
                            # so keep the parameter.
                            parameters.append(
                                ParameterModel(name=param_name, type="any", desc="")
                            )
                        parent = parent.parent
            elif child.type in ["typed_parameter", "typed_default_parameter"]:

                if child.children:
                    if child.children[0].type == "list_splat_pattern":
                        name_node = self.get_first_child_of_type(
                            child.children[0], "identifier"
                        )
                        param_name = "*" + self.get_node_text(name_node, source_code)
                        param_type = self._get_node_type_string(child, source_code)
                        parameters.append(
                            ParameterModel(name=param_name, type=param_type, desc="")
                        )
                    elif child.children[0].type == "dictionary_splat_pattern":
                        name_node = self.get_first_child_of_type(
                            child.children[0], "identifier"
                        )
                        param_name = "**" + self.get_node_text(name_node, source_code)
                        param_type = self._get_node_type_string(child, source_code)
                        parameters.append(
                            ParameterModel(name=param_name, type=param_type, desc="")
                        )
                    elif child.children[0].type == "identifier":
                        name_node = child.children[0]
                        param_name = (
                            self.get_node_text(name_node, source_code)
                            if name_node
                            else ""
                        )
                        param_type = self._get_node_type_string(child, source_code)
                        parameters.append(
                            ParameterModel(name=param_name, type=param_type, desc="")
                        )
            elif child.type == "list_splat_pattern":
                parameters.append(self._get_list_splat_parameter(child, source_code))
            elif child.type == "dictionary_splat_pattern":
                parameters.append(
                    self._get_dictionary_splat_parameter(child, source_code)
                )

        return parameters

    def _get_qualified_name(self, node, source_code: str) -> str:
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
            if parent.type == "class_definition":
                class_name_node = parent.child_by_field_name("name")
                class_name = self.get_node_text(
                    class_name_node, source_code=source_code
                )
                qualified_name = (
                    f"{class_name}.{qualified_name}" if qualified_name else class_name
                )
            elif parent.type == "module":
                # Module name is derived from file name or provided context
                break
            parent = parent.parent
        return qualified_name

    def _get_name(self, root_node, source_code: str) -> str:
        """Returns the name of the given node or empty string."""
        name_node = root_node.child_by_field_name("name")
        if not name_node:
            logger.error("Invalid name node")
            return ""
        name = self.get_node_text(name_node, source_code=source_code)
        return name

    def _get_docstring(self, block_node, source_code: str) -> DocstringModel:
        """Extracts a docstring model from a body node if it exists. Returns None if not."""
        first_stmt = block_node.child(0)
        if first_stmt and first_stmt.type == "expression_statement":
            expr = first_stmt.child(0)
            if expr and expr.type == "string":
                # Get the text slice from the original source
                comment = self.get_node_text(expr, source_code)
                return DocstringModel(
                    lines=comment.splitlines(), start_line=expr.start_point[0]
                )
        return None

    def _get_return_type(self, root_node, source_code: str) -> str | None:
        """Extract the return type annotation from a function_definition node.

        Handles common tree-sitter shapes: a child with field name "return_type",
        an explicit annotation node, or the node following a '->' punctuation.
        Returns the annotated type as a string or None when not present.
        """
        # Prefer a field named "return_type" if present
        try:
            rt = root_node.child_by_field_name("return_type")
            if rt:
                return self.get_node_text(rt, source_code)
        except Exception as e:
            logger.warning("Exception occurred during return type parsing: %s", e)

        # Look for annotation/typed node among children
        for child in root_node.children:
            if child.type in ("annotation", "type", "return_type"):
                return self.get_node_text(child, source_code)

        # Fallback: find a '->' token and take the next sibling as the return type
        for i, child in enumerate(root_node.children):
            # token text may be '->' represented as punctuation; compare the text
            try:
                txt = self.get_node_text(child, source_code)
            except Exception:
                txt = ""
            if txt == "->":
                if i + 1 < len(root_node.children):
                    return self.get_node_text(root_node.children[i + 1], source_code)

        return None

    def extract_function_context(
        self, root_node, source_code: str, module_name: str
    ) -> FunctionContextModel:
        """Extracts function context from a function definition node."""

        if root_node is None or root_node.type != "function_definition":
            raise ValueError("Provided root_node is not a function_definition node.")

        name = self._get_name(root_node, source_code)
        parameters_node = root_node.child_by_field_name("parameters")
        signature = (
            f"def {name}{self.get_node_text(parameters_node, source_code=source_code)}"
        )
        parameters = self._get_parameters(parameters_node, source_code)

        block_node = root_node.child_by_field_name("body")
        docstring = None
        if block_node:
            docstring = self._get_docstring(block_node, source_code)

        qualified_name = self._get_qualified_name(root_node, source_code)
        return_type = self._get_return_type(root_node, source_code)

        context = FunctionContextModel(
            qualified_name=f"{module_name}.{qualified_name}",
            parameters=parameters,
            signature=signature,
            docstring=docstring,
            start_line=root_node.start_point[0],
            return_type=return_type,
        )
        return context
