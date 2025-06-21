# Contributing

## Getting Started

This project uses [Poetry]([Poetry](https://github.com/python-poetry/poetry)) for dependency management and virtual environments.

1. Clone the repository

    ```bash
    git clone https://github.com/brody-clark/docmancer.git
    cd docmancer
    ```

2. Install Dependencies

    ```bash
    poetry install
    ```

3. Activate the Virtual Environment

    ```bash
    poetry shell
    ```

## Code Style & Formatting

- This project follows [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- All code should be formatted using [black](https://github.com/psf/black).
- Run the formatter prior to commits:

    ```bash
    black .
    ```

## Docstring Guidelines

This project follows [PEP 257-style](https://peps.python.org/pep-0257/) docstrings with an emphasis on clarity and brevity.

### Where to Add Docstrings

| Element                    | Docstring Required? | Notes                                            |
| -------------------------- | ------------------- | ------------------------------------------------ |
| Public modules             | Yes                 | Brief summary of purpose                         |
| Public classes             | Yes                 | Summary and responsibilities                     |
| Public methods/functions   | Yes                 | Summary, parameter descriptions, and return info |
| Private/internal functions | Optional            | Add only if they are complex                     |
| Test functions             | No                  | Prefer self-documenting names                    |

### Format Example

```py
def normalize_data(data: List[float]) -> List[float]:
    """
    Normalize a list of floats to the 0–1 range.

    Args:
        data (List[float]): The list of values to normalize.

    Returns:
        List[float]: Normalized values between 0 and 1.
    """
```

## Unit Testing

This project uses [pytest](https://docs.pytest.org/en/stable/) for all unit testing.

### Test Directory Structure

All tests should go in the `tests/` directory and mirror the structure of the src/ folder:

```pqsql
project-root/
├── src/
│   └── core/
│       └── parser/
│           └── python_parser.py
└── tests/
    └── core/
        └── parser/
            └── test_python_parser.py
```

### Writing a Test

- Test files should be named test_*.py.

- Test functions should begin with test_.

- Use clear, descriptive function names.

- Prefer unit tests (isolated and fast), but integration tests are welcome if scoped properly.

```py
# tests/core/parser/test_python_parser.py

import pytest
from core.parser.python_parser import extract_function_signature

def test_extract_function_signature_returns_expected_signature():
    source_code = "def add(a, b):\n    return a + b"
    result = extract_function_signature(source_code)
    assert result == "def add(a, b):"
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/core/parser/test_python_parser.py
```

Run tests and display code coverage (optional):

```bash
pytest --cov=src
```

**Make sure to install test dependencies:**

```bash
poetry install --with dev
```

### Test Checklist

- Does each function/module have corresponding tests?
- Do your tests cover edge cases?
- Do your tests fail when the code is broken?
- Are tests isolated (i.e. no hidden dependencies)?
- Is your test data simple and self-explanatory?

## Before you Commit

1. Format your code
2. Run tests if possible
3. Keep commits small and focused.
4. Write clear commit messages using the conventional format:

    ```txt
    feat: Add support for --function argument
    fix: Correct line offset handling in parser
    chore: refactored python parser
    ```
