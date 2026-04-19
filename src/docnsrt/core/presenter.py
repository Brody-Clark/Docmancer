"""This module contains functions to display text to the CLI."""

from enum import Enum
import logging
import io
import sys
import threading
import tempfile
import subprocess
from typing import List, Callable, Any, Coroutine
from dataclasses import dataclass
from rich.console import Console
from rich.rule import Rule
from rich.markup import escape
from rich.table import Table

# from rich.spinner import Spinner
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import prompt
from docnsrt.core.models import DocstringPresentationModel
from docnsrt.utils import platform_utils
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode

logger = logging.getLogger(__name__)


from dataclasses import dataclass
from enum import Enum, auto


class UserResponse(Enum):
    """
    Enumeration for user responses.
    """

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
    """
    Model for user responses.
    """

    doc_model: DocstringPresentationModel
    response: UserResponse


class Mode(Enum):
    VIEW = auto()
    EDIT = auto()
    CONFIRM = auto()


@dataclass
class UIState:
    doc: DocstringPresentationModel
    mode: Mode = Mode.VIEW
    cursor_y: int = 0
    scroll_offset: int = 0
    edited_lines: list[str] = None
    running: bool = True
    result: UserResponseModel | None = None

docstring_style = Style.from_dict({
    # main input area
    # "": "bg:#000000 #0000ff", # black background, blue text

    # cursor
    "cursor": "bg:#ffffff #000000",

    # bottom toolbar
    "bottom-toolbar": "bg:#222222 #cccccc",

    # optional: prompt text
    "prompt": "bold #00ffff",
})



# 'bg:#0000FF' is hex for blue.
blue_background_style = Style.from_dict(
    {
        "prompt": "#FFFFFF bg:#000094",
        "bottom-toolbar": "#FFFFFF bg:#0000FF",
        "completion-menu": "bg:#333333 #FFFFFF",
        "arg-style": "bold #FFD700",
        "input": "#FFFFFF bg:#0000FF",
    }
)


# class CursesPresenter:
#     def run(self, doc: DocstringPresentationModel) -> UserResponseModel:
#         return curses.wrapper(self._main, doc)

#     def _main(self, stdscr, doc):
#         curses.curs_set(0)
#         stdscr.keypad(True)

#         state = UIState(doc=doc, edited_lines=doc.new_docstring.lines.copy())

#         while state.running:
#             stdscr.clear()
#             self._render(stdscr, state)
#             key = stdscr.getch()
#             self._handle_input(key, state)

#         return state.result

#     def _render(self, stdscr, state: UIState):
#         h, w = stdscr.getmaxyx()

#         self._draw_header(stdscr, state, 0, w)
#         self._draw_existing(stdscr, state, 3, h // 3, w)
#         self._draw_generated(stdscr, state, h // 3 + 4, h // 3, w)
#         self._draw_footer(stdscr, state, h - 2, w)

#     def _draw_header(self, stdscr, state, y, w):
#         doc = state.doc
#         stdscr.addstr(y, 0, f"File: {doc.file_path}")
#         stdscr.addstr(y+1, 0, f"Function: {doc.signature}")

#     def _draw_header(self, stdscr, state, y, w):
#         doc = state.doc
#         stdscr.addstr(y, 0, f"File: {doc.file_path}")
#         stdscr.addstr(y+1, 0, f"Function: {doc.signature}")

#     def _handle_view_input(self, key, state):
#         if key == ord('q'):
#             state.result = UserResponseModel(None, UserResponse.QUIT)
#             state.running = False

#         elif key == ord('a'):
#             state.doc.new_docstring.lines = state.edited_lines
#             state.result = UserResponseModel(state.doc, UserResponse.ACCEPT)
#             state.running = False

#         elif key == ord('s'):
#             state.result = UserResponseModel(state.doc, UserResponse.SKIP)
#             state.running = False

#         elif key == ord('e'):
#             state.mode = Mode.EDIT

#     def _handle_edit_input(self, key, state):
#         y = state.cursor_y
#         lines = state.edited_lines

#         if key == 27:  # ESC
#             state.mode = Mode.VIEW
#             return

#         elif key in (curses.KEY_UP, ord('k')):
#             state.cursor_y = max(0, y - 1)

#         elif key in (curses.KEY_DOWN, ord('j')):
#             state.cursor_y = min(len(lines) - 1, y + 1)

#         elif key in (curses.KEY_BACKSPACE, 127):
#             if lines[y]:
#                 lines[y] = lines[y][:-1]

#         elif key == curses.KEY_ENTER or key == 10:
#             lines.insert(y + 1, "")
#             state.cursor_y += 1

#         elif 32 <= key <= 126:  # printable chars
#             lines[y] += chr(key)

#     def _draw_generated(self, stdscr, state, start_y, height, width):
#         for i in range(height):
#             line_idx = i + state.scroll_offset
#             if line_idx >= len(state.edited_lines):
#                 break

#             line = state.edited_lines[line_idx]

#             if line_idx == state.cursor_y and state.mode == Mode.EDIT:
#                 stdscr.attron(curses.A_REVERSE)
#                 stdscr.addstr(start_y + i, 0, line[:width-1])
#                 stdscr.attroff(curses.A_REVERSE)
#             else:
#                 stdscr.addstr(start_y + i, 0, line[:width-1])


class Presenter:
    """Presenter class for user interaction and displaying information."""

    def __init__(self):
        self._console = Console()
        self._session = self._create_session()
    

    def _create_session(self):
        kb = KeyBindings()

        @kb.add("a")
        def _(event):
            event.app.exit(result="a")

        @kb.add("e")
        def _(event):
            event.app.exit(result="e")

        @kb.add("s")
        def _(event):
            event.app.exit(result="s")

        @kb.add("q")
        def _(event):
            event.app.exit(result="q")

        style = Style.from_dict({
            "bottom-toolbar": "bg:#222222 #cccccc",
        })

        def toolbar():
            return "a: Accept | e: Edit | s: Skip | q: Quit"

        return PromptSession(
            key_bindings=kb,
            style=style,
            bottom_toolbar=toolbar,
        )
        
    def get_user_approval(self, doc: DocstringPresentationModel) -> UserResponseModel:
        """
        Gets user approval for the generated documentation.
        Args:
            doc: The generated documentation model.
        Returns:
            A UserResponseModel.
        """
        while True:
            response = self.interact(doc)
            if response == USER_RESPONSES[UserResponse.QUIT]:
                return UserResponseModel(doc_model=None, response=UserResponse.QUIT)
            if response == USER_RESPONSES[UserResponse.ACCEPT]:
                return UserResponseModel(doc_model=doc, response=UserResponse.ACCEPT)
            if response == USER_RESPONSES[UserResponse.SKIP]:
                return UserResponseModel(doc_model=doc, response=UserResponse.SKIP)
            if response == USER_RESPONSES[UserResponse.EDIT]:
                try:
                    doc.new_docstring.lines = self.edit_text_inline(
                        doc.new_docstring.lines
                    )
                except Exception as e:
                    logger.info(e)
                continue

    def get_toolbar(self):
        return (
            " Ctrl+S: Accept | "
            "Esc: Cancel | "
            "Ctrl+C: Abort"
        )
    
    def edit_text_inline(self, initial_text: List[str]) -> List[str] | None:
        """
        Opens the default text editor with the initial text for editing.
        """
        kb = KeyBindings()

        @kb.add("c-s") 
        def _(event):
            event.app.exit(result=event.app.current_buffer.text)

        @kb.add("escape")
        def _(event):
            event.app.exit(result=None)
            
        session = PromptSession(
            multiline=True,
            style=docstring_style,
            key_bindings=kb,
            bottom_toolbar=self.get_toolbar,
            editing_mode=EditingMode.VI
        )

        text = session.prompt(
            message="Edit docstring:\n",
            default="".join(initial_text),
        )

        if text is None:
            return None

        return text.splitlines(keepends=True)

    def print_error(self, message: str):
        """Prints an error message."""
        self._console.print(
            f"[bold red]Error:[/bold red] {escape(message)}", style="red"
        )

    def print_success(self, message: str):
        """Prints a success message."""
        self._console.print(
            f"[bold green]Success:[/bold green] {message}", style="green"
        )

    def decorate_slow_task_synchronous(
        self, task_description: str, slow_task: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """Decorates a slow task with a spinner.

        Args:
            task_description (str): Description of the task being performed.
            slow_task (Callable[..., Any]): The slow task to be executed.

        Raises:
            RuntimeError: If the slow task fails.

        Returns:
            Any: The result of the slow task.
        """
        spinner_name = "star"
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
        ):
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
            raise RuntimeError(result_container["exception"])

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
        ):
            try:
                result = await async_slow_task(*args, **kwargs)
                return result
            except Exception as e:
                self.print_error(f"Asynchronous task failed: {e}")
                raise  # Re-raise the exception after printing error

    def get_blue_prompt(self, message: str) -> str:
        """
        Shows a prompt_toolkit prompt with a blue background applied to the input area.
        """
        answer = prompt(message=message, style=blue_background_style)
        return answer

    def interact(self, doc: DocstringPresentationModel) -> str:
        """
        Interacts with the user to accept, edit, skip, or quit the documentation generation.
        """
        self._console.print("\n")
        self._console.clear()
        self._console.print(Rule(style="grey69", title="Source"))
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="left")
        grid.add_column(justify="center")

        grid.add_row(
            f"[grey69]File:[/grey69] [yellow]{doc.file_path or 'unknown'}",
            f"[grey69]Qualified Name:[/grey69] [magenta]{doc.qualified_name}[/magenta]",
            f"[grey69]Line:[/grey69] [cyan]{doc.new_docstring.start_line or 'unknown'}",
        )
        self._console.print(grid)
        self._console.print(f"[grey69]Function:[/grey69] [grey]{escape(doc.signature)}")

        if doc.existing_docstring:
            current_lines = "\n".join(doc.existing_docstring.lines)
            self._console.print("[grey69]Existing Docstring:")
            self._console.print(f"[pale_green1]{escape(current_lines.strip())}")
        self._console.print(Rule(style="grey69", title="Generated Docstring"))
        formatted_doc = "".join(doc.new_docstring.lines if doc.new_docstring.lines else [""]).strip()
        self._console.print(f"[green]{escape(formatted_doc)}")
        self._console.print(Rule(style="grey69"))

        # result = self.get_blue_prompt(
        #     f"Accept ({ACCEPT}), Edit ({EDIT}), Skip ({SKIP}), Quit ({QUIT}): "
        # )
        result = self._session.prompt("> ")
        self._console.clear()
        return result.strip().lower()

    def clear_console(self):
        """
        Clears the console output.
        """
        self._console.clear()
