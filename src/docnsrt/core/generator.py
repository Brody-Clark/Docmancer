"""This module provides function summary generators"""

from docnsrt.core.models import (
    DocstringTemplateModel,
    ExceptionModel,
    ParameterModel,
    FunctionContextModel,
)


class DocstringGenerator:
    """
    Generates placeholder values for docstrings based on function contexts.
    """

    def __init__(self):
        pass

    def get_template_values(
        self, context: FunctionContextModel
    ) -> DocstringTemplateModel:
        """Generates template values for a given function context."""
        return DocstringTemplateModel(
            summary="_summary_",
            return_description="_desc_",
            return_type=(
                "_type_" if context.return_type is None else context.return_type
            ),
            remarks="_remarks_",
            exceptions=[ExceptionModel(type="_type_", desc="_desc_")],
            parameters=[
                ParameterModel(name=p.name, type=p.type, desc="_desc_")
                for p in context.parameters
            ],
        )
