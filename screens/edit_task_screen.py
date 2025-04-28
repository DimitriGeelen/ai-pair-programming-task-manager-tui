"""Modal screen for editing an existing task."""

from textual.app import ComposeResult
from textual.containers import Container 
from textual.screen import ModalScreen 
from textual.widgets import Input, Button, Label, Select # Import Select
from typing import Optional, Dict, Tuple, Any, List # Import List

from AI_Pair_Programming_Task_Manager import Task # Import Task for type hinting

# Define options for Select widgets based on Task Literals
# (Text, Value) - Text is displayed, Value is stored/returned
STATUS_OPTIONS: list[tuple[str, str]] = [
    ("To Do", "To Do"),
    ("In Progress", "In Progress"),
    ("Done", "Done"),
    ("Blocked", "Blocked"),
]

PRIORITY_OPTIONS: list[tuple[str, str]] = [
    ("Low", "Low"),
    ("Medium", "Medium"),
    ("High", "High"),
    ("Critical", "Critical"),
]

TYPE_OPTIONS: list[tuple[str, str]] = [
    ("Epic", "Epic"),
    ("Story", "Story"),
    ("Task", "Task"),
    ("Bug", "Bug"),
]

# Define a constant for the 'no parent' value
NO_PARENT_VALUE = "__NONE__"

class EditTaskScreen(ModalScreen[Optional[Dict[str, Any]]]): # Update return type hint
    """A modal screen for editing the details of an existing task.

    Allows modification of title, description, status, priority, type, and parent.
    Dismisses with a dictionary of updated details or None if cancelled.
    """
    
    DEFAULT_CSS = """
    EditTaskScreen > Container {
        width: auto;
        height: auto;
        max-width: 80%;
        max-height: 80%;
        border: thick $accent;
        padding: 1 2;
        background: $panel;
    }
    #edit-task-dialog > * {
        margin-bottom: 1;
    }
    #edit-task-buttons {
        margin-top: 1;
        align-horizontal: center;
        width: 100%;
    }
    #edit-task-buttons Button {
        margin-left: 1;
        margin-right: 1;
    }
    Select {
        width: 100%; /* Make selects take full width */
    }
    """ # Basic styling for the modal

    def __init__(self, task_to_edit: Task, all_tasks: List[Task]) -> None:
        """Initialize the edit screen.

        Args:
            task_to_edit: The Task object to be edited.
            all_tasks: A list of all tasks (used for parent selection).
        """
        super().__init__()
        self.task_to_edit = task_to_edit # Store the task object
        self.all_tasks = all_tasks # Store all tasks for parent selection
        
        # Prepare parent options, excluding the task itself
        self.parent_options: list[tuple[str, str]] = [
            ("(No Parent)", NO_PARENT_VALUE) # Special value for no parent
        ]
        self.parent_options.extend(
            (f"[{t.display_id}] {t.title}", t.id) # Display [display_id] and title, store UUID
            for t in self.all_tasks 
            if t.id != self.task_to_edit.id # Cannot be its own parent
            # TODO: Add check for circular dependency later if needed
        )

    def compose(self) -> ComposeResult:
        """Create the UI widgets for the edit form."""
        # Determine the initial value for parent Select
        current_parent_id = self.task_to_edit.parent_id if self.task_to_edit.parent_id else NO_PARENT_VALUE
        
        # Prefill inputs with existing task data
        with Container(id="edit-task-dialog"):
            yield Label("Edit Task", id="edit-task-title")
            yield Input(value=self.task_to_edit.title, id="edit-task-input-title")
            yield Input(value=self.task_to_edit.description, id="edit-task-input-desc")
            yield Label("Status:")
            yield Select(options=STATUS_OPTIONS, value=self.task_to_edit.status, id="edit-task-select-status")
            yield Label("Priority:")
            yield Select(options=PRIORITY_OPTIONS, value=self.task_to_edit.priority, id="edit-task-select-priority")
            yield Label("Type:")
            yield Select(options=TYPE_OPTIONS, value=self.task_to_edit.task_type, id="edit-task-select-type")
            yield Label("Parent Task:")
            yield Select(options=self.parent_options, value=current_parent_id, id="edit-task-select-parent")
            
            with Container(id="edit-task-buttons"):
                yield Button("Save", variant="primary", id="edit-task-save")
                yield Button("Cancel", id="edit-task-cancel")

    def on_mount(self) -> None:
        """Focus the title input when the screen is mounted."""
        self.query_one("#edit-task-input-title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for save or cancel.
        
        Validates input and dismisses the screen with updated task details
        or None if cancelled or validation fails.
        """
        if event.button.id == "edit-task-cancel":
            self.dismiss(None) # Indicate cancellation
        elif event.button.id == "edit-task-save":
            title_input = self.query_one("#edit-task-input-title", Input)
            desc_input = self.query_one("#edit-task-input-desc", Input)
            status_select = self.query_one("#edit-task-select-status", Select)
            priority_select = self.query_one("#edit-task-select-priority", Select)
            type_select = self.query_one("#edit-task-select-type", Select)
            parent_select = self.query_one("#edit-task-select-parent", Select)
            
            if not title_input.value:
                # TODO: Provide better feedback (e.g., highlight input)
                self.app.bell()
                self.app.notify("Title cannot be empty.", severity="error", title="Validation Error")
                title_input.focus()
                return # Prevent dismissal
                
            # Ensure Select widgets have values (should always have one if options exist)
            if status_select.value is None or priority_select.value is None or type_select.value is None or parent_select.value is None:
                 self.app.bell()
                 self.app.notify("A selection value is missing. Please ensure all dropdowns are set.", severity="error", title="Validation Error")
                 # Optionally focus the first problematic Select
                 return # Prevent dismissal

            # Get parent ID, converting our special value back to None
            selected_parent_id = parent_select.value
            parent_id = selected_parent_id if selected_parent_id != NO_PARENT_VALUE else None

            updated_task_details = {
                "title": title_input.value,
                "description": desc_input.value,
                "status": status_select.value, # Get value from Select
                "priority": priority_select.value, # Get value from Select
                "task_type": type_select.value, # Get value from Select
                "parent_id": parent_id # Use the selected parent ID (or None)
            }
            # Dismiss the screen, returning the updated details
            self.dismiss(updated_task_details) 