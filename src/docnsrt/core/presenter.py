"""This module contains functions to display text to the CLI."""

from enum import Enum
import logging
from dataclasses import dataclass
from rich.markup import escape
from rich.console import Console
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.filters import Condition
from docnsrt.core.models import DocstringPresentationModel

logger = logging.getLogger(__name__)


class UserResponse(Enum):
    """
    Enumeration for user responses.
    """

    QUIT = 1
    ACCEPT = 2
    EDIT = 3
    SKIP = 4


USER_RESPONSES = {
    UserResponse.QUIT: "quit",
    UserResponse.ACCEPT: "accept",
    UserResponse.EDIT: "exit",
    UserResponse.SKIP: "skip",
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


class _PresenterApp:
    def __init__(self, doc: DocstringPresentationModel):
        self.doc = doc
        self.result = None
        self.edit_mode = False

        self.editor = TextArea(
            text="".join(doc.new_docstring.lines or [""]),
            multiline=True,
            scrollbar=True,
            focusable=True,
            style="class:generated",
        )
        self.editor_footer = Window(
            content=FormattedTextControl(
                text=HTML("<b>Ctrl+S: Save &amp; Exit | Esc: Cancel</b>")
            ),
            height=1,
            style="class:footer",
        )

        self.editor_container = HSplit(
            [
                self.editor,
                Window(height=1, char="-"),
                self.editor_footer,
            ]
        )

        # --- Header ---
        self.header = Window(
            content=FormattedTextControl(text=self._get_header_text()),
            wrap_lines=True,
            height=None,
        )

        # --- Existing docstring ---
        existing_text = (
            "\n".join(doc.existing_docstring.lines)
            if doc.existing_docstring
            else "(none)"
        )

        self.existing = TextArea(
            text=existing_text,
            read_only=True,
            scrollbar=True,
            focusable=False,
            style="class:existing",
        )

        # --- Editable generated docstring ---
        generated_text = "".join(doc.new_docstring.lines or [""])

        self.generated = TextArea(
            text=generated_text,
            multiline=True,
            read_only=True,
            scrollbar=True,
            focusable=False,
            style="class:generated",
        )

        # --- Footer ---
        self.footer = Window(
            content=FormattedTextControl(
                text=HTML(
                    "<b>a</b>: Accept | "
                    "<b>e</b>: Edit | "
                    "<b>s</b>: Skip | "
                    "<b>q</b>: Quit"
                )
            ),
            height=1,
            style="class:footer",
        )

        self.view_container = HSplit(
            [
                self.header,
                Window(height=1, char="-"),
                self.existing,
                Window(height=1, char="-"),
                self.generated,
                Window(height=1, char="-"),
                self.footer,
            ]
        )
        # --- Keybindings ---
        kb = KeyBindings()

        @kb.add("q")
        def _(event):
            if not self.edit_mode:
                self.result = (QUIT, None)
                event.app.exit()

        @kb.add("a")
        def _(event):
            if not self.edit_mode:
                self.result = (ACCEPT, self.doc.new_docstring.lines)
                event.app.exit()

        @kb.add("s")
        def _(event):
            if not self.edit_mode:
                self.result = (SKIP, None)
                event.app.exit()

        @kb.add("e")
        def _(event):
            if not self.edit_mode:
                self.edit_mode = True
                event.app.layout.focus(self.editor)

        # ESC to leave edit mode
        @kb.add("escape")
        def _(event):
            if self.edit_mode:
                self.edit_mode = False
                event.app.layout.focus(self.generated)

        @kb.add("c-s")
        def _(event):
            if self.edit_mode:
                text = self.editor.text
                if not text.endswith("\n"):
                    text += "\n"

                lines = text.splitlines(keepends=True)

                self.result = (EDIT, lines)
                event.app.exit()

        root_container = HSplit(
            [
                ConditionalContainer(
                    self.view_container, filter=Condition(self._is_view_mode)
                ),
                ConditionalContainer(
                    self.editor_container, filter=Condition(self._is_edit_mode)
                ),
            ]
        )

        self.app = Application(
            layout=Layout(root_container, focused_element=self.footer),
            key_bindings=kb,
            full_screen=True,
            style=Style.from_dict(
                {
                    "label": "bg:default #ffff66",
                    "file.path": "bg:default #00ffff",
                    "function": "bg:default #ffff66",
                    "existing": "bg:default #206020",
                    "generated": "bg:default #0000ff",
                    "footer": "bg:#aaaaaa #000000",
                }
            ),
        )

    def _get_header_text(self):
        doc = self.doc
        return FormattedText(
            [
                ("class:label.file", "File: "),
                ("", str(doc.file_path or "unknown")),
                ("", "    "),
                ("class:label.name", "Name: "),
                ("", str(doc.qualified_name)),
                ("", "    "),
                ("class:label.line", "Line: "),
                ("", str(doc.new_docstring.start_line or "unknown")),
                ("\n", "\n"),
                ("class:label.func", "Function: "),
                ("", str(doc.signature)),
            ]
        )

    def _is_edit_mode(self):
        return self.edit_mode

    def _is_view_mode(self):
        return not self.edit_mode

    def run(self):
        """
        Runs the prompt toolkit app
        """
        self.app.run()
        return self.result


class Presenter:
    """Presenter class for user interaction and displaying information."""

    def __init__(self):
        pass

    def get_user_approval(
        self, doc: DocstringPresentationModel
    ) -> UserResponseModel | None:
        """
        Gets user approval for the generated documentation.
        Args:
            doc: The generated documentation model.
        Returns:
            A UserResponseModel.
        """
        return self.interact(doc=doc)

    def print_error(self, message: str):
        """Prints an error message."""
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {escape(message)}", style="red")

    def print_success(self, message: str):
        """Prints a success message."""
        console = Console()
        console.print(f"[bold green]Success:[/bold green] {message}", style="green")

    def interact(self, doc: DocstringPresentationModel) -> UserResponseModel | None:
        """
        Interacts with the user to accept, edit, skip, or quit the documentation generation.
        """
        app = _PresenterApp(doc)
        action, text = app.run()

        if action == QUIT:
            return UserResponseModel(doc_model=None, response=UserResponse.QUIT)
        if action == ACCEPT:
            return UserResponseModel(doc_model=doc, response=UserResponse.ACCEPT)
        if action == SKIP:
            return UserResponseModel(doc_model=doc, response=UserResponse.SKIP)
        if action == EDIT:
            doc.new_docstring.lines = text
            return UserResponseModel(doc_model=doc, response=UserResponse.ACCEPT)
        return None
