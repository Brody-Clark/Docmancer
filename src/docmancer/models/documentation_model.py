from dataclasses import dataclass
import json
from typing import List, Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DocumentationModel:
    start_line: int  # Start line of documentation
    qualified_name: str  # Full function name. e.g., module.Class.method
    signature: str  # Full function signature
    formatted_documentation: List[str]  # Formatted doc string lines
    offset_spaces: int = 0  # Number of spaces to offset formatted_documentation
    file_path: Optional[str] = None  # Relative file path
    existing_docstring: Optional[str] = None  # If present
