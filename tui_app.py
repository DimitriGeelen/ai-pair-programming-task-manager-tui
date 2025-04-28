"""
Main Textual application file for the AI Pair Programming Task Manager.
"""

# Imports will go here (Textual, TaskManager, etc.)
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Label, Static # Import DataTable explicitly if not already
from textual.containers import Container # For layout
from textual.screen import Screen, ModalScreen # Import Screen types
from textual.widgets import Input # Widgets for the modal
from textual.message import Message # Import Message base class
from textual.renderables.styled import Styled # For styling table cells
from textual.color import Color # For styling
from textual.reactive import reactive # Import reactive for dynamic updates
# Import our task manager logic
from AI_Pair_Programming_Task_Manager import TaskManager, Task 
from typing import Optional, Dict, List # Ensure List is imported
# --- Import Screens ---
from screens.add_task_screen import AddTaskScreen
from screens.confirm_delete_screen import ConfirmDeleteScreen
from screens.helpers import style_status, refresh_task_table, cycle_task_status, cycle_task_priority # Import new helpers
from screens.edit_task_screen import EditTaskScreen # Import EditTaskScreen

# --- Confirm Delete Screen ---
# Removed class definition

# Main App Class will go here
class TaskManagerApp(App):
    """The main Textual application for managing tasks."""
    
    # CSS_PATH = "app.css" # We might add CSS later
    BINDINGS = [
        ("q", "quit", "Quit"), 
        ("a", "add_task", "Add Task"),
        ("e", "edit_task", "Edit Selected Task"), 
        ("d", "delete_task", "Delete Selected Task"),
        ("s", "cycle_status", "Cycle Status Forward"),
        ("p", "toggle_pause", "Pause/Resume"),
        ("+", "cycle_priority", "Cycle Priority Up"),
        # Filtering Bindings
        ("0", "filter_all", "Filter: All"),
        ("1", "filter_epics", "Filter: Epics"),
        ("2", "filter_stories", "Filter: Stories"),
        ("3", "filter_tasks", "Filter: Tasks"),
        ("4", "filter_bugs", "Filter: Bugs")
    ] 
    
    # Define the order of statuses for cycling
    STATUS_CYCLE = ["To Do", "In Progress", "Done", "Blocked"]
    PRIORITY_CYCLE = ["Low", "Medium", "High", "Critical"]
    
    selected_task_id: Optional[str] = None # Add instance variable to store selected ID
    is_paused: reactive[bool] = reactive(False) # Add reactive paused state
    current_filter: reactive[Optional[str]] = reactive(None) # Add reactive filter state
    
    def __init__(self, task_file_path="tasks.json"):
        super().__init__()
        self.task_manager = TaskManager(file_path=task_file_path)
        # print(f"TUI App initialized with task manager for {task_file_path}") # Debug
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        # Main content area will go here later
        yield DataTable(id="task-list", cursor_type="row") # Ensure row cursor
        yield Static(id="task-details-view", expand=True) # Add static view for details
        yield Footer()
        
    def on_mount(self) -> None:
        """Called when the app is mounted. Load initial data."""
        table = self.query_one(DataTable)
        # Add columns (adjust types and labels as needed)
        table.add_columns("ID", "Title", "Status", "Priority", "Type")
        # Load initial tasks
        tasks = self.task_manager.tasks
        for task in tasks:
            # Add task data as a row
            # Ensure data matches column order and type
            table.add_row(
                task.id,
                task.title, 
                style_status(task.status), # Use imported function
                task.priority, 
                task.task_type,
                key=task.id # Use task ID as the row key for later reference
            )
        # print(f"Mounted and loaded {len(tasks)} tasks into table.") # Debug

    def _refresh_task_table(self, filter_type: Optional[str] = None) -> None:
        """Wrapper method to refresh the task table using the helper function."""
        table = self.query_one(DataTable)
        tasks = self.task_manager.tasks
        # Call the helper function with the necessary arguments
        refresh_task_table(table=table, tasks=tasks, filter_type=filter_type)
        # Original print statement can be removed or kept for app-level logging
        # print(f"Refreshed table. Displaying {table.row_count} tasks (Filter: {filter_type or 'All'})")

    # --- Message Handlers ---
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle task selection in the table."""
        # event.row_key is the task.id we set when adding rows
        self.selected_task_id = event.row_key
        print(f"Selected Task ID: {self.selected_task_id}") # Debug
        # TODO: Update status bar or details view later based on selection
        # --- Update the details view --- 
        details_view = self.query_one("#task-details-view", Static)
        selected_task = self.task_manager.get_task(self.selected_task_id)
        if selected_task:
            # Format the task details nicely
            details_text = (
                f"[b]ID:[/b] {selected_task.id}\n"
                f"[b]Title:[/b] {selected_task.title}\n"
                f"[b]Status:[/b] {selected_task.status}\n"
                f"[b]Priority:[/b] {selected_task.priority}\n"
                f"[b]Type:[/b] {selected_task.task_type}\n"
                f"[b]Created:[/b] {selected_task.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"[b]Updated:[/b] {selected_task.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"[b]Description:[/b]\n{selected_task.description}"
            )
            details_view.update(details_text)
        else:
            # Clear details view if task not found (e.g., after deletion)
            details_view.update("")

    # --- Watchers --- 
    def watch_is_paused(self, paused: bool) -> None:
        """Called when the is_paused reactive variable changes."""
        # Update the header/footer or some indicator to show paused status
        # For simplicity, let's update the app title for now
        status_text = "[PAUSED]" if paused else ""
        self.title = f"Task Manager {status_text}".strip()
        # We might disable certain actions when paused later

    def watch_current_filter(self, new_filter: Optional[str]) -> None:
        """Called when the current_filter changes. Refresh the table."""
        # This now calls the wrapper method, which calls the helper
        self._refresh_task_table(filter_type=new_filter)
        # self.notify(f"Filter set to: {new_filter or 'All'}") # Optional notification

    # --- Action Handlers --- 
    def action_quit(self) -> None:
        """An action to quit the application."""
        self.exit()
        
    def action_add_task(self) -> None:
        """Action to push the Add Task screen."""
        def add_task_callback(task_details: Optional[Dict]):
            """Callback function after AddTaskScreen is dismissed."""
            if task_details:
                try:
                    new_id = self.task_manager.add_task(task_details)
                    # Use notify for better feedback
                    self.notify(f"Added task '{task_details.get('title', new_id)}'.")
                    self._refresh_task_table(filter_type=self.current_filter) # Refresh with current filter
                    # Optional: Select the newly added row?
                    # try:
                    #    new_index = self.query_one(DataTable).get_row_index(new_id)
                    #    self.query_one(DataTable).cursor_coordinate = (new_index, 0)
                    # except KeyError:
                    #    pass # Row might not be visible due to filtering
                except Exception as e:
                    logger.error(f"Error adding task: {e}") 
                    self.bell() 
                    self.notify(f"An error occurred while adding the task.", severity="error")
            else:
                self.notify("Add cancelled.") # User cancelled
                    
        # Pass the list of all tasks to the AddTaskScreen constructor
        all_tasks = self.task_manager.tasks
        self.push_screen(AddTaskScreen(all_tasks), add_task_callback)

    def action_edit_task(self) -> None:
        """Action to push the Edit Task screen for the selected task.
        
        Checks if a task is selected, retrieves the task data, 
        pushes the EditTaskScreen, and handles the callback to update
        the task via the TaskManager and refresh the UI.
        """
        if self.selected_task_id is None:
            self.bell()
            self.notify("No task selected to edit.", severity="warning")
            return
            
        task_to_edit = self.task_manager.get_task(self.selected_task_id)
        
        if not task_to_edit:
            self.bell()
            self.notify(f"Could not find selected task (ID: {self.selected_task_id}). Please refresh or select another.", severity="error")
            self.selected_task_id = None # Clear selection if task disappeared
            return

        def edit_task_callback(updated_details: Optional[Dict]):
            """Callback function after EditTaskScreen is dismissed."""
            if updated_details:
                try:
                    success = self.task_manager.update_task(self.selected_task_id, updated_details)
                    if success:
                        self.notify(f"Task '{updated_details.get('title', self.selected_task_id)}' updated.")
                        self._refresh_task_table(filter_type=self.current_filter) # Refresh table
                        # Update details view by simulating re-selection
                        self.on_data_table_row_selected(DataTable.RowSelected(self.query_one(DataTable)))
                    else:
                        # This case might happen if the task was deleted *while* the edit screen was open
                        self.bell()
                        self.notify(f"Failed to update task (ID: {self.selected_task_id}). It might have been deleted.", severity="error")
                        self.selected_task_id = None # Clear selection
                        self._refresh_task_table(filter_type=self.current_filter) # Refresh anyway
                except Exception as e:
                    logger.error(f"Error updating task {self.selected_task_id}: {e}")
                    self.bell()
                    self.notify(f"An error occurred while updating the task.", severity="error")
            else:
                self.notify("Edit cancelled.") # User cancelled
                    
        # Pass the list of all tasks to the EditTaskScreen constructor
        all_tasks = self.task_manager.tasks
        self.push_screen(EditTaskScreen(task_to_edit, all_tasks), edit_task_callback)

    def action_delete_task(self) -> None:
        """Action to delete the currently selected task."""
        if self.selected_task_id is None:
            self.bell() # No task selected
            return
            
        # TODO: Add confirmation dialog in step -2802
        
        task_to_delete = self.task_manager.get_task(self.selected_task_id)
        if not task_to_delete: # Should not happen, but check anyway
            self.bell()
            return

        def confirm_delete_callback(confirm: bool):
            if confirm:
                try:
                    success = self.task_manager.delete_task(self.selected_task_id)
                    if success:
                        print(f"Deleted task {self.selected_task_id}") 
                        self.selected_task_id = None 
                        self._refresh_task_table(filter_type=self.current_filter) # Refresh with current filter
                        self.query_one("#task-details-view", Static).update("Task deleted.") 
                    else:
                        print(f"Error: Failed to find task {self.selected_task_id} during delete confirmation.")
                        self.bell()
                except Exception as e:
                    print(f"Error deleting task: {e}") # Log error
                    self.bell() # Error feedback
            else:
                print("Deletion cancelled.") # Debug
        
        self.push_screen(ConfirmDeleteScreen(task_to_delete.title), confirm_delete_callback) # Pass title only

    def _cycle_selected_task_status(self, reverse: bool = False) -> None:
        """Wrapper method to cycle status using the helper function."""
        # Call the helper function, passing the app instance (self)
        cycle_task_status(self, reverse=reverse)

    def action_cycle_status(self) -> None:
        """Cycle the selected task's status forward."""
        # This now calls the wrapper, which calls the helper
        self._cycle_selected_task_status(reverse=False)
        
    def action_toggle_pause(self) -> None:
        """Toggle the application's paused state."""
        self.is_paused = not self.is_paused

    def _cycle_selected_task_priority(self) -> None:
        """Wrapper method to cycle priority using the helper function."""
        # Call the helper function, passing the app instance (self)
        cycle_task_priority(self)

    def action_cycle_priority(self) -> None:
        """Cycle the selected task's priority up."""
        # This now calls the wrapper, which calls the helper
        self._cycle_selected_task_priority()

    # --- Filter Actions ---
    def action_filter_all(self) -> None: self.current_filter = None
    def action_filter_epics(self) -> None: self.current_filter = "Epic"
    def action_filter_stories(self) -> None: self.current_filter = "Story"
    def action_filter_tasks(self) -> None: self.current_filter = "Task"
    def action_filter_bugs(self) -> None: self.current_filter = "Bug"

    # Optional: Implement backward cycling if binding is added
    # def action_cycle_status_backward(self) -> None:
    #     """Cycle the selected task's status backward."""
    #     self._cycle_selected_task_status(reverse=True)

# Entry point will go here
if __name__ == "__main__":
    app = TaskManagerApp()
    app.run() 