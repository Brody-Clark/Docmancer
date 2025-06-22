from enum import Enum
import os
import io
import sys
import time
import threading
import tempfile
import subprocess
from typing import List, Callable, Any, Coroutine
import platform
from dataclasses import dataclass
from rich.console import Console
from rich.rule import Rule
from rich.spinner import Spinner
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import prompt, print_formatted_text
from prompt_toolkit.formatted_text import HTML
from docmancer.models.documentation_model import DocumentationModel


class UserResponse(Enum):
    QUIT = 1
    ACCEPT = 2
    EDIT = 3
    SKIP = 4


USER_RESPONSES = {
    UserResponse.QUIT: "q",
    UserResponse.ACCEPT: "a",
    UserResponse.EDIT: "e",
    UserResponse.SKIP: "s",
}

ACCEPT = USER_RESPONSES[UserResponse.ACCEPT]
EDIT = USER_RESPONSES[UserResponse.EDIT]
SKIP = USER_RESPONSES[UserResponse.SKIP]
QUIT = USER_RESPONSES[UserResponse.QUIT]


@dataclass
class UserResponseModel:
    doc_model: DocumentationModel
    response: UserResponse


# Define a style for the prompt (e.g., blue background)
# 'bg:#0000FF' is hex for blue. You can use standard color names like 'bg:blue'
# or more specific colors like 'bg:#1e4369' for a darker blue.
blue_background_style = Style.from_dict(
    {
        "prompt": "#FFFFFF bg:#000094",  # White foreground on a slightly darker blue background for the prompt string itself
        "bottom-toolbar": "#FFFFFF bg:#0000FF",  # Example: if you had a toolbar
        "completion-menu": "bg:#333333 #FFFFFF",  # Example: styling for auto-completion menu
        "arg-style": "bold #FFD700",  # Example: style for argument names
        "input": "#FFFFFF bg:#0000FF",  # White text on blue background for user input
    }
)


class Presenter:

    def __init__(self):
        self._console = Console()

    def get_user_approval(self, doc: DocumentationModel) -> UserResponseModel:
        while True:
            response = self.interact(doc)
            if response == USER_RESPONSES[UserResponse.QUIT]:
                return UserResponseModel(doc_model=None, response=UserResponse.QUIT)
            elif response == USER_RESPONSES[UserResponse.ACCEPT]:
                return UserResponseModel(doc_model=doc, response=UserResponse.ACCEPT)
            elif response == USER_RESPONSES[UserResponse.SKIP]:
                return UserResponseModel(doc_model=doc, response=UserResponse.SKIP)
            elif response == USER_RESPONSES[UserResponse.EDIT]:
                try:
                    doc.formatted_documentation = self.edit_text_with_editor(
                        doc.formatted_documentation
                    )
                except Exception as e:
                    print(e)
                continue

    def edit_text_with_editor(self, initial_text: List[str]) -> str:
        editor = self.get_default_editor()
        with tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+", delete=False) as tf:
            tf.writelines(initial_text)
            tf.flush()
            file_path = tf.name

        subprocess.call([editor, file_path])

        with open(file_path, "r") as tf:
            return tf.readlines()

    def get_default_editor(self):
        if platform.system() == "Windows":
            return os.environ.get("EDITOR", "notepad")
        else:
            return os.environ.get("EDITOR", "nano")

    def print_error(self, message: str):
        """Prints an error message."""
        self._console.print(f"[bold red]Error:[/bold red] {message}", style="red")

    def print_success(self, message: str):
        """Prints a success message."""
        self._console.print(
            f"[bold green]Success:[/bold green] {message}", style="green"
        )

    def decorate_slow_task_synchronous(
        self, task_description: str, slow_task: Callable[..., Any], *args, **kwargs
    ) -> Any:
        spinner_name = "star"
        # spinner_name="moon"
        # spinner_name="earth"
        result_container = {"result": None, "exception": None}

        def target_function():
            """
            The function to run in the separate thread, with stdout redirected.
            """
            # Create a StringIO object to capture stdout
            old_stdout = sys.stdout
            redirected_stdout = io.StringIO()
            sys.stdout = redirected_stdout

            try:
                result_container["result"] = slow_task(*args, **kwargs)
            except Exception as e:
                result_container["exception"] = e
            finally:
                # Restore original stdout
                sys.stdout = old_stdout
                # Store captured output
                result_container["captured_output"] = redirected_stdout.getvalue()
                redirected_stdout.close()  # Close the StringIO object

        # Start the slow_task in a separate thread
        thread = threading.Thread(target=target_function)
        thread.start()

        with self._console.status(
            f"[bold magenta]{task_description}...[/bold magenta]", spinner=spinner_name
        ) as status:
            while thread.is_alive():
                # Keep the main thread alive and let rich update the spinner
                pass

        # After the thread finishes, retrieve the result or re-raise the exception
        if result_container["captured_output"]:
            # Optionally print the captured output *after* the spinner has stopped
            self._console.print(
                f"\n[dim italic]Captured output from task:\n{result_container['captured_output'].strip()}[/dim italic]"
            )

        # After the thread finishes, retrieve the result or re-raise the exception
        if result_container["exception"]:
            self.print_error(f"Task failed: {result_container['exception']}")
            raise result_container["exception"]
        else:
            return result_container["result"]

    async def magic_spinner_async(
        self,
        task_description: str,
        async_slow_task: Callable[..., Coroutine],
        *args,
        **kwargs,
    ) -> Any:
        """
        Displays a magic-themed spinner while an asynchronous slow task executes.

        Args:
            task_description (str): A descriptive message for the user.
            async_slow_task (Callable[..., Coroutine]): The asynchronous function (coroutine) to execute.
            *args: Positional arguments to pass to the async_slow_task.
            **kwargs: Keyword arguments to pass to the async_slow_task.

        Returns:
            Any: The result of the async_slow_task.
        """
        spinner_name = "line"  # Or another magical spinner
        with self._console.status(
            f"[bold magenta]{task_description}...[/bold magenta]", spinner=spinner_name
        ) as status:
            try:
                result = await async_slow_task(*args, **kwargs)
                return result
            except Exception as e:
                status.stop()  # Ensure spinner stops on error
                self.print_error(f"Asynchronous task failed: {e}")
                raise  # Re-raise the exception after printing error

    def get_blue_prompt(self, message: str) -> str:
        """
        Shows a prompt_toolkit prompt with a blue background applied to the input area.
        """
        answer = prompt(message=message, style=blue_background_style)
        return answer

    def interact(self, doc: DocumentationModel):
        self._console.clear()
        self._console.print(Rule(style="grey69", title="Source"))
        self._console.print(
            f"[grey69]File:[/grey69] [yellow]{doc.file_path or 'unknown'}"
        )
        self._console.print(
            f"[grey69]Line:[/grey69] [cyan]{doc.start_line or 'unknown'}"
        )
        self._console.print(f"[grey69]Function:[/grey69] [grey]{doc.signature}")
        # self._console.print(Rule(style="grey69"))

        if doc.existing_docstring:
            self._console.print("[grey69]Existing Docstring:")
            self._console.print(f"[pale_green1]{doc.existing_docstring.strip()}")
        self._console.print(Rule(style="grey69", title="Generated Docstring"))
        formatted_doc = "".join(doc.formatted_documentation)
        self._console.print(f"[green]{formatted_doc}")
        self._console.print(Rule(style="grey69"))

        result = self.get_blue_prompt(
            f"Accept ({ACCEPT}), Edit ({EDIT}), Skip ({SKIP}), Quit ({QUIT}): "
        )
        self._console.clear()
        return result.strip().lower()

    def clear_console(self):
        self._console.clear()
