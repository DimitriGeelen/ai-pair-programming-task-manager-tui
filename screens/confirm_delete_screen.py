from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Label

# --- Confirm Delete Screen ---
class ConfirmDeleteScreen(ModalScreen[bool]): # Return bool on dismiss
    """Screen to confirm deleting a task."""

    def __init__(self, task_title: str) -> None:
        super().__init__()
        self.task_title = task_title

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Really delete task '{self.task_title}'?"),
            Container(
                Button("Delete", variant="error", id="delete-confirm"),
                Button("Cancel", id="delete-cancel"),
                id="confirm-delete-buttons"
            ),
            id="confirm-delete-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-confirm":
            self.dismiss(True) # Confirm deletion
        else:
            self.dismiss(False) # Cancel deletion 