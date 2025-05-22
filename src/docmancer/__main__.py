import os
import sys
from docmancer.core.cli import parse_args
from docmancer.core.engine import DocumentationBuilderEngine
from docmancer.generator.documentation_generator import DocumentationGenerator
from docmancer.generator.llm.llm_agent_factory import LLMAgentFactory
from docmancer.formatter.formatter_factory import FormatterFactory
from docmancer.core.presenter import Presenter
from docmancer.parser.parser_factory import ParserFactory
from docmancer.config import DocmancerConfig, LLMType


def main():
    config = parse_args()
    if not os.path.isdir(config.project_dir):
        raise Exception("Error: Project directory does not exist.")

    try:

        # --- Accessing config settings ---
        llm_config = config.llm_config  # Direct attribute access!
        llm_mode_enum = llm_config.get_mode_enum()  # Get the type-safe Enum member

        print(f"\nLLM Mode: {llm_mode_enum.value} (Enum: {llm_mode_enum.name})")
        print(f"  Temperature: {llm_config.temperature}")
        print(f"  Max Tokens per Response: {llm_config.max_tokens_per_response}")

        if llm_mode_enum == LLMType.LOCAL:
            if not llm_config.local:
                raise ValueError(
                    "Config error: 'local' settings missing for LOCAL mode."
                )
            local_settings = llm_config.local 
            print(f"  Model Path: {local_settings.model_path}")
            print(f"  GPU Layers: {local_settings.n_gpu_layers}")
            # Use these settings to initialize your local LLM agent
            # llm_agent = LLMAgent(mode=llm_mode_enum, config=local_settings)

        elif llm_mode_enum == LLMType.REMOTE_API:
            if not llm_config.remote_api:
                raise ValueError(
                    "Config error: 'remote_api' settings missing for REMOTE_API mode."
                )
            remote_settings = llm_config.remote_api
            print(f"  Base URL: {remote_settings.base_url}")
            print(f"  Model Name: {remote_settings.model_name}")
            print(f"  Track Tokens/Cost: {remote_settings.track_tokens_and_cost}")

            if remote_settings.api_key_env_var:
                api_key = os.environ.get(remote_settings.api_key_env_var)
                if not api_key:
                    print(
                        f"Error: API key environment variable "
                        f"'{remote_settings.api_key_env_var}' not set.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            else:
                print("  No API key environment variable specified.")

            if remote_settings.track_tokens_and_cost:
                print(
                    f"  User Max Prompt Tokens: {remote_settings.user_max_prompt_tokens}"
                )

    except (FileNotFoundError, ValueError, RuntimeError, TypeError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        agent_factory = LLMAgentFactory()
        agent = agent_factory.get_agent(llm_config=config.llm_config)
    except Exception as e:
        print(e)

    presenter = Presenter()

    generator = DocumentationGenerator(model=agent, language=config.language)

    formatter_factory = FormatterFactory()
    formatter = formatter_factory.get_formatter(
        style=config.style, language=config.language
    )

    parser_factory = ParserFactory()
    parser = parser_factory.get_parser(language=config.language)

    builder_engine = DocumentationBuilderEngine(
        generator=generator, formatter=formatter, presenter=presenter, parser=parser
    )

    builder_engine.run(config)


if __name__ == "__main__":
    main()
