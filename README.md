> [!NOTE]
> This project is a work in progress. As such, some features may be missing or incomplete

<h1 align="center">docnsrt</h1><h2 align="center"> A Docstring Insertion Tool</h2>

<p align="center">
Supported Languages:
  <em>
    Python, C#
  </em>
</p>

## Intro

**docnsrt** (pronounced *doc-insert*) is a CLI-based docstring template insertion tool that supports multiple languages and docstring styles. It inserts language-specific docstring templates directly into code and provides an interactive interface for completing and validating documentation.

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
docnsrt --write --file example_script.py --function calculate_rectangle_area --style PEP --language python
```

#### Output (with generated docstring template)

```py
# example_script.py
def calculate_rectangle_area(length, width, unit="meters"):
  """ _summary_

  Args:
    length: _desc_
    width: _desc_
    unit: _desc_

  Returns:
    _desc_

  Raises:
    _desc_

  """
  if length < 0 or width < 0:
    raise ValueError("Length and width must be non-negative.")
  return length * width
```

---

**[Documentation](docs/)**

[Install](docs/Install.md) ·
[Configuration](docs/Configuration.md)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
