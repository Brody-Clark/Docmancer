from abc import ABC, abstractmethod
from typing import List
from docmancer.models.function_context import FunctionContextModel


class BaseParser(ABC):
    @abstractmethod
    def parse(
        self, file: str, function_patterns: List[str]
    ) -> List[FunctionContextModel]:
        pass
