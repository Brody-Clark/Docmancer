from docmancer.config import LLMConfig, LLMType
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.generators.llm.local_agent import LlamaCppAgent


class LlmFactory:

    def get_agent(self, llm_config: LLMConfig) -> LlmAgentBase:
        if llm_config.get_mode_enum() == LLMType.LOCAL:
            return LlamaCppAgent(llm_config.local)
        else:
            raise NotImplementedError(f"{llm_config.model_type} is not supported")
