from llama_cpp import Llama
from docmancer.generator.llm.llm_agent_base import LLMAgent
from docmancer.config import LocalLLMSettings


class LlamaCppAgent(LLMAgent):
    def __init__(self, settings: LocalLLMSettings):
        self._model_path = settings.model_path
        # TODO: initialize system here with other settings!

    def send_message(self, message: str) -> str:

        llm = Llama(
            model_path=self._model_path, chat_format="chatml", n_ctx=0, verbose=False
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
            temperature=0.7,
        )

        return response["choices"][0]["message"]["content"]
