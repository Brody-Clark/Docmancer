import httpx
from typing import Dict, Any, List, Optional, Union
import json
from docmancer.generator.llm.llm_agent_base import LLMAgent


class WebAgent(LLMAgent):
    def __init__(self, api_endpoint: str, api_key: Optional[str] = None):
        """
        Initializes the WebAgent with the LLM API endpoint and an optional API key.

        Args:
            api_endpoint (str): The URL of the LLM API endpoint.
                                 Examples:
                                 - OpenAI: "https://api.openai.com/v1/chat/completions"
                                 - Custom hosted model: "https://your-custom-llm.com/generate"
            api_key (Optional[str]): The API key for authentication, if required by the endpoint.
                                      Can be None if the endpoint doesn't require one.
        """
        if not api_endpoint:
            raise ValueError("API endpoint cannot be empty.")
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        # Use httpx.AsyncClient for persistent connections and better performance
        # across multiple requests.
        self._client = httpx.AsyncClient()

    async def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make the actual HTTP POST request to the LLM API.

        Args:
            payload (Dict[str, Any]): The JSON payload to send to the API.
                                       This structure depends heavily on the LLM API.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx status code.
            httpx.RequestError: For network-related errors.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            # Common header for Bearer token authentication (e.g., OpenAI, many others)
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Some APIs might use different headers, e.g., "X-API-Key"
            # Adjust as per your specific LLM API's documentation.

        try:
            response = await self._client.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=60.0,  # Set a reasonable timeout for LLM responses
            )
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()
        except httpx.HTTPStatusError as e:
            print(
                f"API request failed with status {e.response.status_code}: {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise
        except json.JSONDecodeError as e:
            print(
                f"Failed to decode JSON response: {e}. Response text: {response.text}"
            )
            raise

    async def generate_summary_for_function(
        self,
        function_code: str,
        function_name: str,
        model_id: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 200,
    ) -> Dict[str, Any]:
        """
        Generates a documentation summary for a single function using the web LLM.

        Args:
            function_code (str): The full source code of the function to document.
            function_name (str): The name of the function (for context/identification).
            model_id (str): The ID of the model to use (e.g., "gpt-4o", "claude-3-sonnet").
                            This will vary based on the specific API.
            temperature (float): Controls the randomness of the output.
            max_tokens (int): Maximum number of tokens to generate in the response.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed JSON summary from the LLM.
                            Example: {"summary": "...", "parameters": [{"name": "...", "description": "..."}]}
                            The exact structure depends on your prompt and the LLM's output.
        """
        # --- Prompt Engineering ---
        # Craft the prompt to guide the LLM to produce the desired JSON format.
        # This is CRUCIAL for reliable parsing.

        system_prompt = (
            "You are a highly skilled documentation generator for Python code. "
            "Your task is to analyze a given Python function and generate a JSON object "
            "containing a concise 'summary' of its purpose and 'parameters' details. "
            "For each parameter, provide its 'name' and a 'description'. "
            "Do NOT include any additional text, preambles, or explanations outside the JSON."
            "Example JSON format:\n"
            "```json\n"
            "{\n"
            '  "summary": "Concise description of the function\'s purpose.",\n'
            '  "parameters": [\n'
            '    {"name": "param1", "description": "Description of param1."},\n'
            '    {"name": "param2", "description": "Description of param2."}\n'
            "  ]\n"
            "}\n"
            "```"
        )

        user_message = (
            f"Please generate documentation for the following Python function '{function_name}':\n\n"
            f"```python\n{function_code}\n```"
        )

        # --- API Payload Construction ---
        # This payload structure is typical for OpenAI-compatible APIs (e.g., LiteLLM, vLLM, custom servers).
        # You MUST adjust this based on the specific LLM API you are using.
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {
                "type": "json_object"
            },  # Use this if the API supports it (OpenAI, some others)
        }

        try:
            response_data = await self._make_api_request(payload)
            # --- Response Parsing ---
            # Extract the actual content. This also depends on the API.
            # For OpenAI-compatible chat APIs:
            if "choices" in response_data and response_data["choices"]:
                raw_content = response_data["choices"][0]["message"]["content"]
                return json.loads(raw_content)
            else:
                raise ValueError(
                    "Unexpected API response structure: No 'choices' found."
                )

        except (
            httpx.HTTPStatusError,
            httpx.RequestError,
            json.JSONDecodeError,
            ValueError,
        ) as e:
            print(f"Error during summary generation for '{function_name}': {e}")
            # Decide how to handle this: re-raise, return empty, log, etc.
            raise

    async def generate_summaries_in_batch(
        self,
        functions_data: List[Dict[str, str]],
        model_id: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens_per_summary: int = 150,
    ) -> List[Dict[str, Any]]:
        """
        Generates documentation summaries for multiple functions in a single API request (batching).

        Args:
            functions_data (List[Dict[str, str]]): A list of dictionaries, each with 'name' and 'code' keys.
                                                Example: [{"name": "func_a", "code": "def func_a():..."}, ...]
            model_id (str): The ID of the model to use.
            temperature (float): Controls the randomness of the output.
            max_tokens_per_summary (int): Approximate max tokens per function summary.

        Returns:
            List[Dict[str, Any]]: A list of parsed JSON summaries.
        """
        if not functions_data:
            return []

        # --- Prompt Engineering for Batching ---
        # This is where the delimiter strategy comes in.
        system_prompt = (
            "You are a highly skilled documentation generator for Python code. "
            "For each Python function provided, you MUST generate a separate JSON object "
            "containing a 'function_name', 'summary', and 'parameters' (as a list of objects with 'name' and 'description'). "
            "Each JSON object MUST be separated by the unique delimiter '---DOCMANCER_FUNCTION_DELIMITER---'. "
            "Do NOT include any preambles, postambles, or additional text outside the JSON and delimiters. "
            "Ensure the 'function_name' in the JSON matches the provided function's name exactly."
            "Example JSON format (for one function):\n"
            "```json\n"
            "{\n"
            '  "function_name": "example_function",\n'
            '  "summary": "Concise description.",\n'
            '  "parameters": [\n'
            '    {"name": "param1", "description": "Desc param1."}\n'
            "  ]\n"
            "}\n"
            "```"
        )

        user_messages_parts = []
        for func_data in functions_data:
            user_messages_parts.append(
                f"Function '{func_data['name']}':\n"
                f"```python\n{func_data['code']}\n```"
            )

        user_message_combined = "\n\n".join(user_messages_parts)

        # Calculate max tokens for the whole batch response
        # A rough estimate: (num_functions * max_tokens_per_summary) + (num_functions * delimiter_tokens)
        DELIMITER_TOKEN_ESTIMATE = 5  # Adjust based on actual delimiter length
        max_batch_tokens = (len(functions_data) * max_tokens_per_summary) + (
            len(functions_data) * DELIMITER_TOKEN_ESTIMATE
        )
        max_batch_tokens = min(
            max_batch_tokens, 4000
        )  # Cap to avoid exceeding context window for output

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message_combined},
            ],
            "temperature": temperature,
            "max_tokens": max_batch_tokens,
            # Be careful with response_format:json_object for batching.
            # It expects a single valid JSON object. If your delimiter strategy leads to multiple,
            # it might fail. Some APIs might interpret the whole thing as one JSON object, which is bad.
            # Often, for custom batching with delimiters, you *don't* use response_format:json_object.
            # You rely on the prompt instructions and post-processing.
            # For simplicity, if API supports it, you might have to return a JSON array of objects.
            # Here we assume we rely on post-processing.
            # "response_format": {"type": "json_object"}
        }

        try:
            response_data = await self._make_api_request(payload)
            raw_content = response_data["choices"][0]["message"]["content"]

            # --- Parsing Batched Response ---
            parsed_summaries = []
            delimiter = "---DOCMANCER_FUNCTION_DELIMITER---"
            json_strings = [
                s.strip() for s in raw_content.split(delimiter) if s.strip()
            ]

            for json_str in json_strings:
                try:
                    parsed_summaries.append(json.loads(json_str))
                except json.JSONDecodeError as e:
                    print(
                        f"Warning: Could not parse JSON object from batch: {e}. Malformed part: {json_str[:200]}..."
                    )
                    # Handle error: perhaps skip, or log for manual review

            return parsed_summaries

        except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as e:
            print(f"Error during batch summary generation: {e}")
            raise

    async def close(self):
        """Closes the HTTP client session."""
        await self._client.aclose()
