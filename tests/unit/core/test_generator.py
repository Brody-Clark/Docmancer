from docnsrt.core.generator import DocstringGenerator
from docnsrt.core.models import (
    FunctionContextModel,
    ParameterModel,
    DocstringModel,
    ExceptionModel,
)


def test_get_template_values_returns_correct_defaults():
    param_1 = ParameterModel(name="p1", type="t1", desc="d1")
    param_2 = ParameterModel(name="p2", type="t2", desc="d2")

    docstring = DocstringModel(lines=["l1", "l2"], start_line=12)

    fcm = FunctionContextModel(
        qualified_name="name",
        signature="def func()",
        parameters=[param_1, param_2],
        docstring=docstring,
        start_line=10,
        return_type="str",
    )
    generator = DocstringGenerator()
    template = generator.get_template_values(fcm)

    assert template.exceptions == [ExceptionModel(type="_type_", desc="_desc_")]
    assert template.parameters == [
        ParameterModel(name=p.name, type=p.type, desc="_desc_") for p in fcm.parameters
    ]
    assert template.return_description == "_desc_"
    assert template.summary == "_summary_"
    assert template.remarks == "_remarks_"
    assert template.return_type == "str"
