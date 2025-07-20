from typing import Dict, List, Any
from enum import Enum


class DocstringStyle(Enum):
    """
    Enum representing the supported documentation styles.
    The value of each enum member is its canonical string representation.
    """

    PEP = "PEP"
    DOXYGEN = "doxygen"
    NUMPY = "numpy"
    BASIC = "basic"
    CUSTOM = "custom"
    XML = "xml"

    def lower(self) -> str:
        return self.value.lower()


STYLE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    DocstringStyle.GOOGLE.value: {
        "description": "Google Style Guide docstring format."
    },
    DocstringStyle.PEP.value: {
        "description": "PEP 257 docstring conventions (often reStructuredText-like)."
    },
    DocstringStyle.DOXYGEN.value: {
        "description": "Doxygen-compatible docstring format (common in C++/Java, adaptable to Python)."
    },
    DocstringStyle.BASIC.value: {"description": "Unformatted comment style."},
    DocstringStyle.NUMPY.value: {"description": "NumPy/SciPy style docstring format."},
    DocstringStyle.CUSTOM.value: {
        "description": "User-defined style docstring format."
    },
    DocstringStyle.XML.value: {"description": "Formatting with tags in xml format."},
}

CANONICAL_STYLE_NAMES: List[str] = [style.value for style in DocstringStyle]
LOWERCASE_STYLE_NAMES: List[str] = [style.lower() for style in DocstringStyle]

DEFAULT_STYLE_ENUM = DocstringStyle.BASIC
DEFAULT_STYLE_NAME = DEFAULT_STYLE_ENUM.value
