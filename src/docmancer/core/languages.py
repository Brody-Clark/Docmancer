from typing import List
from enum import Enum


class Languages(Enum):
    """
    Enum representing the supported documentation languages
    """

    PYTHON = "python"
    CSHARP = "csharp"

    def lower(self) -> str:
        return self.value.lower()


CANONICAL_LANGUAGE_NAMES: List[str] = [lang.value for lang in Languages]
LOWERCASE_LANGUAGES_NAMES: List[str] = [lang.lower() for lang in Languages]
