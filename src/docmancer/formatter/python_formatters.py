from docmancer.models.documentation_model import DocumentationModel
from docmancer.formatter.formatter_base import FormatterBase
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
import docmancer.utils.file_utils as fu

INDENT_SPACES = 4


class pythonPepFormatter(FormatterBase):

    def get_formatted_documentation(
        self,
        func_context: FunctionContextModel,
        func_summary: FunctionSummaryModel,
        file_path: str,
    ) -> DocumentationModel:

        function_signature_offset = fu.get_line_text_offset_spaces(
            file_path, func_context.start_line
        )

        lines = ['"""', func_summary.summary.strip(), ""]

        if func_summary.parameters:
            lines.append("Args:")
            for param in func_summary.parameters:
                name = param.name
                typ = param.type if param.type is not None else "Any"
                desc = param.desc
                lines.append(f"    {name} ({typ}): {desc}")

        if func_summary.return_description:
            lines.append("")
            lines.append("Returns:")
            lines.append(f"    {func_summary.return_description.strip()}")

        lines.append('"""')

        # add newlines to each line
        lines = [line + "\n" for line in lines]

        if function_signature_offset >= 0:
            offset = function_signature_offset + INDENT_SPACES
        else:
            raise ValueError(
                f"Unable to read start line {func_context.start_line} from file {file_path}"
            )

        doc_model = DocumentationModel(
            qualified_name=func_context.qualified_name,
            formatted_documentation=lines,
            signature=func_context.signature,
            start_line=func_context.start_line,  # pep doc strings go right below the signature
            file_path=file_path,
            existing_docstring=func_context.comments,
            offset_spaces=offset,
        )

        return doc_model
