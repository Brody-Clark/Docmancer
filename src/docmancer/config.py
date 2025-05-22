import yaml
import os
import sys
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from dataclasses_json import dataclass_json
from docmancer.core.styles import DocstringStyle


class LLMType(Enum):
    LOCAL = "LOCAL"
    REMOTE_API = "REMOTE_API"


@dataclass_json
@dataclass
class LocalLLMSettings:
    """Settings for running a local GGUF model."""

    model_path: str
    n_gpu_layers: int = -1
    n_ctx: int = 4096
    n_batch: int = 560
    n_threads: Optional[int] = None
    main_gpu: Optional[int] = None


@dataclass_json
@dataclass
class RemoteApiLLMSettings:
    """Settings for interacting with a remote LLM API."""

    base_url: str
    model_name: str
    api_key_env_var: Optional[str] = None
    track_tokens_and_cost: bool = True
    user_max_prompt_tokens: Optional[int] = None


@dataclass_json
@dataclass
class LLMConfig:
    """General LLM configuration and mode-specific settings."""

    mode: str = ""
    temperature: float = 0.7
    max_tokens_per_response: int = 2048

    # Nested settings based on mode
    local: Optional[LocalLLMSettings] = None
    remote_api: Optional[RemoteApiLLMSettings] = None

    def get_mode_enum(self) -> LLMType:
        try:
            return LLMType[self.mode.upper()]
        except KeyError:
            raise ValueError(
                f"Invalid LLM mode '{self.mode}' in config. "
                f"Must be one of: {', '.join([s.name for s in LLMType])}."
            )
        except AttributeError:
            raise TypeError(f"Mode '{self.mode}' is not a string type.")


@dataclass_json
@dataclass
class DocmancerConfig:
    """Main configuration for the application."""

    project_dir: str = None
    llm_config: LLMConfig = None
    files: List[str] = field(default_factory=lambda: ["*"])
    functions: List[str] = field(default_factory=lambda: ["*"])
    language: str = None
    style: str = DocstringStyle.BASIC.value
    ignore_files: List[str] = field(default_factory=list)
    ignore_functions: List[str] = field(default_factory=list)
    no_summary: bool = False
    check: bool = False
    generate: bool = True
    force_all: bool = False

    def get_default_style_enum(self) -> DocstringStyle:
        try:
            for style_enum_member in DocstringStyle:
                if style_enum_member.value.lower() == self.default_style.lower():
                    return style_enum_member
            raise ValueError(f"Invalid default_style '{self.default_style}' in config.")
        except AttributeError:
            raise TypeError(
                f"default_style '{self.default_style}' is not a string type."
            )


class EnvVarLoader(yaml.SafeLoader):
    """
    A custom YAML loader that processes !ENV tags to pull values from environment variables.
    Supports a default fallback value using '|' (e.g., !ENV VAR_NAME | default_value).
    """


def construct_env_var(loader, node):
    """
    Constructor for the !ENV tag.
    It attempts to retrieve the environment variable.
    If a default value is provided (e.g., '!ENV VAR_NAME | default'), it uses that if the env var is not set.
    Otherwise, it raises a ValueError if the env var is missing and no default is provided.
    """
    value = loader.construct_scalar(node)

    # Split the value by '|' to separate variable name and optional default
    parts = [p.strip() for p in value.split("|", 1)]
    env_var_name = parts[0]
    default_value = parts[1] if len(parts) > 1 else None

    # Retrieve environment variable
    env_val = os.getenv(env_var_name)

    if env_val is None:
        if default_value is not None:
            # If default is provided, use it
            return default_value
        else:
            # If no default and env var is missing, raise an error
            raise ValueError(
                f"Environment variable '{env_var_name}' is not set "
                f"and no default value was provided for '!ENV {value}' in config."
            )
    return env_val


EnvVarLoader.add_constructor("!ENV", construct_env_var)
