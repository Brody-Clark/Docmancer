from docmancer.models.function_context import FunctionContextModel
from docmancer.models.functional_models import (
    ParameterModel,
    ExceptionModel,
    FunctionSummaryModel,
)
from typing import List
import yaml
from pathlib import Path


class Prompt:
    def __init__(self):
        self._prompt_template = self._load_prompt_template()

    def create(self, context: FunctionContextModel) -> str:
        # At runtime, inject values
        prompt = self._prompt_template.format(
            signature=context.signature,
            preceding_comments=self._get_leading_comments_str(context.comments),
            qualified_name=context.qualified_name,
            body=context.body,
            expected_json_format=self._get_expected_json_format(),
        )

        return prompt

    def _get_leading_comments_str(self, comments: List[str]) -> str:
        return ("\n").join(comments)

    def _get_expected_json_format(self):

        model = FunctionSummaryModel(
            summary="A summary of what the function does based on its definition.",
            parameters=[
                ParameterModel(
                    name="parameter", type="type", desc="description of parameter"
                )
            ],
            return_description="A description of the return value if there is one.",
            remarks="A remark about usage if necessary.",
            exceptions=[ExceptionModel(type="type", desc="description of exception")],
        )
        return model.to_json(indent=2)

    def _load_prompt_template(self) -> str:
        # Load config
        try:
            with open(Path("prompt.yaml")) as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            print("No valid prompt.yaml file found for LLM.")

        prompt_template = config["prompt_template"]
        return prompt_template
