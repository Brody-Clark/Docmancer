import pytest
from unittest.mock import patch, MagicMock
from docmancer.generators.llm.prompt import Prompt
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel


@pytest.fixture
def mock_prompt_template():
    return (
        "Function Signature: {signature}\n"
        "Comments: {preceding_comments}\n"
        "Qualified Name: {qualified_name}\n"
        "Body:\n{body}\n"
        "Format:\n{expected_json_format}"
    )

@pytest.fixture
def mock_context():
    return FunctionContextModel(
        qualified_name="module.func",
        signature="def func(x, y):",
        body="    return x + y",
        start_line=1,
        end_line=3,
        comments=["# comment1", "# comment2"],
    )


@patch("docmancer.generators.prompts.Prompt._load_prompt_template")
def test_create_prompt_injects_values(
    mock_load_template: MagicMock,
    mock_prompt_template: MagicMock,
    mock_context: MagicMock,
):
    mock_load_template.return_value = mock_prompt_template
    prompt = Prompt()
    result = prompt.create(mock_context)
    assert "def func(x, y):" in result
    assert "module.func" in result
    assert "# comment1\n# comment2" in result
    assert "return x + y" in result
    assert "summary" in result  # from expected_json_format


@patch("docmancer.generators.prompts.Prompt._load_prompt_template")
def test_get_leading_comments_str_joins_lines(
    mock_load_template: MagicMock, mock_prompt_template: MagicMock
):
    mock_load_template.return_value = mock_prompt_template
    prompt = Prompt()
    comments = ["# first", "# second"]
    result = prompt.get_leading_comments_str(comments)
    assert result == "# first\n# second"


@patch("docmancer.generators.prompts.Prompt._load_prompt_template")
def test_get_expected_json_format_returns_json(
    mock_load_template: MagicMock, mock_prompt_template: MagicMock
):
    mock_load_template.return_value = mock_prompt_template
    prompt = Prompt()
    json_str = prompt.get_expected_json_format()
    assert "summary" in json_str
    assert "parameters" in json_str
    assert "return_description" in json_str
    assert "remarks" in json_str
    assert "exceptions" in json_str

    summary_model: FunctionSummaryModel = FunctionSummaryModel.from_json(json_str)

    assert summary_model is not None
