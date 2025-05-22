import os
from pathlib import Path
from typing import List


def get_all_files_in_dir(dir_path):
    """
    Returns a list of all files in the given directory path.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list: A list of file names in the directory.
            Returns an empty list if the directory does not exist or is empty.
    """
    if not os.path.isdir(dir_path):
        return []

    files = os.listdir(dir_path)
    return files


def get_files_by_pattern(pattern: str) -> List[Path]:
    """
    Return a list of Path objects matching the given glob pattern.
    Example patterns:
        "*.py" - all Python files in current dir
        "src/**/*.py" - all Python files recursively under src/
    """
    return list(Path().glob(pattern))  # Non-recursive unless you use **


def get_line_text_offset_spaces(file_path: str, line: int) -> int:
    """
    Returns the number of spaces before text begins on a given line
    or -1 if not found.

    Args:
        line (int): line number of file

    """
    with open(file_path, "r", encoding="utf8") as f:
        for idx, line_text in enumerate(f, start=1):
            if idx == line:
                return len(line_text) - len(line_text.lstrip(" "))
    return -1


def read_file_to_string(file_path):
    """_summary_

    Args:
        file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(file_path, "r", encoding="utf8") as file:
        file_content = file.read()
        return file_content


def read_file_to_bytes(file_path):
    """_summary_

    Args:
        file_path (file_path): path to file

    Returns:
        bytes: content of file in bytes
    """
    with open(file_path, "rb") as file:
        file_content = file.read()
        return file_content
