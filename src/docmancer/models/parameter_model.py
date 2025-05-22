from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class ParameterModel:
    name: str
    type: str
    desc: str
