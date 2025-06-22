# Configuring Docmancer

Docmancer supports several options for documentation generation.
*it is recommended to use the configuration file for specifying options that do not change often.*

## Arguments & Options

> [!NOTE]
> Some features are experimental or may be incomplete

| Argument / Flag            | Description                                                 | Default |
| -------------------------- | ----------------------------------------------------------- | ------- |
| `--write`                  | Writes generated strings to files                           | N/A     |
| `--config <path>`          | Path to config file                                         | `.docmancer.yaml`     |
| `--file <path>`            | Glob pattern path to a specific file to document            | `*`  |
| `--ignore-files <name...>` | Specific file names or glob pattern to ignore (space-separated list) | N/A |
| `--functions <name...>`    | Specific function names or glob pattern to target (space-separated list) | `[*]`    |
| `--ignore-functions <name...>`| Specific function names or glob pattern to ignore (space-separated list) | N/A   |
| `--project-dir <path>`     | Path to project source.                                     | Current Working Directory |
| `--language <language>`    | Language of source files.                                   | N/A |
| `--style <style>`          | Genereated docstring format: *See supported formats*        | `None`    |
| `--no-summary`  | Skips generating summary. Creates placeholder docstrings.   | N/A |
| `--force-all`    | Skips prompting for each generated docstring. Force writes to files.    | N/A |
| `--model-type <backend>`   | Type of LLM to use (local, web)                             | N/A |
| `--model-local-path <path>`| File path of .gguf file if model-type is 'local'            | N/A |
| `--model-web-api <url>`    | URL of remote model if model-type is 'web'. _Currently Unsupported_   | N/A |
| `-h, --help`               | Show help message and exit                                  | N/A     |

## Configuration File

This project supports YAML-based config files for storing options that do not need to regularly change.
See [config.yaml](../config.yaml) for a template.

### Example

YAML

```yml
# .docmancer.yaml
style: PEP
language: python
files:
  - "src/**/*.py"
functions:
  - "*"
ignore_files:
  - "**/test_*.py"     
  - "**/__init__.py"     
  - "docs/"               
  - ".git/"        
ignore_functions:
  - "main"               
  - "__init__"
  - "test_*"
llm_config:
  mode: LOCAL
  temperature: 0.5   
  local:
    model_path: !ENV DOCMANCER_MODEL_PATH 
    n_gpu_layers: -1 
    n_ctx: 4096        
    n_batch: 512 

```

## Supported Styles

> [!NOTE]
> Support for more styles is ongoing

- PEP
