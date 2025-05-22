from docmancer.config import LLMConfig, LLMType
from docmancer.generator.llm.llm_agent_base import LLMAgent
from docmancer.generator.llm.local_agent import LlamaCppAgent


class LLMAgentFactory:

    def get_agent(self, llm_config: LLMConfig) -> LLMAgent:
        if llm_config.get_mode_enum() == LLMType.LOCAL:
            return LlamaCppAgent(llm_config.local)
        else:
            raise NotImplementedError(f"{llm_config.model_type} is not supported")
