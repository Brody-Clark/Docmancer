import docmancer.utils.json_utils as ju
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.parameter_model import ParameterModel
from docmancer.generators.prompts import Prompt
from abc import abstractmethod, ABC


class GeneratorBase(ABC):
    @abstractmethod
    def get_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:
        """Creates a function summary model based on function context

        Args:
            context (FunctionContextModel): Function context

        Returns:
            FunctionSummaryModel: Model containing information for docstring creation
        """


class DefaultGenerator(GeneratorBase):
    def __init__(self):
        pass

    def get_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:
        return FunctionSummaryModel(
            summary="_summary_",
            return_description="_returns_",
            parameters=[
                ParameterModel(name="_name_", type="_type_", desc="_description_")
            ],  # TODO: add parameters to FunctionContextModel and use here
        )


class LlmGenerator(GeneratorBase):
    def __init__(self, model: LlmAgentBase):
        self._agent = model
        self._prompt = Prompt()

    def get_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:

        # Prompt model and get response
        try:
            prompt_msg = self._prompt.create(context)
            response = self._agent.send_message(prompt_msg)
        except Exception as e:
            print(f"Generation failed: {e}")

        # Parse response into Function Summary Model
        try:
            func_summary_json = ju.extract_json_from_text(response)
            func_summary_model = FunctionSummaryModel.from_dict(func_summary_json)
            return func_summary_model
        except ValueError:
            print("ERROR")
            return None
