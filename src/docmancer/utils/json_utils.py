import re
import json

# def extract_json_from_text(text: str):
#     """
#     Extracts and parses the first valid JSON object found in the input text.
#     Returns the parsed Python object or raises ValueError if no valid JSON is found.
#     """
#     # This regex matches the outermost curly braces and captures the inner JSON
#     json_match = re.search(r'\{(?:[^{}]*|\n)*\}', text, re.DOTALL)

#     if json_match:
#         json_string = json_match.group()
#         try:
#             parsed_json = json.loads(json_string)
#             return parsed_json
#         except json.JSONDecodeError:
#             return None
#     else:
#         return None


def extract_json_from_text(text: str):
    start = text.find("{")
    if start == -1:
        return None
    count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            count += 1
        elif text[i] == "}":
            count -= 1
            if count == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None
