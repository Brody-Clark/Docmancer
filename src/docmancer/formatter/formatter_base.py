from abc import abstractmethod, ABC
from docmancer.models.documentation_model import DocumentationModel
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel


class FormatterBase(ABC):
    @abstractmethod
    def get_formatted_documentation(
        self,
        func_context: FunctionContextModel,
        func_summary: FunctionSummaryModel,
        file_path: str,
    ) -> DocumentationModel:
        """
        Creates a formatted documentation model that can be used to write a docstring into a source file.

        Args:
            doc_model: Generated documentation response model object

        Returns:
            A formatted Python docstring string.
        """
