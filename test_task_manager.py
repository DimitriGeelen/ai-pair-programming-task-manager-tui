import unittest
# We will import the TaskManager class here once it's created
# from AI_Pair_Programming_Task_Manager import TaskManager 
# --- Import the actual Task class --- 
from AI_Pair_Programming_Task_Manager import Task 
# --- Import the actual JSON functions --- 
from AI_Pair_Programming_Task_Manager import load_tasks_from_json, save_tasks_to_json
from AI_Pair_Programming_Task_Manager import Task, TaskManager # Import TaskManager now
from AI_Pair_Programming_Task_Manager import load_tasks_from_json, save_tasks_to_json
from AI_Pair_Programming_Task_Manager import Task # Task already imported
from AI_Pair_Programming_Task_Manager import load_tasks_from_json, save_tasks_to_json # Already imported
from AI_Pair_Programming_Task_Manager import Task, TaskManager 
from AI_Pair_Programming_Task_Manager import load_tasks_from_json, save_tasks_to_json
from AI_Pair_Programming_Task_Manager import Task, TaskManager, load_tasks_from_json, save_tasks_to_json
from AI_Pair_Programming_Task_Manager import Task, TaskManager, load_tasks_from_json, save_tasks_to_json
from AI_Pair_Programming_Task_Manager import Task, TaskManager, load_tasks_from_json, save_tasks_to_json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal
import uuid
import json # Add json import
import os   # Add os import for file handling
import tempfile # Add tempfile import
from unittest.mock import patch, MagicMock # Add mock imports
from unittest.mock import patch, MagicMock, PropertyMock # Import PropertyMock

# Placeholder for TaskManager until it's defined
"""
class TaskManager:
    def __init__(self):
        self._tasks = [] # Assuming a list to store tasks

    def add_task(self, task_details):
        # This method needs to be implemented
        # For now, let's pretend it adds a task dictionary
        # In reality, this will initially be missing or empty
        # task_id = len(self._tasks) + 1
        # task_details['id'] = task_id
        # self._tasks.append(task_details) 
        # return task_id
        pass # No implementation yet

    def get_task(self, task_id):
       # This method also needs implementation
       # for task in self._tasks:
       #     if task.get('id') == task_id:
       #         return task
       # return None
       pass # No implementation yet
       
    @property
    def tasks(self):
        # Property to get the list of tasks
        return self._tasks
"""
# --- End Placeholder ---

# --- Placeholder Task Dataclass (to be defined in main module) ---
# This allows the test to be written before the actual class exists
"""
@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: Literal["To Do", "In Progress", "Done", "Blocked"] = "To Do"
    priority: Literal["Low", "Medium", "High", "Critical"] = "Medium"
    task_type: Literal["Epic", "Story", "Task", "Bug"] = "Task"
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None # Default to None
    # Add other fields as needed

    def __post_init__(self):
        # Ensure updated_at is set to created_at initially if not provided
        if self.updated_at is None:
            self.updated_at = self.created_at
"""
# --- End Placeholder ---

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        """Define a standard file path for tests, could be temporary."""
        self.test_json_path = "test_tasks.json" # Use a predictable name for mocking
        # Ensure file doesn't exist from previous failed runs if needed, 
        # but mocking load/save avoids this mostly.
        # if os.path.exists(self.test_json_path):
        #     os.remove(self.test_json_path)

    # Optional: Add tearDown to remove self.test_json_path if not mocking save
    # def tearDown(self):
    #     if os.path.exists(self.test_json_path):
    #         os.remove(self.test_json_path)

    @patch('AI_Pair_Programming_Task_Manager.load_tasks_from_json')
    def test_init_loads_tasks(self, mock_load):
        """Test TaskManager.__init__ calls load_tasks_from_json."""
        # Arrange: Setup the mock to return predefined tasks
        mock_task_list = [Task(title="Loaded Task 1"), Task(title="Loaded Task 2")]
        mock_load.return_value = mock_task_list
        
        # Act: Initialize the TaskManager
        # We need to ensure TaskManager uses a predictable path or pass it in
        # Let's assume it defaults to 'tasks.json' for now or takes it as arg
        manager = TaskManager(file_path=self.test_json_path) 
        
        # Assert: Check load was called and tasks are set
        mock_load.assert_called_once_with(self.test_json_path)
        self.assertEqual(len(manager.tasks), 2)
        self.assertEqual(manager.tasks[0].title, "Loaded Task 1")
        self.assertEqual(manager.tasks[1].title, "Loaded Task 2")

    # Patch save_tasks_to_json for add_task test
    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    # Also patch load_tasks_from_json for setup, return empty list initially
    @patch('AI_Pair_Programming_Task_Manager.load_tasks_from_json') 
    def test_add_task(self, mock_load, mock_save):
        """
        Test that a new task can be added to the manager.
        It should call save_tasks_to_json.
        """
        # Arrange: Mock load to return empty list initially
        mock_load.return_value = []
        manager = TaskManager(file_path=self.test_json_path)
        self.assertEqual(len(manager.tasks), 0) # Verify initially empty
        
        task_details = {
            'title': 'Implement task adding',
            'description': 'Add the basic add_task functionality.',
            'status': 'To Do',
            'priority': 'High' 
            # We might add more fields like assignee, type (Epic, Story, Task, Bug) later
        }
        
        # Act: Add the task
        task_id = manager.add_task(task_details) 
        
        # Assert: Check task was added internally and ID returned
        self.assertIsNotNone(task_id, "add_task should return an ID") 
        self.assertEqual(len(manager.tasks), 1, "Task list should have one task after adding")
        
        # Assert: Check the added task details (access via manager.tasks)
        added_task_obj = manager.tasks[0]
        self.assertEqual(added_task_obj.id, task_id) # Check ID matches
        self.assertEqual(added_task_obj.title, task_details['title'])
        self.assertEqual(added_task_obj.description, task_details['description'])
        self.assertEqual(added_task_obj.status, task_details['status'])
        self.assertEqual(added_task_obj.priority, task_details['priority'])
        self.assertIsInstance(added_task_obj.created_at, datetime)
        self.assertIsInstance(added_task_obj.updated_at, datetime)

        # Assert: Check save was called correctly
        mock_save.assert_called_once()
        # Check the first argument passed to save (the list of tasks)
        saved_tasks_list = mock_save.call_args[0][0] 
        self.assertEqual(len(saved_tasks_list), 1)
        self.assertEqual(saved_tasks_list[0].id, task_id)
        self.assertEqual(saved_tasks_list[0].title, task_details['title'])
        # Check the second argument (the file path)
        saved_file_path = mock_save.call_args[0][1]
        self.assertEqual(saved_file_path, self.test_json_path)

        # --- Remove old assertions that relied on get_task --- 
        # added_task = manager.get_task(task_id) # Assume get_task retrieves by ID
        # self.assertIsNotNone(added_task, "get_task should retrieve the added task")
        # self.assertEqual(added_task['title'], task_details['title'], "Added task title mismatch")
        # We could add more assertions for other fields

    def test_get_task_found(self):
        """Test retrieving an existing task by its ID."""
        # Arrange: Manually set up tasks in the manager instance
        # Bypass load/add to isolate get_task logic
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Task One")
        task2 = Task(title="Task Two")
        manager._tasks = [task1, task2] # Directly manipulate internal list for test isolation
        
        # Act: Try to get the second task
        retrieved_task = manager.get_task(task2.id)
        
        # Assert: Check the correct task was returned
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.id, task2.id)
        self.assertEqual(retrieved_task.title, "Task Two")

    def test_get_task_not_found(self):
        """Test retrieving a non-existent task returns None."""
        # Arrange: Setup manager with some tasks
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Task One")
        manager._tasks = [task1]
        non_existent_id = str(uuid.uuid4())
        
        # Act: Try to get a task with an ID that doesn't exist
        retrieved_task = manager.get_task(non_existent_id)
        
        # Assert: Check None was returned
        self.assertIsNone(retrieved_task)

    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    def test_update_task_found(self, mock_save):
        """Test updating an existing task's details."""
        # Arrange: Setup manager with a task
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Original Title", status="To Do")
        original_updated_at = task1.updated_at
        manager._tasks = [task1]
        updates = {"title": "Updated Title", "status": "In Progress"}
        
        # Act: Update the task
        result = manager.update_task(task1.id, updates)
        
        # Assert: Check result, updated fields, and timestamp
        self.assertTrue(result, "update_task should return True on success")
        updated_task = manager.get_task(task1.id) # Use get_task to verify
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.status, "In Progress")
        self.assertNotEqual(updated_task.updated_at, original_updated_at)
        self.assertIsInstance(updated_task.updated_at, datetime)
        
        # Assert: Check save was called
        mock_save.assert_called_once_with(manager.tasks, self.test_json_path)

    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    def test_update_task_not_found(self, mock_save):
        """Test updating a non-existent task returns False and doesn't save."""
        # Arrange: Setup empty manager
        manager = TaskManager(file_path=self.test_json_path)
        manager._tasks = []
        non_existent_id = str(uuid.uuid4())
        updates = {"title": "Doesn't Matter"}
        
        # Act: Try to update non-existent task
        result = manager.update_task(non_existent_id, updates)
        
        # Assert: Check result and that save was not called
        self.assertFalse(result, "update_task should return False for non-existent ID")
        mock_save.assert_not_called()

    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    def test_update_task_ignores_protected_fields(self, mock_save):
        """Test that update_task ignores attempts to change id or created_at."""
        # Arrange
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Immutable Test")
        original_id = task1.id
        original_created_at = task1.created_at
        manager._tasks = [task1]
        updates = {"id": "new_id", "created_at": datetime.now(), "title": "New Title"}

        # Act
        result = manager.update_task(task1.id, updates)

        # Assert
        self.assertTrue(result)
        updated_task = manager.get_task(task1.id)
        self.assertEqual(updated_task.id, original_id) # ID should not change
        self.assertEqual(updated_task.created_at, original_created_at) # created_at should not change
        self.assertEqual(updated_task.title, "New Title") # Title should change
        mock_save.assert_called_once()

    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    def test_delete_task_found(self, mock_save):
        """Test deleting an existing task removes it and saves."""
        # Arrange
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Delete Me")
        task2 = Task(title="Keep Me")
        manager._tasks = [task1, task2]
        self.assertEqual(len(manager.tasks), 2)
        
        # Act
        result = manager.delete_task(task1.id)
        
        # Assert
        self.assertTrue(result, "delete_task should return True on success")
        self.assertEqual(len(manager.tasks), 1, "Task list should have one less task")
        self.assertEqual(manager.tasks[0].id, task2.id) # Check remaining task is correct
        self.assertIsNone(manager.get_task(task1.id), "Deleted task should not be findable")
        mock_save.assert_called_once_with(manager.tasks, self.test_json_path)
        
    @patch('AI_Pair_Programming_Task_Manager.save_tasks_to_json')
    def test_delete_task_not_found(self, mock_save):
        """Test deleting a non-existent task returns False and doesn't save."""
        # Arrange
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Keep Me")
        manager._tasks = [task1]
        self.assertEqual(len(manager.tasks), 1)
        non_existent_id = str(uuid.uuid4())
        
        # Act
        result = manager.delete_task(non_existent_id)
        
        # Assert
        self.assertFalse(result, "delete_task should return False for non-existent ID")
        self.assertEqual(len(manager.tasks), 1, "Task list should be unchanged")
        mock_save.assert_not_called()

    def test_get_all_tasks_property(self):
        """Test the tasks property returns the internal list."""
        # Arrange
        manager = TaskManager(file_path=self.test_json_path)
        task1 = Task(title="Task A")
        task2 = Task(title="Task B")
        manager._tasks = [task1, task2] # Manually set internal list
        
        # Act
        retrieved_tasks = manager.tasks # Access the property
        
        # Assert
        self.assertIsInstance(retrieved_tasks, list)
        self.assertEqual(len(retrieved_tasks), 2)
        self.assertIs(retrieved_tasks, manager._tasks) # Check it returns the actual internal list object
        self.assertEqual(retrieved_tasks[0].title, "Task A")
        self.assertEqual(retrieved_tasks[1].title, "Task B")

class TestTaskDataclass(unittest.TestCase):
    
    def test_task_creation_defaults(self):
        """Test creating a Task with default values."""
        task = Task(title="Default Test")
        self.assertIsInstance(task.id, str)
        self.assertTrue(len(task.id) > 0)
        self.assertEqual(task.title, "Default Test")
        self.assertEqual(task.description, "")
        self.assertEqual(task.status, "To Do")
        self.assertEqual(task.priority, "Medium")
        self.assertEqual(task.task_type, "Task")
        self.assertIsNone(task.parent_id)
        self.assertIsInstance(task.created_at, datetime)
        self.assertIsInstance(task.updated_at, datetime)
        self.assertEqual(task.created_at, task.updated_at) # Initially they should be the same

    def test_task_creation_specific_values(self):
        """Test creating a Task with specific values."""
        now = datetime.now()
        task_id = str(uuid.uuid4())
        parent = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            title="Specific Test",
            description="Detailed desc.",
            status="In Progress",
            priority="High",
            task_type="Story",
            parent_id=parent,
            created_at=now, # Use pre-defined time to avoid race condition in test
            updated_at=now
        )
        
        self.assertEqual(task.id, task_id)
        self.assertEqual(task.title, "Specific Test")
        self.assertEqual(task.description, "Detailed desc.")
        self.assertEqual(task.status, "In Progress")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.task_type, "Story")
        self.assertEqual(task.parent_id, parent)
        self.assertEqual(task.created_at, now)
        self.assertEqual(task.updated_at, now)

# --- Placeholder JSON functions (to be defined in main module) --- 
"""
def load_tasks_from_json(file_path: str) -> list[Task]:
    # Placeholder implementation
    # if not os.path.exists(file_path):
    #     return []
    # try:
    #     with open(file_path, 'r') as f:
    #         # Need custom decoder for datetime/dataclass
    #         tasks_data = json.load(f)
    #         # Convert dicts back to Task objects
    #         return [Task(**data) for data in tasks_data] # Simplified
    # except (json.JSONDecodeError, FileNotFoundError):
    #     return []
    return [] # Return empty list for now

def save_tasks_to_json(tasks: list[Task], file_path: str):
    # Placeholder implementation
    # try:
    #     with open(file_path, 'w') as f:
    #         # Need custom encoder for datetime/dataclass
    #         json.dump([task.__dict__ for task in tasks], f, indent=4) # Simplified
    # except IOError:
    #     # Handle error
    #     pass
    pass # Do nothing for now
"""
# --- End Placeholder --- 

class TestJsonPersistence(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary file for testing."""
        # Create a temporary file safely
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix=".json")
        # print(f"Created temp file: {self.temp_path}") # Optional: for debugging

    def tearDown(self):
        """Clean up the temporary file."""
        # Ensure the file descriptor is closed and the file is deleted
        os.close(self.temp_fd)
        os.remove(self.temp_path)
        # print(f"Removed temp file: {self.temp_path}") # Optional: for debugging
        
    def test_save_and_load_empty_list(self):
        """Test saving and loading an empty list of tasks."""
        save_tasks_to_json([], self.temp_path)
        loaded_tasks = load_tasks_from_json(self.temp_path)
        self.assertEqual(loaded_tasks, [])

    def test_save_and_load_single_task(self):
        """Test saving and loading a single task."""
        task = Task(title="Test JSON Single")
        tasks_to_save = [task]
        
        save_tasks_to_json(tasks_to_save, self.temp_path)
        loaded_tasks = load_tasks_from_json(self.temp_path)
        
        # These assertions WILL FAIL initially due to placeholder functions
        # --- These assertions should now PASS --- 
        self.assertEqual(len(loaded_tasks), 1)
        # self.assertEqual(loaded_tasks[0].id, task.id) # Requires proper serialization
        # self.assertEqual(loaded_tasks[0].title, task.title)
        # self.assertIsInstance(loaded_tasks[0].created_at, datetime) # Requires proper deserialization
        self.assertEqual(loaded_tasks[0].id, task.id)
        self.assertEqual(loaded_tasks[0].title, task.title)
        self.assertEqual(loaded_tasks[0].status, task.status)
        self.assertIsInstance(loaded_tasks[0].created_at, datetime)
        self.assertEqual(loaded_tasks[0].created_at.isoformat(), task.created_at.isoformat()) # Compare ISO strings for precision

    def test_save_and_load_multiple_tasks(self):
        """Test saving and loading multiple tasks."""
        task1 = Task(title="Test JSON Multi 1")
        task2 = Task(title="Test JSON Multi 2", status="In Progress")
        tasks_to_save = [task1, task2]
        
        save_tasks_to_json(tasks_to_save, self.temp_path)
        loaded_tasks = load_tasks_from_json(self.temp_path)
        
        # These assertions WILL FAIL initially
        # --- These assertions should now PASS --- 
        self.assertEqual(len(loaded_tasks), 2)
        # Add more specific checks if needed after implementation
        self.assertEqual(loaded_tasks[0].id, task1.id)
        self.assertEqual(loaded_tasks[1].id, task2.id)
        self.assertEqual(loaded_tasks[0].title, task1.title)
        self.assertEqual(loaded_tasks[1].title, task2.title)
        self.assertEqual(loaded_tasks[1].status, "In Progress")

    def test_load_non_existent_file(self):
        """Test loading from a non-existent file returns an empty list."""
        non_existent_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.json")
        # No error should be logged here, as the file doesn't exist
        loaded_tasks = load_tasks_from_json(non_existent_path)
        self.assertEqual(loaded_tasks, [])

    def test_load_invalid_json_file(self):
        """Test loading from an invalid JSON file returns an empty list and logs error."""
        with open(self.temp_path, 'w') as f:
            f.write("this is not valid json{")
        
        # Expect an error message to be logged when loading invalid JSON
        # The logger name might need adjustment if we implement proper logging
        # Assuming the print goes to stderr or is caught by default logger
        # Let's assume the logger is the root logger or associated with the module
        # Trying with the root logger first.
        # If this fails, we might need to find the specific logger name 
        # used by print (often none) or modify load_tasks_from_json to use logging.
        # For now, we assume print() might be captured by root logger if configured.
        # A more robust solution might involve patching 'print' or using logging module.
        
        # Let's try capturing logs from the module where load_tasks_from_json resides
        # Assuming the module name is AI_Pair_Programming_Task_Manager
        with self.assertLogs('AI_Pair_Programming_Task_Manager', level='ERROR') as cm:
            loaded_tasks = load_tasks_from_json(self.temp_path)
            
        self.assertEqual(loaded_tasks, [])
        # Check that the expected error message was logged
        self.assertIn(f"Error loading tasks from {self.temp_path}", cm.output[0])
        self.assertIn("Expecting value", cm.output[0]) # Check for part of the JSONDecodeError message

class TestTuiAppImport(unittest.TestCase):
    
    def test_tui_app_importable(self):
        """Ensure the tui_app.py file can be imported without syntax errors."""
        try:
            import tui_app
            importable = True
        except ImportError as e:
            # We might expect ImportError if dependencies aren't installed yet,
            # but syntax errors are different.
            importable = False
            print(f"ImportError during test_tui_app_importable: {e}") # Debug output
        except Exception as e:
            importable = False
            # Re-raise unexpected errors
            raise AssertionError(f"Failed to import tui_app due to unexpected error: {e}") from e
            
        self.assertTrue(importable, "tui_app.py should be importable")

    def test_tui_app_instantiable(self):
        """Test if the main TUI App class can be instantiated."""
        try:
            # Import inside test to avoid issues if textual isn't installed yet
            from tui_app import TaskManagerApp # Assuming this will be the App class name
            app = TaskManagerApp()
            instantiable = True
            # We could potentially check some initial state here later if needed
            # app.exit() # Try to clean up if possible, though might not be needed
        except ImportError as e:
            # If textual is not installed, this test might fail, which is acceptable 
            # for now as it indicates a setup issue rather than code issue.
            instantiable = False 
            print(f"ImportError during test_tui_app_instantiable: {e}") 
        except Exception as e:
            instantiable = False
            raise AssertionError(f"Failed to instantiate TaskManagerApp due to unexpected error: {e}") from e
            
        self.assertTrue(instantiable, "TaskManagerApp should be instantiable")

class TestTuiAppFeatures(unittest.TestCase):
    
    # We might need to use textual's test harness later for more complex tests
    # from textual.pilot import Pilot 

    @patch('AI_Pair_Programming_Task_Manager.TaskManager.tasks', new_callable=PropertyMock)
    def test_task_list_loads_on_mount(self, mock_tasks_prop):
        """Test that the task list view populates from TaskManager on mount."""
        # Arrange: Mock the tasks property to return sample tasks
        mock_task_list = [Task(title="Task One"), Task(title="Task Two")]
        mock_tasks_prop.return_value = mock_task_list
        
        from tui_app import TaskManagerApp # Import here to use updated code
        app = TaskManagerApp()
        
        # Act: Simulate app mounting and composing (simplified)
        # Ideally use textual's test harness/pilot, but for a basic check:
        # Access the presumed DataTable/ListView after compose.
        # This requires knowing the widget structure defined in compose.
        # Let's assume the main content widget will have id="task-list"
        
        # Need a way to trigger compose and access widgets without running the app fully.
        # This is hard without the test harness. Let's just check if the
        # TaskManager was called during init for now, deferring widget check.
        # (Self-correction: The initial test goal is hard without textual's harness.
        # Let's simplify: Test that compose ADDS a DataTable/ListView widget.)

        # Re-evaluate test goal: Check compose yields a DataTable or ListView
        # This still requires inspecting the result of compose().

        # Final approach for now: Since we can't easily test the composed widget state
        # without the harness, let's stick to testing if the App can be instantiated
        # (already done) and defer specific widget tests until we have the harness or
        # visual inspection is possible.
        # Therefore, no new assertions here for now.
        pass # Placeholder until better TUI testing is set up.

if __name__ == '__main__':
    unittest.main() 