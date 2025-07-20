from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass_json
@dataclass
class ParameterModel:
    name: str
    type: str
    desc: str


@dataclass_json
@dataclass
class ExceptionModel:
    type: str
    desc: str


@dataclass_json
@dataclass
class FunctionSummaryModel:
    summary: str
    return_description: str
    parameters: List[ParameterModel] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: List[ExceptionModel] = field(default_factory=list)
    remarks: Optional[str] = None
