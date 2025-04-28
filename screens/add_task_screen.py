"""Modal screen for adding a new task."""

from textual.app import ComposeResult
from textual.containers import Container 
from textual.screen import ModalScreen 
from textual.widgets import Input, Button, Label, Select # Import Select
from typing import Optional, Dict, List, Tuple, Any # Import List, Tuple, Any

from AI_Pair_Programming_Task_Manager import Task # Import Task for type hinting

# Define options for Select widgets (copied from EditTaskScreen for independence)
# Could potentially be moved to a shared constants file later
STATUS_OPTIONS: list[tuple[str, str]] = [
    ("To Do", "To Do"), ("In Progress", "In Progress"), ("Done", "Done"), ("Blocked", "Blocked"),
]
PRIORITY_OPTIONS: list[tuple[str, str]] = [
    ("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Critical", "Critical"),
]
TYPE_OPTIONS: list[tuple[str, str]] = [
    ("Epic", "Epic"), ("Story", "Story"), ("Task", "Task"), ("Bug", "Bug"),
]
NO_PARENT_VALUE = "__NONE__"

class AddTaskScreen(ModalScreen[Optional[Dict[str, Any]]]): # Update return type hint
    """Screen with a form to add a new task.
    
    Allows setting title, description, status, priority, type, and parent.
    Dismisses with a dictionary of new task details or None if cancelled.
    """
    
    DEFAULT_CSS = """
    AddTaskScreen > Container {
        width: auto;
        height: auto;
        max-width: 80%;
        max-height: 80%;
        border: thick $accent;
        padding: 1 2;
        background: $panel;
    }
    #add-task-dialog > * {
        margin-bottom: 1;
    }
    #add-task-buttons {
        margin-top: 1;
        align: center;
        width: 100%;
    }
    #add-task-buttons Button {
        margin-left: 1;
        margin-right: 1;
    }
    Select {
        width: 100%;
    }
    """

    def __init__(self, all_tasks: List[Task]) -> None:
        """Initialize the add screen.
        
        Args:
            all_tasks: List of all current tasks (for parent selection).
        """
        super().__init__()
        self.all_tasks = all_tasks
        # Prepare parent options
        self.parent_options: list[tuple[str, str]] = [
            ("(No Parent)", NO_PARENT_VALUE)
        ]
        self.parent_options.extend(
            (f"{t.id[:4]}...: {t.title}", t.id)
            for t in self.all_tasks
        )

    def compose(self) -> ComposeResult:
        with Container(id="add-task-dialog"):
            yield Label("Add New Task", id="add-task-title")
            yield Input(placeholder="Title", id="add-task-input-title")
            yield Input(placeholder="Description (Optional)", id="add-task-input-desc")
            yield Label("Status:")
            yield Select(options=STATUS_OPTIONS, value="To Do", id="add-task-select-status") # Default: To Do
            yield Label("Priority:")
            yield Select(options=PRIORITY_OPTIONS, value="Medium", id="add-task-select-priority") # Default: Medium
            yield Label("Type:")
            yield Select(options=TYPE_OPTIONS, value="Task", id="add-task-select-type") # Default: Task
            yield Label("Parent Task:")
            yield Select(options=self.parent_options, value=NO_PARENT_VALUE, id="add-task-select-parent") # Default: No Parent
            
            with Container(id="add-task-buttons"):
                yield Button("Save", variant="primary", id="add-task-save")
                yield Button("Cancel", id="add-task-cancel")

    def on_mount(self) -> None:
        """Focus the title input on mount."""
        self.query_one("#add-task-input-title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-task-cancel":
            self.dismiss(None) # Indicate cancellation
        elif event.button.id == "add-task-save":
            title_input = self.query_one("#add-task-input-title", Input)
            desc_input = self.query_one("#add-task-input-desc", Input)
            status_select = self.query_one("#add-task-select-status", Select)
            priority_select = self.query_one("#add-task-select-priority", Select)
            type_select = self.query_one("#add-task-select-type", Select)
            parent_select = self.query_one("#add-task-select-parent", Select)
            
            if not title_input.value:
                self.app.bell()
                self.app.notify("Title cannot be empty.", severity="error", title="Validation Error")
                title_input.focus()
                return

            # Basic check for selects - assumes they have a value if options exist
            if status_select.value is None or priority_select.value is None or type_select.value is None or parent_select.value is None:
                self.app.bell()
                self.app.notify("A selection value is missing. Please ensure all dropdowns are set.", severity="error", title="Validation Error")
                return
                
            # Get parent ID, handling NO_PARENT_VALUE
            selected_parent_id = parent_select.value
            parent_id = selected_parent_id if selected_parent_id != NO_PARENT_VALUE else None

            new_task_details = {
                "title": title_input.value,
                "description": desc_input.value,
                "status": status_select.value,
                "priority": priority_select.value,
                "task_type": type_select.value,
                "parent_id": parent_id
            }
            # Dismiss the screen, returning the details
            self.dismiss(new_task_details) 