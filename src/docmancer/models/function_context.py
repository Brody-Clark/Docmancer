from dataclasses import dataclass
from typing import List


@dataclass
class FunctionContextModel:
    qualified_name: str
    signature: str
    body: str
    comments: List[str]
    start_line: int
    end_line: int
