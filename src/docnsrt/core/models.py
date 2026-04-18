"""
Data model definitions.
"""

from typing import List, Optional
from dataclasses import dataclass, field
import enum


class DocstringLocation(enum.Enum):
    """Enumeration for docstring locations."""

    INLINE = "inline"
    ABOVE = "above"
    BELOW = "below"


@dataclass(slots=True)
class ParameterModel:
    """Model for function parameters."""

    name: str = ""
    type: str = ""
    desc: Optional[str] = ""


@dataclass(slots=True)
class ExceptionModel:
    """Model for function exceptions."""

    type: str = ""
    desc: Optional[str] = ""


@dataclass(slots=True)
class DocstringModel:
    """Model for function docstrings."""

    lines: List[str]
    start_line: int


@dataclass(slots=True)
class FunctionContextModel:
    """Model for function context information."""

    qualified_name: str
    signature: str
    parameters: List[ParameterModel]
    docstring: DocstringModel
    start_line: int
    return_type: str | None


@dataclass(slots=True)
class WritableFileModel:
    """Model for writable file information."""

    file_path: str
    last_time_modified: Optional[float] = None
    last_size_bytes: Optional[int] = None


@dataclass(slots=True)
class DocstringPresentationModel:
    """Model for function writable documentation."""

    qualified_name: str  # Full function name. e.g., module.Class.method
    signature: str  # Full function signature
    new_docstring: Optional[DocstringModel] = (
        None  # New docstring to replace the existing one
    )
    offset_spaces: int = 0  # Number of spaces to offset formatted_documentation
    file_path: Optional[str] = None  # Relative file path
    existing_docstring: Optional[DocstringModel] = None  # If present
    docstring_location: DocstringLocation = (
        DocstringLocation.INLINE
    )  # Location of the docstring


@dataclass(slots=True)
class FileProcessingContextModel:
    """Model for capturing docstring data that is needed to write to a file"""

    file: WritableFileModel
    functions: list[FunctionContextModel]
    docstrings: list[DocstringPresentationModel]


@dataclass(slots=True)
class DocstringTemplateModel:
    """Model for docstring template values."""

    summary: str
    return_description: Optional[str] = None
    parameters: List[ParameterModel] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: List[ExceptionModel] = field(default_factory=list)
    remarks: Optional[str] = None


@dataclass(slots=True)
class FormattedDocstringModel:
    """Model representing a formatted docstring."""

    start_line: int  # Start line of documentation
    formatted_documentation: List[str]  # Formatted doc string lines
    offset_spaces: int = 0  # Number of spaces to offset formatted_documentation
    docstring_location: DocstringLocation = (
        DocstringLocation.INLINE
    )  # Location of the docstring
