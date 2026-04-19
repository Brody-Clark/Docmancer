"""CLI for docnsrt - a documentation generation tool."""

from pathlib import Path
import argparse
import os
import yaml
from docnsrt.config import DocnsrtConfig, load_project_config_yaml
from docnsrt.core.styles import (
    CANONICAL_STYLE_NAMES,
    LOWERCASE_STYLE_NAMES,
    DEFAULT_STYLE_NAME,
)
from docnsrt.core.languages import CANONICAL_LANGUAGE_NAMES


def load_config(config_path: str) -> dict:
    """Loads and parses a YAML configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the configuration file is not a valid YAML file.
        ValueError: If the configuration file is missing required fields.
        RuntimeError: If an unexpected error occurs while loading the configuration.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    if not os.path.isfile(config_path):
        raise ValueError(f"Provided path is not a file: {config_path}")

    try:
        config = load_project_config_yaml(config_path)
        return config
    except yaml.YAMLError as e:
        raise ValueError(
            f"Error parsing YAML configuration file '{config_path}': {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while loading config '{config_path}': {e}"
        ) from e


def validate_style_case_insensitive(style_string: str) -> str:
    """
    Custom type function for argparse to validate --style argument,
    ignoring case, and returning the canonical style name.
    """
    lower_style_input = style_string.lower()

    if lower_style_input in LOWERCASE_STYLE_NAMES:
        # Find the original, correctly cased style name from STYLE_DEFINITIONS keys
        # by looking up its lowercase version.
        return next(
            (
                name
                for name in CANONICAL_STYLE_NAMES
                if name.lower() == lower_style_input
            ),
            None,
        )

    # Raise error if style is not found
    raise argparse.ArgumentTypeError(
        f"Invalid style '{style_string}'. "
        f"Allowed styles are: {', '.join(CANONICAL_STYLE_NAMES)} (case-insensitive). "
        f"Default: {DEFAULT_STYLE_NAME}"
    )


def find_and_load_config(
    start_path: Path, config_file_name: str = ".docnsrt.yaml"
) -> dict:
    """
    Searches for a configuration file in the starting path and its parent directories.

    Args:
        start_path (Path): The directory to start searching from (usually current working directory).
        config_file_name (str): The name of the configuration file to look for.

    Returns:
        (config_path, dict): The path of the config file and a dictionary containing the loaded configuration, or an empty dict if not found.
    """
    current_path = start_path
    while current_path != current_path.parent:  # Loop until the root directory
        config_path = current_path / config_file_name
        if config_path.is_file():
            try:
                config_dict = load_config(config_path=config_path)
                return (config_path, config_dict)
            except Exception as e:
                print(
                    f"Warning: Could not load config file '{config_path}'. Error: {e}",
                    file=os.sys.stderr,
                )
                return (None, {})  # Return empty config if parsing fails
        current_path = current_path.parent
    print(
        f"No configuration file '{config_file_name}' found in current or parent directories."
    )
    return (None, {})  # Return empty config if no file found


def get_default(config, arg_name, fallback=None):
    """Gets the default value for a configuration argument.

    Args:
        config (dict): The configuration dictionary.
        arg_name (str): The name of the argument to retrieve.
        fallback (Any, optional): A fallback value to return if the argument is not found. Defaults to None.

    Returns:
        Any: The default value for the argument, or the fallback value if not found.
    """
    return config.get(
        arg_name.replace("-", "_"), fallback
    )  # Config keys are snake_case


def parse_args() -> DocnsrtConfig:
    """Parses command line arguments and returns a docnsrtConfig object."""

    parser = argparse.ArgumentParser(
        description="Generate documentation from source code.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=".docnsrt.yaml",
        help="Path to the YAML configuration file for docstring settings.",
    )

    parser.add_argument(
        "--files",
        nargs="+",
        default=argparse.SUPPRESS,
        help="File paths or glob patterns (e.g., src/**/*.py)",
    )
    parser.add_argument(
        "--functions",
        "-func",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Function names or glob patterns to match functions to within speficied files (e.g., calculate_*). Default is all functions.",
    )
    parser.add_argument(
        "--ignore-files",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Files names or glob patterns to skip (e.g., src/**/test_*.py)",
    )
    parser.add_argument(
        "--ignore-functions",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Function names or glob patterns to skip within speficied files (e.g., _test_*)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        nargs="?",  # Make it optional so it can be defaulted by config
        default=argparse.SUPPRESS,
        help="Path to the root of the source code project. Defaults to current directory if not specified and no config file defines it.",
    )

    parser.add_argument(
        "--language",
        "-l",
        type=str,
        choices=CANONICAL_LANGUAGE_NAMES,
        default=argparse.SUPPRESS,
        help="Programming language of the source project",
    )

    parser.add_argument(
        "--style",
        "-s",
        type=str,
        choices=CANONICAL_STYLE_NAMES,
        default=argparse.SUPPRESS,
        help="Style of generated documentation",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Writes doc strings to specified files and functions",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Returns a message indicating which functions are undocumented",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        default=argparse.SUPPRESS,
        help="If included, force-approves all generated documention. User will not be prompted to accept/skip/edit/etc..",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Skips functions that already appear to have a docstring.",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (overrides DOCNSRT_LOG_LEVEL env var)",
        default="INFO",
    )

    # Parse arguments after defaults are set
    args = parser.parse_args()
    app_config = vars(args)

    # Dictionary representation of defaults
    config = DocnsrtConfig().to_dict()

    if app_config["config"] == ".docnsrt.yaml":
        # Load configuration first to use its values as defaults
        # Start searching from the current working directory where the CLI is run.
        config_path, user_config = find_and_load_config(Path.cwd())
        config.update(user_config)
    else:
        # If user explicitly provided a config path
        try:
            user_config = load_config(Path(args.config))
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing configuration file '{args.config}': {e}")
            return None
        except RuntimeError as e:
            print(f"An unexpected error occurred while loading config: {e}")
            return None

        if not user_config:
            print(f"Configuration file '{args.config}' is empty.")
            return None

        # Merge explicit config over everything else
        config.update(user_config)
        config_path = args.config

    # Post-processing for boolean flags to override defaults.
    # For flags using action='store_true', their default is False.
    # If config should set them to True, handle it after parsing.
    if app_config.get("write") is None and app_config.get("check") is None:
        parser.error("You must specify either --write or --check.")

    if (
        get_default(config, "force-all", False)
        and not parser.parse_known_args()[0].force_all
    ):
        app_config["force_all"] = True
    if (
        get_default(config, "no-summary", False)
        and not parser.parse_known_args()[0].no_summary
    ):
        app_config["no_summary"] = True
    if (
        get_default(config, "skip-existing", False)
        and not parser.parse_known_args()[0].skip_existing
    ):
        app_config["skip_existing"] = True
    if get_default(config, "check", False) and not parser.parse_known_args()[0].check:
        app_config["check"] = True

    # If `project_dir` is not explicitly set, derive it from config file location
    # This assumes `project_dir` in config is the true project root
    if "project_dir" not in config and config:
        # If config was found, assume its parent directory is the project_dir
        config["project_dir"] = str(
            Path(config_path).parent
        )  # Store config_path in a global var or return it
    else:  # Fallback if no config and no arg
        config["project_dir"] = str(Path.cwd())

    if args.log_level:
        config["log_level"] = args.log_level

    # Finally, update config with args
    config.update(app_config)

    return DocnsrtConfig.from_dict(config)
