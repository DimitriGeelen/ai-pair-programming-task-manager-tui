# - Interaction: Handled via Textual event loop and components
# 
# Future Roadmap Considerations:
# - Explore Option 4 (Web UI) for enhanced accessibility and features.

# --- Implementation Starts Here ---

from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from typing import Optional, Literal, List
import uuid
import json
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get a logger for this module

@dataclass
class Task:
    """Represents a single task in the Task Manager."""
    """Represents a single task, encapsulating its properties and metadata.

    Attributes:
        id (str): Unique identifier for the task (UUID string).
        title (str): Short description or name of the task.
        description (str): More detailed description of the task.
        status (Literal): Current status (e.g., "To Do", "In Progress").
        priority (Literal): Priority level (e.g., "Low", "Medium", "High").
        task_type (Literal): Agile classification (e.g., "Epic", "Story", "Task").
        parent_id (Optional[str]): ID of the parent task, if any.
        created_at (datetime): Timestamp when the task was created.
        updated_at (datetime): Timestamp when the task was last updated.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: Literal["To Do", "In Progress", "Done", "Blocked"] = "To Do"
    priority: Literal["Low", "Medium", "High", "Critical"] = "Medium"
    task_type: Literal["Epic", "Story", "Task", "Bug"] = "Task"
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None # Allow None initially

    def __post_init__(self):
        """Ensure updated_at is set to created_at initially if not provided."""
        if self.updated_at is None:
            self.updated_at = self.created_at

# --- Other Classes/Functions will follow (TaskManager, JSON handling, etc.) ---

class TaskManager:
    """Manages the collection of tasks, including loading and saving."""
    
    def __init__(self, file_path: str = "tasks.json"):
        """Initializes the TaskManager, loading tasks from the specified file.
        
        Args:
            file_path (str): The path to the JSON file storing tasks. 
                             Defaults to 'tasks.json'.
        """
        self._file_path = file_path
        self._tasks: list[Task] = load_tasks_from_json(self._file_path)
        # print(f"TaskManager initialized. Loaded {len(self._tasks)} tasks from {self._file_path}") # Optional debug

    @property
    def tasks(self) -> list[Task]:
        """Provides read-only access to the list of tasks."""
        return self._tasks
    
    # --- Methods for add, get, update, delete will follow ---
    def add_task(self, task_details: dict) -> str:
        """Creates a new task, adds it to the list, saves, and returns the ID.
        
        Args:
            task_details: A dictionary containing the initial details for the task
                          (e.g., title, description, status, priority, etc.).
                          'id', 'created_at', 'updated_at' will be ignored if present.
                          
        Returns:
            The unique ID (str) of the newly created task.
        """
        # Ensure required fields are present? Or rely on Task defaults?
        # For now, rely on Task defaults and provided details.
        
        # Create a new Task object, ignoring potential id/timestamps from input dict
        new_task = Task(
            title=task_details.get('title', ''),
            description=task_details.get('description', ''),
            status=task_details.get('status', 'To Do'),
            priority=task_details.get('priority', 'Medium'),
            task_type=task_details.get('task_type', 'Task'),
            parent_id=task_details.get('parent_id')
            # id, created_at, updated_at use defaults
        )
        
        self._tasks.append(new_task)
        save_tasks_to_json(self._tasks, self._file_path) # Save changes
        # print(f"Added task {new_task.id}. Total tasks: {len(self._tasks)}") # Optional debug
        return new_task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieves a single task by its unique ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object if found, otherwise None.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: str, updates: dict) -> bool:
        """Updates an existing task with new details.

        Only updates fields provided in the updates dictionary.
        Ignores attempts to update 'id' or 'created_at'.
        Updates the 'updated_at' timestamp on successful update.

        Args:
            task_id: The ID of the task to update.
            updates: A dictionary containing the fields and new values to update.

        Returns:
            True if the update was successful, False if the task was not found.
        """
        task_to_update = self.get_task(task_id)
        if task_to_update is None:
            return False

        updated = False
        allowed_fields = [f.name for f in fields(Task) if f.name not in ['id', 'created_at']] 
        # Alternative: explicitly list allowed fields: ['title', 'description', 'status', ...]
        
        for key, value in updates.items():
            if key in allowed_fields and hasattr(task_to_update, key):
                current_value = getattr(task_to_update, key)
                if current_value != value:
                    setattr(task_to_update, key, value)
                    updated = True
            # Silently ignore disallowed fields like 'id', 'created_at' or unknown fields

        if updated:
            task_to_update.updated_at = datetime.now() # Update timestamp
            save_tasks_to_json(self._tasks, self._file_path) # Save changes
            # print(f"Updated task {task_id}.") # Optional debug
        
        return True # Return True even if no fields were changed, as task was found

    def delete_task(self, task_id: str) -> bool:
        """Deletes a task by its unique ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the deletion was successful, False if the task was not found.
        """
        original_length = len(self._tasks)
        # Rebuild the list excluding the task with the matching ID
        self._tasks = [task for task in self._tasks if task.id != task_id]
        
        if len(self._tasks) < original_length:
            # Task was found and removed
            save_tasks_to_json(self._tasks, self._file_path) # Save changes
            # print(f"Deleted task {task_id}. Remaining tasks: {len(self._tasks)}") # Optional debug
            return True
        else:
            # Task was not found
            return False

# --- JSON Persistence Functions ---

def _datetime_encoder(obj):
    """JSON encoder for datetime objects."""
    """Custom JSON encoder to serialize datetime objects into ISO 8601 format.
    
    Raises:
        TypeError: If the object is not a datetime object.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()

def _datetime_decoder(dct):
    """JSON decoder hook for datetime objects."""
    """Custom JSON object hook to deserialize ISO 8601 strings back into 
    datetime objects for specific keys ('created_at', 'updated_at').
    """
    for key, value in dct.items():
        # Basic ISO format check (adjust if using different formats)
        if isinstance(value, str) and len(value) > 10 and value[10] == 'T': 
            try:
                # Attempt to parse common datetime fields
                if key in ['created_at', 'updated_at']:
                     dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass # Ignore if parsing fails, leave as string
    return dct

def save_tasks_to_json(tasks: list[Task], file_path: str):
    """Saves a list of Task objects to a JSON file.
    
    Args:
        tasks: The list of Task objects to save.
        file_path: The path to the JSON file.
    """
    try:
        # Convert list of Task objects to list of dictionaries
        tasks_as_dict = [asdict(task) for task in tasks]
        with open(file_path, 'w') as f:
            json.dump(tasks_as_dict, f, indent=4, default=_datetime_encoder)
    except IOError as e:
        logger.error(f"Error saving tasks to {file_path}: {e}")
    except TypeError as e:
        logger.error(f"Error serializing task data: {e}")

def load_tasks_from_json(file_path: str) -> list[Task]:
    """Loads a list of Task objects from a JSON file.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A list of Task objects, or an empty list if the file 
        doesn't exist or contains invalid data.
    """
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r') as f:
            tasks_data = json.load(f, object_hook=_datetime_decoder)
            # Convert dictionaries back to Task objects
            # Filter out any potential None values from malformed data
            tasks_list = [Task(**data) for data in tasks_data if data is not None]
            return tasks_list
    except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
        logger.error(f"Error loading tasks from {file_path}: {e}")
        # Optionally: backup corrupted file here
        return []
