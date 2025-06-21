<h1 align="center">Docmancer</h1><h2 align="center"> Documentation Generation Engine</h2>

<p align="center">
Supported Languages:
  <em>
    Python
  </em>
</p>

## Intro

Docmancer is a source code documentation generation engine that uses a user-provided Large Language Model to generate docstring summaries for in-code documentation.

### Example Usage

#### Original function (no docstring)

```py
# example_script.py
def calculate_rectangle_area(length, width, unit="meters"):
  if length < 0 or width < 0:
    raise ValueError("Length and width must be non-negative.")
  return length * width
```

#### Input

```bash
docmancer --write --file example_script.py --function claculate_rectangle_area --style "PEP"
```

#### Output (with generated docstring)

```py
def calculate_rectangle_area(length, width, unit="meters"):
  """Calculates the area of a rectangle.

  Args:
    length (float): The length of the rectangle. Must be a non-negative number.
    width (float): The width of the rectangle. Must be a non-negative number.
    unit (str, optional): The unit of measurement for the length and width.
                          Defaults to "meters". Other common options include
                          "centimeters", "inches", "feet", etc.

  Returns:
    float: The calculated area of the rectangle in square units.

  Raises:
    ValueError: If either `length` or `width` is a negative number.

  """
  if length < 0 or width < 0:
    raise ValueError("Length and width must be non-negative.")
  return length * width
```

---

**[Documentation](docs/)**

[Install](docs/install) ·
[Options](docs/options) ·
[CLI](docs/cli) ·

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
