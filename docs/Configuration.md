# Configuring docnsrt

docnsrt supports several options for documentation generation.
*it is recommended to use the configuration file for specifying options that do not change often.*

## Arguments & Options

> [!NOTE]
> Some features are experimental or may be incomplete

| Argument / Flag            | Description                                                 | Default |
| -------------------------- | ----------------------------------------------------------- | ------- |
| `--write`                  | Writes generated strings to files                           | N/A     |
| `--config <path>`          | Path to config file                                         | `.docnsrt.yaml`     |
| `--file <path>`            | Glob pattern path to a specific file to document            | `*`  |
| `--log-level`              | Level of logging (DEBUG, INFO, WARNING, ERROR)            | `INFO`|
| `--ignore-files <name...>` | Specific file names or glob pattern to ignore (space-separated list) | N/A |
| `--functions <name...>`    | Specific function names or glob pattern to target (space-separated list) | `[*]`    |
| `--ignore-functions <name...>`| Specific function names or glob pattern to ignore (space-separated list) | N/A   |
| `--project-dir <path>`     | Path to project source.                                     | Current Working Directory |
| `--language, -l <language>`    | Language of source files: *See supported languages*                                | N/A |
| `--force-all`              | Skips prompting for each generated docstring. Force writes to files. | N/A |
| `--style, -s <style>`          | Generated docstring format: *See supported styles*        | `None`    |
| `-h, --help`               | Show help message and exit                                   | N/A     |

## Configuration File

This project supports YAML-based config files for storing options that do not need to regularly change.
See [config.yaml](../config.yaml) for a template.

### Example

YAML for PEP formatted docstrings

```yml
# .docnsrt.yaml
style: PEP
log_level: INFO
language: python
files:                # Files to include by pattern
  - "src/**/*.py"
functions:
  - "*"
ignore_files:         # Files to ignore by pattern
  - "**/test_*.py"     
  - "**/__init__.py"     
  - "docs/"               
  - ".git/"        
ignore_functions:     # Functions to ignore by pattern
  - "main"               
  - "__init__"
  - "test_*"

```

## Supported Styles

> [!NOTE]
> Support for more styles is ongoing

- PEP
- XML
- Numpy

## Supported Languages

> [!NOTE]
> Support for more languages is ongoing

- python
- csharp
