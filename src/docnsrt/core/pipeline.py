"""
Main processing pipeline for documentation generation
"""

import logging
import os
from typing import List
import portalocker
from docnsrt.core.models import (
    WritableFileModel,
    DocstringPresentationModel,
    DocstringModel,
    FileProcessingContextModel,
    DocstringLocation,
)
from docnsrt.parsers.parser_base import ParserBase
from docnsrt.core.generator import DocstringGenerator
from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.core.presenter import Presenter, UserResponse
from docnsrt.config import DocnsrtConfig
from docnsrt.utils import file_utils
from docnsrt.core.languages import SupportedFileExtensions

logger = logging.getLogger(__name__)


class DocumentationPipeline:
    """
    Pipeline for processing documentation generation. Parses source code files,
    extracts function context, generates docstring template, and presents it to the user.
    """

    def __init__(
        self,
        generator: DocstringGenerator,
        parser: ParserBase,
        presenter: Presenter,
        formatter: FormatterBase,
    ):
        self._generator = generator
        self._parser = parser
        self._presenter = presenter
        self._formatter = formatter
        self._errors = []

    def run(self, settings: DocnsrtConfig):
        """
        Runs the documentation generation pipeline.
        Args:
            settings: Configuration settings for the documentation generation.
        Returns:
            None
        """

        # Parse all files/functions into {file_path: List[FunctionContextModel]} map
        files = file_utils.get_files_by_pattern(
            settings.project_dir,
            settings.files,
            settings.ignore_files,
            SupportedFileExtensions[settings.language],
        )
        file_contexts: List[FileProcessingContextModel] = []
        docstring_count = 0
        for f in files:
            file_context = self.get_file_context(f, settings)

            should_continue = True

            # Present the user with generated docs and get approval if "force-all" is not present
            if not settings.force_all:
                should_continue, file_context.docstrings = self.get_approved_docstrings(
                    file_context.docstrings
                )

            if not should_continue:
                logger.debug("Aborting the documentation process")
                file_contexts = []
                break

            if file_context.docstrings is not None and len(file_context.docstrings) > 0:
                file_contexts.append(file_context)
                docstring_count += len(file_context.docstrings)

        # If no docstrings to write, exit
        if not file_contexts:
            logger.debug("No docstrings to write, exiting")
            self._presenter.print_success("0/0 docstrings written successfully")
            return

        # Write formatted docstrings to files and save
        count_written = self.write_docstrings(self._errors, file_contexts)

        if len(self._errors) > 0:
            for e in self._errors:
                self._presenter.print_error(f"Error: {e}")
        self._presenter.print_success(
            f"{count_written}/{docstring_count} docstrings written successfully"
        )

    def get_file_context(
        self, file_path: str, settings: DocnsrtConfig
    ) -> FileProcessingContextModel:
        """
        Gets the file processing context for the specified file.
        Args:
            file_path: The path to the file.
            settings: Configuration settings for the documentation generation.
        Returns:
            A FileProcessingContextModel.
        """
        func_contexts = self._parser.parse(
            file_path, settings.functions, settings.ignore_functions
        )

        mtime, size = self.get_file_stats(file_path)
        f = WritableFileModel(
            file_path=file_path, last_time_modified=mtime, last_size_bytes=size
        )

        file_context = FileProcessingContextModel(
            file=f, functions=func_contexts, docstrings=[]
        )
        # Loop through function context and get formatted docs
        if not file_context.functions:
            return file_context
        for func_context in file_context.functions:

            # Generate summary for function context
            try:
                docstring_template_values = self._generator.get_template_values(
                    func_context
                )
            except Exception as e:
                self._errors.append(e)
                continue

            # Convert function summary to formatted summary
            formatted_docstring = self._formatter.get_formatted_docstring(
                file_path=file_context.file.file_path,
                func_context=func_context,
                template_values=docstring_template_values,
            )

            # Create documentation model database from function context and formatted summary
            doc = DocstringPresentationModel(
                new_docstring=DocstringModel(
                    lines=formatted_docstring.formatted_documentation,
                    start_line=formatted_docstring.start_line,
                ),
                qualified_name=func_context.qualified_name,
                signature=func_context.signature,
                offset_spaces=formatted_docstring.offset_spaces,
                file_path=file_context.file.file_path,
                existing_docstring=func_context.docstring,
                docstring_location=formatted_docstring.docstring_location,
            )

            file_context.docstrings.append(doc)
        return file_context

    def get_file_stats(self, file_path: str) -> tuple[float, int]:
        """
        Gets the file statistics for the specified file.
        Args:
            file_path: The path to the file.
        Returns:
            A tuple containing the last modification time and size of the file.
        """
        st = os.stat(file_path)
        return st.st_mtime, st.st_size

    def write_docstrings(
        self, errors, file_contexts: List[FileProcessingContextModel]
    ) -> int:
        """
        Writes the generated docstrings to the appropriate files.
        Args:
            errors: List to append any errors to.
            file_contexts: The list of file processing context models.
        Returns:
            The number of docstrings written.
        """
        count_written = 0
        for file_context in file_contexts:
            if len(file_context.docstrings) > 0:
                try:
                    self.commit(
                        file_path=file_context.file.file_path,
                        docs=file_context.docstrings,
                        orig_mtime=file_context.file.last_time_modified,
                        orig_size=file_context.file.last_size_bytes,
                    )
                    count_written += len(file_context.docstrings)
                except Exception as e:
                    errors.append(e)
        return count_written

    def get_approved_docstrings(
        self, docstring_models: List[DocstringPresentationModel]
    ) -> tuple[bool, FileProcessingContextModel]:
        """
        Gets user approval for the generated docstrings.
        Args:
            docstring_models: List of generated docstring models.
        Returns:
            A tuple containing a boolean indicating whether to continue and a list of approved docstring models.
        """
        approved_docs = []
        while docstring_models:
            doc = docstring_models.pop()
            approval_response = self._presenter.get_user_approval(doc)
            if not approval_response:
                logger.error("Failed to get response for docstring model")
                continue
            if approval_response.response == UserResponse.QUIT:
                return False, None
            if approval_response.response == UserResponse.SKIP:
                continue
            if approval_response.response == UserResponse.ACCEPT:
                approved_docs.append(doc)
        return True, approved_docs

    def commit(
        self,
        file_path: str,
        docs: List[DocstringPresentationModel],
        orig_mtime: float,
        orig_size: int,
    ):
        """
        Commits the generated documentation to the specified file.
        Args:
            file_path: The path to the file to write to.
            docs: The list of documentation models to write.
            orig_mtime: The original modification time of the file.
            orig_size: The original size of the file.
        Raises:
            RuntimeError: If the file has been modified externally since it was read.
        """

        logger.debug("Writing %i docstrings to file %s", len(docs), file_path)

        # Sort docs by start_line and write to files
        # Read the file into memory
        with open(file_path, "r+", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)

            # Detect external changes
            st = os.stat(file_path)
            if st.st_mtime != orig_mtime or st.st_size != orig_size:
                logger.error(
                    "File %s changed externally (mtime or size mismatch)", file_path
                )
                raise RuntimeError(f"File {file_path} changed externally")
            lines = f.readlines()

            # Sort insertions by line number (ascending)
            docs.sort(key=lambda x: x.new_docstring.start_line)

            offset = 0
            for doc in docs:

                adjusted_line = doc.new_docstring.start_line + offset

                # Remove existing docstring if there is one
                removed_lines = 0
                if doc.existing_docstring:
                    start_line = doc.existing_docstring.start_line + offset
                    end_line = start_line + len(doc.existing_docstring.lines)
                    del lines[start_line:end_line]
                    removed_lines = len(doc.existing_docstring.lines)

                # Write the docstring to the appropriate location
                indented_documentation = [
                    " " * doc.offset_spaces + doc_line
                    for doc_line in doc.new_docstring.lines
                ]
                logger.debug(
                    "Inserting docstring at line %i in file %s",
                    adjusted_line,
                    file_path,
                )

                # If docstring is above the function, adjust the line to insert at for removed lines
                if doc.docstring_location == DocstringLocation.ABOVE:
                    adjusted_line = max(0, adjusted_line - removed_lines)

                lines[adjusted_line:adjusted_line] = list(indented_documentation)

                offset += len(doc.new_docstring.lines) - removed_lines

            # Write the modified lines back to the file
            f.seek(0)
            f.truncate()
            f.writelines(lines)
        logger.info("Wrote %i docstrings to file %s", len(docs), file_path)
