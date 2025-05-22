# Configuring Docmancer

Docmancer supports several options for documentation generation.
*it is recommended to use the configuration file for specifying options that do not change often.*

## Arguments & Options

| Argument / Flag            | Description                                                 | Default |
| -------------------------- | ----------------------------------------------------------- | ------- |
| `--file <path>`            | Glob pattern path to a specific file to document            | `*`  |
| `--functions <name...>`    | Specific function names or glob pattern to target (space-separated list) | `[*]`    |
| `--style <style>`          | Genereated docstring format: *See supported formats*        | `None`    |
| `--model <backend>`        | Backend model to use (e.g., `llama`, `mistral`)             | `llama` |
| `--dry-run`                | Preview changes without writing to files                    | `False` |
| `-h, --help`               | Show help message and exit                                  | N/A     |

## Configuration File

This project supports YAML-based config files for storing options that do not need to regularly change.
See [](config file) for all supported features.

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