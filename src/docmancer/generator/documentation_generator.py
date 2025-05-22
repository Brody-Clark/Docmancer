import docmancer.utils.json_utils as ju
from docmancer.generator.llm.llm_agent_base import LLMAgent
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.parameter_model import ParameterModel
from docmancer.generator.prompts import Prompt


class DocumentationGenerator:
    def __init__(self, model: LLMAgent, language: str):
        self._quality = 1
        self._agent = model

    def get_default_summary(
        self, context: FunctionContextModel
    ) -> FunctionSummaryModel:
        return FunctionSummaryModel(
            summary="_summary_",
            return_description="_returns_",
            parameters=[
                ParameterModel(name="_name_", type="_type_", desc="_description_")
            ],  # TODO: add parameters to FunctionContextModel and use here
        )

    def generate_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:

        # TODO: handle quality here
        # Step 1. create prompt for model
        prompt = Prompt(context)

        # Step 2. Prompt model and get response
        try:
            prompt_msg = prompt.get()
            response = self._agent.send_message(prompt_msg)
        except Exception as e:
            print(f"Generation failed: {e}")

        # Step 3. Parse response into Function Summary Model
        try:
            func_summary_json = ju.extract_json_from_text(response)
            func_summary_model = FunctionSummaryModel.from_dict(func_summary_json)
            return func_summary_model
        except ValueError:
            print("ERROR")
            return None
