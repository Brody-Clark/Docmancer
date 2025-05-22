from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from docmancer.models.parameter_model import ParameterModel
from typing import List


@dataclass_json
@dataclass
class FunctionSummaryModel:
    summary: str
    return_description: str
    parameters: List[ParameterModel] = field(default_factory=list)
