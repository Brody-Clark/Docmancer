from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.parameter_model import ParameterModel
from typing import List
import json


class Prompt:
    def __init__(self, function_context: FunctionContextModel):
        self._prompt_cls = self.create_prompt(function_context)

    def get(self) -> str:
        return self._prompt_cls

    def get_leading_comments_string(self, comments: List[str]) -> str:
        return ("\n").join(comments)

    def get_expected_json_format(self):

        model = FunctionSummaryModel(
            summary="A summary of what the function does based on its definition.",
            parameters=[
                ParameterModel(
                    name="parameter", type="type", desc="description of parameter"
                )
            ],
            return_description="A description of the return value if there is one",
        )
        return model.to_json(indent=2)

    def create_prompt(self, context: FunctionContextModel):
        return (
            f"\n\nFunction Signature: {context.signature}"
            f"\nPreceding Comments: {self.get_leading_comments_string(context.comments)}"
            f"\nQualified Name: {context.qualified_name}"
            f"\n\nFunction Body:"
            f"\n---"
            f"{context.body}"
            f"\n---"
            f"\n\nYour task:"
            f"\n- Summarize what the function does, optionally adding any remarks or example usage if they would be useful to developers calling the function such as rasied exceptions."
            f"\n- Describe what each parameter means in the context of the function if there are any. Ignore parameters if there are none."
            f"\n- Omit any unnecessary details if the code is not clear enough to draw conclusions from. Do not rely too heavily on function or variable names since they may be misleading."
            f"\n- Describe the return value if it has one"
            f"\n- Do not write an introduction or summary. Respond with only valid JSON and make sure it follows this format:"
            f"\n{self.get_expected_json_format()}"
        )
