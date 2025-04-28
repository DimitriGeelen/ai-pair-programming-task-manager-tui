# AI Pair Programming Workflow Management App - Work Package

## Status Key:
- [ ] To Do
- [x] Done
- [-] In Progress
- [!] Blocked

## Initial Tasks (Based on Steps_new_code):

- [x] **-100: !DefGoal:** Define project goals. (Completed in initial query)
- [x] **-200: !DefMeas:** Define measurement of success. (Completed in initial query)
- [x] **-300: !CreMoFi:** Create the main application file/module.
- [x] **-400: !CreMoDo:** Document Goals & Measurement of Success in main project documentation.
- [x] **-500: !WriCoUT:** Write the first unit test for core functionality (e.g., adding a task).
- [x] **-600: !RunUnTe:** Run the unit test (expecting failure).
- [x] **-700: !LoopUnT:** Refine unit test and document negative test outcome.
- [x] **-800: !ReaArGu:** Review Architecture_rules.
- [x] **-900: !ResPSol:** Research potential technical solutions.
- [x] **-1000: !PrSolOp:** Present solution options to the user.
- [x] **-1100: !ReSolOp:** Iterate on solution options and document chosen design.
- [x] **-1200: !CrTasSo:** Create detailed implementation sub-tasks.
- [-] **-1300: !CodeSol:** Begin iterative implementation of sub-tasks.

## Implementation Tasks (Created during -1200):

- [x] **-2000:** Define the `Task` dataclass in `AI_Pair_Programming_Task_Manager.py`.
- [x] **-2100:** Implement basic JSON loading/saving functions.
- [x] **-2200:** Implement the core `TaskManager` class.
    - [x] **-2201:** Implement `__init__` to load tasks from JSON.
    - [x] **-2202:** Implement `add_task` method.
    - [x] **-2203:** Implement `get_task(task_id)` method.
    - [x] **-2204:** Implement `update_task(task_id, updates)` method.
    - [x] **-2205:** Implement `delete_task(task_id)` method.
    - [x] **-2206:** Implement `get_all_tasks()` property.
- [x] **-2300:** Refactor `test_task_manager.py`.
    - [x] **-2301:** Import actual `TaskManager` and `Task`.
    - [x] **-2302:** Remove placeholder `TaskManager`.
    - [x] **-2303:** Adapt and pass `test_add_task`.
    - [x] **-2304:** Write unit tests for `get_task`.
    - [x] **-2305:** Write unit tests for `update_task`.
    - [x] **-2306:** Write unit tests for `delete_task`.
    - [x] **-2307:** Write unit tests for JSON loading/saving.
- [x] **-2400:** Set up the basic `textual` application structure.
    - [x] **-2401:** Create `tui_app.py`.
    - [x] **-2402:** Add `textual` to `requirements.txt`.
    - [x] **-2403:** Implement basic `textual App` class.
- [x] **-2450:** Resolve environment/dependency installation issue for 'textual' (High Priority)
- [-] **-2500:** Implement the main Task List view (TUI).
    - [x] **-2501:** Use `DataTable` or `ListView`.
    - [x] **-2502:** Implement initial loading.
    - [x] **-2503:** Implement view refreshing. # Now includes hierarchical display
- [x] **-2600:** Implement Task Adding (TUI).
    - [x] **-2601:** Create add task modal/screen.
    - [x] **-2602:** Handle submission and call `TaskManager.add_task`.
    - [x] **-2603:** Update main list view.
- [x] **-2700:** Implement Task Viewing/Editing (TUI).
    - [x] **-2701:** Allow task selection.
    - [x] **-2702:** Display task details.
    - [x] **-2703:** Implement editing functionality. # Basic Edit screen + integration done
- [x] **-2800:** Implement Task Deleting (TUI).
    - [x] **-2801:** Trigger deletion.
    - [x] **-2802:** Add confirmation.
    - [x] **-2803:** Call `TaskManager.delete_task`.
- [x] **-2900:** Implement Status Update/Progress Tracking (TUI).
    - [x] **-2901:** Allow status changes.
    - [x] **-2902:** Visually indicate status.
- [x] **-3000:** Implement User Interaction (Pause/Priority Change) (TUI).
    - [x] **-3001:** Define pause mechanism.
    - [x] **-3002:** Allow priority changes.
- [x] **-3100:** Implement Agile Taxonomy handling (Filtering/Grouping) (TUI).
    - [x] **-3101:** Filter by type.
    - [ ] **-3102:** Visual grouping. *(Note: Deferred due to complexity with DataTable. Consider Tree widget or refactor)*

## Refactoring Tasks:

- [x] **-4000:** Refactor `tui_app.py` to reduce complexity/size (e.g., separate screens/widgets into modules). # Screens and helpers moved

## New Tasks (Optional - Add as needed):
# - [ ] **-5000:** Enhance AddTaskScreen (Status, Priority, Type, Parent)
# - [ ] **-5100:** Implement Parent/Child linking logic/validation in TaskManager
# - [ ] **-5200:** Improve DataTable filtering to preserve hierarchy
# - [ ] **-5300:** Add Parent/Child info to details view
