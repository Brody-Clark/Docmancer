from llama_cpp import Llama
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.config import LocalLLMSettings


class LlamaCppAgent(LlmAgentBase):
    def __init__(self, settings: LocalLLMSettings):
        self._settings = settings

    def send_message(self, message: str) -> str:

        llm = Llama(
            model_path=self._settings.model_path,
            chat_format="chatml",
            n_ctx=self._settings.n_ctx,
            verbose=self._settings.log_verbose,
        )
        response = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a source code documentation generator that responds only in JSON format.",
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "int"},
                        "letter": {"type": "string"},
                    },
                    "required": ["number", "letter"],
                },
            },
            temperature=self._settings.temperature,
        )

        return response["choices"][0]["message"]["content"]
