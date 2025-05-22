from abc import ABC, abstractmethod


class LLMAgent(ABC):

    @abstractmethod
    def send_message(self, message: str) -> str:
        """_summary_

        Args:
            message (str): User prompt used to generate function summary

        Returns:
            str: JSON response containing function summary
        """
