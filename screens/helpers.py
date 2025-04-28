from textual.renderables.styled import Styled
from textual.color import Color # Keep Color import if needed for more complex styling
from textual.widgets import DataTable # Import DataTable
from textual.app import App # Import App
from AI_Pair_Programming_Task_Manager import Task, TaskManager # Import TaskManager
from typing import List, Optional, TYPE_CHECKING, Dict, Set
import logging

# Avoid circular import for type hints
if TYPE_CHECKING:
    from tui_app import TaskManagerApp # Use string hint later if needed

def style_status(status: str) -> Styled:
    """Return a Styled object for the status string with appropriate color/style.
    
    Args:
        status: The status string.
        
    Returns:
        A Textual Styled object.
    """
    style = ""
    if status == "To Do":
        style = "dim" # Less prominent
    elif status == "In Progress":
        style = "bold yellow"
    elif status == "Done":
        style = "bold green"
    elif status == "Blocked":
        style = "bold red"
    return Styled(status, style)

def _add_rows_recursively(
    table: DataTable, 
    parent_id: Optional[str], 
    tasks_by_parent: Dict[Optional[str], List[Task]],
    tasks_by_id: Dict[str, Task],
    added_keys: Set[str],
    level: int = 0
) -> None:
    """Recursively adds task rows to the table, indenting children.
    
    Args:
        table: The DataTable to add rows to.
        parent_id: The ID of the parent task whose children should be added.
        tasks_by_parent: Dictionary mapping parent IDs to lists of child Tasks.
        tasks_by_id: Dictionary mapping task IDs to Task objects.
        added_keys: Set of task IDs already added to the table (to prevent duplicates).
        level: The current depth in the hierarchy for indentation.
    """
    children = tasks_by_parent.get(parent_id, [])
    indent = "  " * level # Two spaces per level
    for task in sorted(children, key=lambda t: t.created_at): # Sort children, e.g., by creation time
        if task.id not in added_keys:
            # Add the row with indented title
            table.add_row(
                task.id,
                f"{indent}{task.title}", # Indented title
                style_status(task.status),
                task.priority, 
                task.task_type,
                key=task.id
            )
            added_keys.add(task.id)
            # Recursively add children of this task
            _add_rows_recursively(table, task.id, tasks_by_parent, tasks_by_id, added_keys, level + 1)

def refresh_task_table(table: DataTable, tasks: List[Task], filter_type: Optional[str] = None) -> None:
    """Clears and re-populates the task table hierarchically based on parent_id.
    
    Handles building the tree, adding rows recursively with indentation, 
    applying basic filtering, and restoring cursor position.

    Args:
        table: The DataTable widget to update.
        tasks: The list of ALL Task objects.
        filter_type: Optional task type string to filter by (applied AFTER hierarchy).
    """
    
    # --- Build Tree Structure --- 
    tasks_by_id: Dict[str, Task] = {task.id: task for task in tasks}
    tasks_by_parent: Dict[Optional[str], List[Task]] = {}
    root_tasks: List[Task] = []
    
    for task in tasks:
        parent_id = task.parent_id
        if parent_id not in tasks_by_parent:
            tasks_by_parent[parent_id] = []
        tasks_by_parent[parent_id].append(task)
        # Check if it's a root task (no parent ID or parent doesn't exist)
        # Note: This handles orphaned tasks gracefully
        if parent_id is None or parent_id not in tasks_by_id:
             root_tasks.append(task)
             # If an orphan had parent_id set, ensure it's treated as root
             if parent_id is not None:
                 task.parent_id = None # Correct the data structure in memory for hierarchy building
                 if parent_id in tasks_by_parent:
                     # Clean up tasks_by_parent if orphan was moved
                     tasks_by_parent[parent_id] = [t for t in tasks_by_parent[parent_id] if t.id != task.id]
                     if not tasks_by_parent[parent_id]:
                         del tasks_by_parent[parent_id]
                 # Add to None parent list if not already there implicitly
                 if None not in tasks_by_parent: tasks_by_parent[None] = []
                 if task not in tasks_by_parent[None]: tasks_by_parent[None].append(task)
                 
    # --- Populate Table --- 
    current_cursor_row_key = None
    if table.cursor_coordinate:
         try:
             current_cursor_row_key = table.get_row_at(table.cursor_coordinate.row)[0] # Get ID from first column
         except IndexError:
             current_cursor_row_key = None # Cursor was likely invalid
             
    table.clear()
    added_keys: Set[str] = set()
    # Start recursion from root tasks (those with parent_id=None or orphaned)
    _add_rows_recursively(table, None, tasks_by_parent, tasks_by_id, added_keys, level=0)
    
    # --- Filtering (Simple Approach) ---
    # This simple filter removes rows that don't match, potentially breaking visual hierarchy.
    # A better approach would involve greying out non-matching rows or filtering 
    # the initial `tasks` list while preserving ancestors of matching tasks.
    if filter_type:
        rows_to_remove = []
        for row_key in list(table.rows.keys()): # Iterate over copy of keys
            task = tasks_by_id.get(str(row_key))
            if task and task.task_type != filter_type:
                rows_to_remove.append(row_key)
        for key in rows_to_remove:
            if key in table.rows:
                 table.remove_row(key)
                 if key in added_keys:
                      added_keys.remove(key)

    # --- Restore Cursor --- 
    new_cursor_row_index = None
    if current_cursor_row_key and current_cursor_row_key in added_keys:
        try:
            new_cursor_row_index = table.get_row_index(current_cursor_row_key)
        except KeyError:
             new_cursor_row_index = None # Row key not found after potential filtering
             
    if new_cursor_row_index is not None:
        # Ensure the column index is valid (use 0 if previous was out of bounds)
        col = table.cursor_coordinate.column if table.cursor_coordinate and table.cursor_coordinate.column < table.column_count else 0
        table.cursor_coordinate = (new_cursor_row_index, col)
    elif table.row_count > 0:
        # Move to first row if previous selection is gone or invalid
        col = table.cursor_coordinate.column if table.cursor_coordinate and table.cursor_coordinate.column < table.column_count else 0
        table.cursor_coordinate = (0, col) 
        
    # print(f"Refreshed table hierarchically. Displaying {len(added_keys)} tasks (Filter: {filter_type or 'All'})")

def cycle_task_status(app: 'TaskManagerApp', reverse: bool = False) -> None:
    """Cycles the status of the app's currently selected task.
    
    Retrieves the selected task, calculates the next status in the cycle 
    (defined in app.STATUS_CYCLE), updates the task via TaskManager, 
    refreshes the UI, and shows notifications.
    
    Args:
        app: The main TaskManagerApp instance.
        reverse: If True, cycle status backwards.
    """
    if app.selected_task_id is None:
        app.bell()
        app.notify("No task selected to cycle status.", severity="warning")
        return
        
    task = app.task_manager.get_task(app.selected_task_id)
    if not task:
        app.bell()
        app.notify(f"Selected task {app.selected_task_id} not found.", severity="error")
        return
        
    try:
        current_index = app.STATUS_CYCLE.index(task.status)
    except ValueError:
        current_index = -1 # Default to first status if current one not found
        
    step = -1 if reverse else 1
    next_index = (current_index + step) % len(app.STATUS_CYCLE)
    new_status = app.STATUS_CYCLE[next_index]
    
    updates = {"status": new_status}
    try:
        success = app.task_manager.update_task(app.selected_task_id, updates)
        if success:
            app.notify(f"Status updated to {new_status}")
            app._refresh_task_table(filter_type=app.current_filter) # Refresh table
            # Trigger details view update by simulating re-select
            # Ensure DataTable is imported if direct access is needed, otherwise rely on app method
            try:
                table = app.query_one(DataTable)
                app.on_data_table_row_selected(DataTable.RowSelected(table)) # Simulate re-select
            except Exception as e:
                # Log error if table query fails
                app.notify("Error updating details view after status change.", severity="error")
                logger.error(f"Error querying DataTable after status cycle: {e}") # Assuming logger is available
        else:
            app.bell()
            app.notify(f"Failed to update status for task {app.selected_task_id}.", severity="error")
    except Exception as e:
        logger.error(f"Error updating status for {app.selected_task_id}: {e}") # Assuming logger is available
        app.bell()
        app.notify("An error occurred while updating status.", severity="error")

def cycle_task_priority(app: 'TaskManagerApp') -> None:
    """Cycles the priority of the app's currently selected task upwards.

    Retrieves the selected task, calculates the next priority in the cycle 
    (defined in app.PRIORITY_CYCLE), updates the task via TaskManager, 
    refreshes the UI, and shows notifications.
    
    Args:
        app: The main TaskManagerApp instance.
    """
    if app.selected_task_id is None:
        app.bell()
        app.notify("No task selected to cycle priority.", severity="warning")
        return
        
    task = app.task_manager.get_task(app.selected_task_id)
    if not task:
        app.bell()
        app.notify(f"Selected task {app.selected_task_id} not found.", severity="error")
        return
        
    try:
        current_index = app.PRIORITY_CYCLE.index(task.priority)
    except ValueError:
        current_index = -1 # Default to Low if not found
    
    next_index = (current_index + 1) % len(app.PRIORITY_CYCLE)
    new_priority = app.PRIORITY_CYCLE[next_index]
    
    updates = {"priority": new_priority}
    try:
        success = app.task_manager.update_task(app.selected_task_id, updates)
        if success:
            app.notify(f"Priority updated to {new_priority}")
            app._refresh_task_table(filter_type=app.current_filter)
            # Trigger details view update by simulating re-select
            try:
                table = app.query_one(DataTable)
                app.on_data_table_row_selected(DataTable.RowSelected(table)) # Simulate re-select
            except Exception as e:
                app.notify("Error updating details view after priority change.", severity="error")
                logger.error(f"Error querying DataTable after priority cycle: {e}") # Assuming logger is available
        else:
            app.bell() 
            app.notify(f"Failed to update priority for task {app.selected_task_id}.", severity="error")
    except Exception as e:
        logger.error(f"Error updating priority for {app.selected_task_id}: {e}") # Assuming logger is available
        app.bell()
        app.notify("An error occurred while updating priority.", severity="error")

# Ensure logger is defined if used directly (e.g., import logging and get logger)
logger = logging.getLogger(__name__) 