# Developer Guide

This guide is for contributors and developers who want to understand the architecture and make modifications to the Seating Plan Application.

## Architecture Overview

The application follows a **layered architecture** pattern based on **Domain-Driven Design (DDD)** principles:

```
┌─────────────────────────────────────────────────────────┐
│ Presentation Layer (UI)                                 │
│ • PyQt6-based user interface                           │
│ • Dialogs, widgets, and main window                    │
│ └─ src/ui/                                             │
├─────────────────────────────────────────────────────────┤
│ Application Layer (Services & Commands)                │
│ • Use case coordination                                 │
│ • Command pattern for undo/redo                        │
│ • Services orchestrating operations                    │
│ └─ src/application/                                    │
│    • services/ (SeatingPlanService, SectionService)   │
│    • commands/ (11 command implementations)            │
│    • handlers/ (CommandHandler)                        │
├─────────────────────────────────────────────────────────┤
│ Domain Layer (Business Logic)                           │
│ • Core business entities (SeatingPlan, Section, Seat) │
│ • Domain rules and validations                         │
│ • Domain exceptions                                    │
│ └─ src/domain/                                         │
│    • models/ (SeatingPlan, Section, Seat)            │
│    • services/ (Business rules)                       │
│    • exceptions.py (Domain errors)                    │
├─────────────────────────────────────────────────────────┤
│ Infrastructure Layer (Persistence & I/O)              │
│ • Repository pattern for data persistence              │
│ • Import/export adapters                               │
│ • Implementation of infrastructure concerns            │
│ └─ src/infrastructure/                                 │
│    • persistence/ (JSONRepository)                    │
│    • import_export/ (Adapters for JSON/Excel/Avail)  │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
seating-plan-app/
├── src/
│   ├── domain/                          # Business logic layer
│   │   ├── models/
│   │   │   ├── seating_plan.py         # Core SeatingPlan entity
│   │   │   ├── section.py              # Section entity
│   │   │   └── seat.py                 # Seat entity
│   │   ├── services/
│   │   │   ├── seating_plan_service.py # Domain business rules
│   │   │   └── section_service.py      # Section rules
│   │   └── exceptions.py               # Domain-specific exceptions
│   │
│   ├── application/                     # Use cases & services layer
│   │   ├── services/
│   │   │   ├── base.py                 # BaseService with validation
│   │   │   ├── seating_plan_service.py # High-level operations
│   │   │   ├── section_service.py      # Section use cases
│   │   │   └── seat_service.py         # Seat use cases
│   │   ├── commands/
│   │   │   ├── base.py                 # Command base class
│   │   │   ├── add_section.py          # AddSection command
│   │   │   ├── delete_section.py       # DeleteSection command
│   │   │   ├── rename_section.py       # RenameSection command
│   │   │   ├── clone_section.py        # CloneSection command
│   │   │   ├── merge_sections.py       # MergeSections command
│   │   │   └── seat_commands.py        # All seat commands
│   │   ├── handlers/
│   │   │   └── command_handler.py      # Command execution & history
│   │   ├── result.py                   # Result[T, E] type
│   │   ├── dto.py                      # Data transfer objects
│   │   └── use_cases.py                # Import/Export use cases
│   │
│   ├── infrastructure/                  # Persistence & I/O layer
│   │   ├── persistence/
│   │   │   ├── abstract.py             # Repository interface
│   │   │   └── json_repository.py      # JSON implementation
│   │   ├── import_export/
│   │   │   ├── abstract.py             # Importer/Exporter interfaces
│   │   │   ├── json_importer.py        # JSON import adapter
│   │   │   ├── json_exporter.py        # JSON export adapter
│   │   │   ├── excel_importer.py       # Excel import adapter
│   │   │   ├── excel_exporter.py       # Excel export adapter
│   │   │   └── avail_importer.py       # Avail XML import adapter
│   │   └── utils/
│   │       └── alphanum_handler.py     # Range utilities
│   │
│   ├── ui/                              # Presentation layer (PyQt6)
│   │   ├── main_window.py              # Legacy main window
│   │   ├── main_window_refactored.py   # Modern main window (~200 lines)
│   │   ├── section_view.py             # Section detail view
│   │   ├── dialogs/
│   │   │   ├── base.py                 # Base dialog classes
│   │   │   ├── section_dialogs.py      # Section dialogs
│   │   │   ├── seat_dialogs.py         # Seat dialogs
│   │   │   └── dialogs.py              # Legacy dialogs
│   │   └── widgets/
│   │       ├── base.py                 # BasePanel with error handling
│   │       ├── sections_panel.py       # Sections management
│   │       └── (other widgets)
│   │
│   └── utils/                           # General utilities
│       └── file_handlers.py            # Legacy file I/O
│
├── tests/                               # Test suite
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_seating_plan.py
│   │   │   └── test_section.py
│   │   ├── application/                # (Empty - covered by integration)
│   │   └── infrastructure/
│   │       ├── test_import_export.py
│   │       └── test_workflows.py
│   └── ui/
│       └── test_ui_features.py
│
├── docs/                                # Documentation
│   ├── DEVELOPER_GUIDE.md              # This file
│   ├── USER_GUIDE.md                   # User documentation
│   ├── RELEASE.md                      # Release procedures
│   └── MIGRATION_GUIDE.md              # Refactoring details
│
├── requirements/                        # Dependencies
│   ├── base.txt                        # Core dependencies
│   ├── gui.txt                         # GUI dependencies
│   └── api.txt                         # Optional API dependencies
│
├── run.py                              # Application entry point
├── pyproject.toml                      # Project metadata
├── CHANGELOG.md                        # Version history
├── README.md                           # User-facing documentation
└── CLEANUP_REPORT.md                   # Recent cleanup details
```

## Design Patterns & Principles

### Core Patterns

**Domain-Driven Design (DDD)**
- Business logic isolated in domain layer
- Domain models represent real-world concepts
- Domain exceptions for business errors

**Clean Architecture**
- Strict layer separation with clear dependencies
- Only outer layers know about inner layers
- Domain layer is completely independent

**Command Pattern**
- 11 concrete commands for all operations
- Automatic undo/redo support
- Explicit history management
- All mutations go through CommandHandler

**Service Pattern**
- BaseService provides common validation framework
- Services expose use cases to higher layers
- Services coordinate across domain and infrastructure

**Repository Pattern**
- Abstract persistence layer
- Currently: JSONRepository
- Easy to add database support later

**Result Type**
- Explicit error handling: `Result[T, E]`
- No exceptions for expected errors
- Type-safe operation outcomes
- Callback support for async notifications

### Coding Standards

1. **Layer Independence**
   - Domain: Pure Python, no frameworks or external dependencies
   - Application: Can depend on Domain and Infrastructure
   - Infrastructure: Can depend on Domain only
   - UI: Can depend on all layers

2. **Naming Conventions**
   - Services: `*Service` (e.g., `SeatingPlanService`)
   - Commands: `*Command` (e.g., `AddSectionCommand`)
   - Dialogs: `*Dialog` (e.g., `AddSectionDialog`)
   - Exceptions: `*Error` or `*Exception` (e.g., `ValidationError`)

3. **Code Style**
   - Follow PEP 8
   - Use type hints for all public APIs
   - Add docstrings to classes and public methods
   - Use descriptive variable names

4. **Testing**
   - Unit tests in `tests/unit/` organized by layer
   - UI tests in `tests/ui/` for integration testing
   - Tests should be isolated and repeatable
   - Mock external dependencies

## New Features Workflow

### Adding a New Seating Operation

1. **Implement Domain Logic** (if needed)
   - Add methods to domain models if business rules change
   - Add exceptions if new error conditions exist

2. **Create a Command** (if operation should be undoable)
   ```python
   # src/application/commands/your_command.py
   from .base import Command
   
   class YourCommand(Command):
       def __init__(self, seating_plan, ...):
           self.seating_plan = seating_plan
           # Store state needed for undo
       
       def execute(self):
           # Perform the operation
           pass
       
       def undo(self):
           # Restore previous state
           pass
   ```

3. **Add to CommandHandler** (if it's a new operation)
   - Export from `src/application/commands/__init__.py`

4. **Create or Update Service Method**
   ```python
   # src/application/services/section_service.py
   def your_operation(self, ...) -> Result[ValueType, ValidationErrors]:
       # Validate inputs
       errors = self._validate(...)
       if not errors.is_empty():
           return Result.failure(errors)
       
       # Create and execute command
       command = YourCommand(self.seating_plan, ...)
       try:
           self.command_handler.execute(command)
           return Result.success(value)
       except Exception as e:
           return Result.failure(...)
   ```

5. **Update UI** (optional)
   - Add dialog in `src/ui/dialogs/` if user input needed
   - Add menu/button in main window
   - Connect service methods to UI signals

6. **Add Tests**
   - Unit test in `tests/unit/domain/` for model behavior
   - Integration test in `tests/unit/infrastructure/` for full workflow
   - UI test if adding new user interaction

7. **Document Changes**
   - Update README.md if user-facing
   - Update this guide if architecture-relevant
   - Update CHANGELOG.md with feature description

## Working with Services

### BaseService Pattern

All application services inherit from `BaseService`:

```python
from src.application.services.base import BaseService

class MyService(BaseService):
    def __init__(self, seating_plan, command_handler):
        super().__init__(seating_plan, command_handler)
        # Custom initialization
    
    def my_operation(self, arg: str) -> Result[str, ValidationErrors]:
        # Use self._validate() for input validation
        # Use self.command_handler.execute(cmd) for operations
        # Return Result with success or failure
        pass
    
    def on_error(self):
        # Override to handle validation errors
        # Called when Result.failure() generated with error callbacks enabled
        pass
```

### Result Type Usage

```python
# Successful operation
result = service.perform_operation()
if result.is_success():
    value = result.get_value()
    print(f"Success: {value}")

# Failed operation
else:
    error = result.get_error()
    print(f"Error: {error}")

# Check without branching
if not result.has_errors():
    # Handle success
    pass
```

## Error Handling

### Domain Exceptions
Domain layer uses exceptions for programming errors:
```python
from src.domain.exceptions import ValidationError, MergeConflictError

try:
    section = seating_plan.get_section(name)
except ValidationError as e:
    # Handle invalid argument
    pass
```

### Operation Failures
Services return `Result` for expected failures:
```python
result = seating_plan_service.add_section("Main", is_ga=False)
if result.is_failure():
    errors = result.get_error()
    for error_msg in errors.errors:
        logger.warning(f"Operation failed: {error_msg}")
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Run by layer
python -m pytest tests/unit/domain/ -v
python -m pytest tests/unit/infrastructure/ -v
python -m pytest tests/ui/ -v

# Run specific test file
python -m pytest tests/unit/domain/test_seating_plan.py -v
```

## Debugging Tips

1. **Trace command execution**: Enable logging in `CommandHandler`
2. **Inspect seating plan state**: Use `seating_plan.to_dict()` to view structure
3. **Test service directly**: Run service methods in Python REPL
4. **Check undo/redo**: Verify `can_undo()` and `can_redo()` states

## Resources

- [Domain-Driven Design (DDD)](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Command Pattern](https://refactoring.guru/design-patterns/command)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- See also: `docs/MIGRATION_GUIDE.md` for detailed architecture refactoring notes
rebuilds the `sections` dict and refreshes the table.

## Releases
See `docs/RELEASE.md` for tagging and change log management. Bump version in
`pyproject.toml` and append notes to `README.md` or `CHANGELOG.md`.

## Running the UI in Development
Start the application with:
```bash
python -m src.ui.main_window
```
Use debug prints or logging if necessary. The UI tolerates missing selections gracefully.

## Testing
Tests are plain pytest. Focus on model operations; UI behaviors are encoded in
`tests/test_ui_features.py` without creating real windows.

## Packaging
A future step: create a wheel or PyInstaller spec (already present as `SeatingPlan.spec`).
Use `pyinstaller` to build executables.
