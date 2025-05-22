from typing import List
from docmancer.parser.base_parser import BaseParser
from docmancer.generator.llm.llm_agent_factory import LLMAgentFactory
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.generator.documentation_generator import DocumentationGenerator
from docmancer.formatter.formatter_base import FormatterBase
from docmancer.core.presenter import Presenter, UserResponse
from docmancer.models.documentation_model import DocumentationModel
from docmancer.config import DocmancerConfig
import docmancer.utils.file_utils as file_utils


class DocumentationBuilderEngine:
    def __init__(
        self,
        generator: DocumentationGenerator,
        parser: BaseParser,
        presenter: Presenter,
        formatter: FormatterBase,
    ):
        self._generator = generator
        self._parser = parser
        self._presenter = presenter
        self._formatter = formatter

    def run(self, settings: DocmancerConfig):
        errors = []

        # Step 1. parse all files/functions into {file_path: List[function]} map
        file_contexts = {}
        for file_pattern in settings.files:
            files = file_utils.get_files_by_pattern(file_pattern)
            for f in files:
                func_contexts = self._parser.parse(f, settings.functions)
                file_contexts[f] = func_contexts

        # TODO: implement display message for all function context models that dont
        # have existing docstrings. Make sure existing docstrings are parsed depending on language and style(?)
        # if settings.check:
        #     self._presenter.display_message()

        # Loop through function context and get formatted docs
        doc_model_database = {}
        for file_path, func_contexts in file_contexts.items():
            for func_context in func_contexts:

                # Step 2. Convert function contexts to Documention Models
                try:
                    if settings.no_summary:
                        summary = self._generator.get_default_summary(func_context[0])
                    else:
                        summary = self._generator.generate_summary(func_context[0])
                except Exception as e:
                    errors.append(e)
                    continue

                # Step 3. Convert function summary to formatted documentation
                doc = self._formatter.get_formatted_documentation(
                    func_context=func_context[0],
                    func_summary=summary,
                    file_path=file_path,
                )

                if file_path in doc_model_database:
                    doc_model_database[file_path].append(doc)
                else:
                    doc_model_database[file_path] = [doc]

        # Step 4. Present the user with generated docs and get approval if "force" is not present
        if not settings.force_all:
            for file_path, doc_models in doc_model_database.copy().items():
                approved_docs = []
                while doc_models:
                    doc = doc_models.pop()
                    approval_response = self._presenter.get_user_approval(doc)
                    if approval_response.response == UserResponse.QUIT:
                        return
                    if approval_response.response == UserResponse.SKIP:
                        continue
                    if approval_response.response == UserResponse.ACCEPT:
                        approved_docs.append(doc)
                doc_model_database[file_path] = approved_docs

        # Step 5. Commit formatted docs to files and save
        for file_path, doc_models in doc_model_database.items():
            if len(doc_models) > 0:
                try:
                    self.commit(file_path=file_path, docs=doc_models)
                except Exception as e:
                    errors.append(e)

        # TODO: Implement better error notification system
        if len(errors) > 0:
            for e in errors:
                self._presenter.print_error(f"Error: {e}")
        else:
            self._presenter.clear_console()
            self._presenter.print_success("Documentation Generation Complete")

    def commit(self, file_path: str, docs: List[DocumentationModel]):

        # Sort docs by start_line and write to files
        # Read the file into memory
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Sort insertions by line number (ascending)
        docs.sort(key=lambda x: x.start_line)

        offset = 0
        for doc in docs:
            adjusted_line = doc.start_line + offset
            indented_documentation = [
                " " * doc.offset_spaces + doc_line
                for doc_line in doc.formatted_documentation
            ]
            lines[adjusted_line:adjusted_line] = [
                line for line in indented_documentation
            ]

            offset += len(doc.formatted_documentation)

        # Write modified lines back to file
        with open(file_path, "w") as f:
            f.writelines(lines)
