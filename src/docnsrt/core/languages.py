"""Supported programming languages."""

from typing import List
from enum import Enum


class Languages(Enum):
    """
    Enum representing the supported documentation languages
    """

    PYTHON = "python"
    CSHARP = "csharp"
    JAVA = "java"

    def lower(self) -> str:
        """
        Returns the lowercase version of the language name.
        """
        return self.value.lower()


CANONICAL_LANGUAGE_NAMES: List[str] = [lang.value for lang in Languages]
LOWERCASE_LANGUAGES_NAMES: List[str] = [lang.lower() for lang in Languages]

SupportedFileExtensions: dict = {
    Languages.PYTHON.value: [".py"],
    Languages.CSHARP.value: [".cs"],
}
