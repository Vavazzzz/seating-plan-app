# Seating Plan Application

A modern, full-featured PyQt6 desktop application for creating and managing seating plans with a clean layered architecture built on Domain-Driven Design principles.

## Overview

The Seating Plan Application is a professional-grade GUI tool designed to help event organizers create and manage seating arrangements. It provides a comprehensive solution for seating plan creation, management, persistence, and reporting—combining an intuitive user interface with a robust backend built on clean architecture principles.

**Architecture**: The application follows a layered architecture pattern with clear separation of concerns:
- **Domain Layer**: Business logic and entities (completely independent)
- **Application Layer**: Use cases and services with command pattern
- **Infrastructure Layer**: Persistence and import/export implementations
- **Presentation Layer**: PyQt6-based UI with dialogs and widgets

## Core Features

### Seating Management
- Create and manage seating plans with multiple sections
- Add, delete, clone, and merge sections
- Add seats individually or in ranges (numeric and alphanumeric support)
- Change row and seat numbering/labeling
- Move selected seats between sections
- Support for general-admission sections

### Advanced Operations
- **Clone sections**: Single or batch cloning with automatic naming
- **Merge sections**: Combine sections with data consolidation
- **Batch operations**: Select rows, sections, or all seats for bulk modifications
- **Range operations**: Add seat/row ranges with optional prefixes/suffixes and parity filters

### File Operations
- **Save/Load**: JSON-based project persistence (`.seatproj`)
- **Import formats**: JSON, Excel (`.xlsx`), Avail XML
- **Export formats**: JSON, Excel
- **Undo/Redo**: Complete command history with memory-efficient snapshots

### User Interface
- Central graphics view with zoom, pan, and multi-select capabilities
- Right-click context menu for seat operations
- Sections panel with drag-and-drop reordering
- Status bar with real-time operation feedback
- Tabbed interface for section management
- Keyboard shortcuts for common operations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or poetry package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd seating-plan-app
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv .venv-gui
   ```

3. **Activate virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv-gui\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     .venv-gui\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv-gui/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements/gui.txt
   ```
   
   Or with Poetry:
   ```bash
   poetry install
   ```

### Development Setup

For development with testing and code formatting tools:
```bash
pip install -r requirements/base.txt -r requirements/gui.txt
pip install pytest black  # Optional development tools
```

## Usage

### Running the Application

From the repository root:
```bash
python run.py
```

Or using Python module syntax:
```bash
python -m src.ui.main_window
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Delete** | Delete selected seats |
| **Shift+Delete** | Delete entire rows of selected seats |
| **Ctrl+A** | Select all seats in current section |
| **Ctrl+N** | Add new section / Create new project |
| **Ctrl+Z** | Undo last operation |
| **Ctrl+Y** | Redo last undone operation |
| **F5** | Refresh current view |

### User Interface Features

- **Zoom Control**: Floating zoom slider in bottom right of section view
- **Drag & Drop**: Reorder sections via the sections panel
- **Context Menu**: Right-click on seats for operation menu
- **Status Bar**: Real-time feedback on operations and selection status
- **Tabbed Interface**: View and manage sections with tab navigation

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# UI tests only
python -m pytest tests/ui/ -v

# Domain model tests
python -m pytest tests/unit/domain/ -v

# Infrastructure tests
python -m pytest tests/unit/infrastructure/ -v
```

### Test Structure

- **`tests/unit/domain/`**: Domain model unit tests
- **`tests/unit/infrastructure/`**: Persistence and import/export tests
- **`tests/ui/`**: UI integration tests

### Phase Validation Tests

The repository includes phase tests from the refactoring process for validation:
- `test_phase3.py` - Commands and handlers
- `test_phase4.py` - Application services layer
- `test_phase5.py` - UI refactoring validation
- `test_phase6.py` - End-to-end integration

Run any phase test directly:
```bash
python test_phase6.py
```

## Project Structure

```
seating-plan-app/
├── src/                              # Application source code
│   ├── domain/                       # Domain layer (business logic)
│   │   ├── models/
│   │   │   ├── seating_plan.py      # SeatingPlan entity
│   │   │   ├── section.py           # Section entity  
│   │   │   └── seat.py              # Seat entity
│   │   ├── services/                # Domain services
│   │   └── exceptions.py            # Domain exceptions
│   │
│   ├── application/                 # Application layer (use cases & services)
│   │   ├── services/                # Application services
│   │   │   ├── base.py              # BaseService with validation framework
│   │   │   ├── seating_plan_service.py
│   │   │   ├── section_service.py
│   │   │   └── seat_service.py
│   │   ├── commands/                # Command pattern (11 commands)
│   │   │   ├── add_section.py
│   │   │   ├── delete_section.py
│   │   │   ├── rename_section.py
│   │   │   ├── clone_section.py
│   │   │   ├── merge_sections.py
│   │   │   └── seat_commands.py
│   │   ├── handlers/                # Command handler
│   │   │   └── command_handler.py
│   │   ├── result.py                # Result[T, E] type for error handling
│   │   └── dto.py                   # Data transfer objects
│   │
│   ├── infrastructure/              # Infrastructure layer (persistence, I/O)
│   │   ├── persistence/             # Data persistence
│   │   │   ├── abstract.py
│   │   │   └── json_repository.py   # JSON-based repository
│   │   ├── import_export/           # File I/O implementations
│   │   │   ├── json_importer.py
│   │   │   ├── json_exporter.py
│   │   │   ├── excel_importer.py
│   │   │   ├── excel_exporter.py
│   │   │   └── avail_importer.py    # Avail XML support
│   │   └── utils/                   # Infrastructure utilities
│   │       ├── alphanum_handler.py
│   │       └── validators.py
│   │
│   ├── ui/                          # Presentation layer (PyQt6 UI)
│   │   ├── main_window.py           # Main application window (legacy)
│   │   ├── main_window_refactored.py # Refactored main window (~200 lines)
│   │   ├── section_view.py          # Section detail view
│   │   ├── dialogs/                 # Dialog implementations
│   │   │   ├── base.py              # Base dialog classes
│   │   │   ├── section_dialogs.py   # Section operation dialogs
│   │   │   ├── seat_dialogs.py      # Seat operation dialogs
│   │   │   └── dialogs.py           # Legacy dialogs (RangeInputDialog, etc.)
│   │   └── widgets/                 # Reusable UI components
│   │       ├── base.py              # BasePanel with error handling
│   │       ├── sections_panel.py    # Sections management panel
│   │       └── (other widgets)
│   │
│   ├── utils/                       # General utilities
│   │   ├── file_handlers.py
│   │   └── alphanum_handler.py
│   │
│   └── config.py                    # Application configuration
│
├── tests/                           # Test suite
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_seating_plan.py
│   │   │   └── test_section.py
│   │   └── infrastructure/
│   │       └── (infrastructure tests)
│   └── ui/
│       └── test_ui_features.py
│
├── docs/                            # Documentation
│   ├── DEVELOPER_GUIDE.md          # Development guidelines
│   ├── USER_GUIDE.md               # End-user documentation
│   ├── RELEASE.md                  # Release procedures
│   └── MIGRATION_GUIDE.md          # Architecture migration guide
│
├── requirements/                    # Dependency specifications
│   ├── base.txt                    # Base dependencies
│   ├── gui.txt                     # GUI dependencies
│   └── api.txt                     # API dependencies
│
├── run.py                          # Application entry point
├── pyproject.toml                  # Poetry configuration
├── CHANGELOG.md                    # Version history
├── SeatingPlan.spec                # PyInstaller spec for compilation
└── README.md                       # This file
```

### Architecture Layers

**Domain Layer** (`src/domain/`)
- Core business entities: `SeatingPlan`, `Section`, `Seat`
- Domain-specific exceptions and validation
- Completely independent of UI, frameworks, and external libraries

**Application Layer** (`src/application/`)
- Services pattern for business use cases
- Command pattern for undo/redo support (11 command implementations)
- Result type for explicit error handling
- No direct dependencies on UI or persistence

**Infrastructure Layer** (`src/infrastructure/`)
- Repository pattern for data persistence
- Import/export adapters for multiple file formats
- Dependency injection points for concrete implementations
- Isolated I/O and external service integrations

**Presentation Layer** (`src/ui/`)
- PyQt6-based user interface
- Dialog components for user interactions
- View models and adapters for display logic
- Signal/slot architecture for reactive updates

## Architecture & Design Patterns

### Design Principles
- **Domain-Driven Design (DDD)**: Organization around core business concepts
- **Clean Architecture**: Clear separation of concerns across layers
- **SOLID Principles**: Single responsibility, open/closed, etc.
- **Command Pattern**: For undo/redo support with explicit history management

### Key Patterns
- **Command Pattern**: 11 command implementations for all seating operations
- **Service Pattern**: Application services as use case coordinators
- **Repository Pattern**: Abstract persistence layer
- **Result Type**: Explicit error handling (Result[T, E]) instead of exceptions
- **Factory Pattern**: Used in import/export adapters

### Error Handling
The application uses a `Result[T, E]` type for explicit error handling:
```python
result = service.perform_operation()
if result.is_success():
    value = result.get_value()
else:
    error = result.get_error()
```

This approach ensures:
- No silent failures
- Clear error propagation
- Type-safe operation outcomes
- Testable error scenarios

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. **Fork and branch**: Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Maintain architecture**: Keep changes within appropriate layers
   - Domain changes: Core business logic only
   - Application changes: Services and commands
   - UI changes: Dialogs and widgets only

3. **Add tests**: Create corresponding tests for any new functionality
   ```bash
   # Add unit tests in tests/unit/
   # Add integration tests as needed
   ```

4. **Run validation**: Before submitting, validate your changes
   ```bash
   python -m pytest tests/ -v           # Run all tests
   python test_phase6.py                # Run integration validation
   ```

5. **Code quality**: Follow PEP 8 guidelines
   ```bash
   black src/                           # Format code
   ```

6. **Document changes**: Update docstrings and comments
   - Add docstrings to new functions and classes
   - Update README if behavior changes
   - Update CHANGELOG.md with your changes

### Submission

- Submit a pull request with clear description of changes
- Reference any related issues
- Ensure all tests pass before requesting review
- Be open to feedback and iteration

### Release Process

Maintainers can release new versions by:
1. Updating version in `pyproject.toml`
2. Adding entry to `CHANGELOG.md`
3. Creating Git tag (e.g., `v1.2.0`)
4. GitHub Actions handles automated release build

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)**: End-user documentation and tutorials
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Development setup and conventions
- **[Migration Guide](docs/MIGRATION_GUIDE.md)**: Architecture refactoring details
- **[Release Process](docs/RELEASE.md)**: Release and deployment procedures

See `docs/RELEASE.md` for a sample release workflow.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

### Release Notes (latest)
- **v1.1.8**
  - Added drag & drop ordering of sections
  - Developed right-click context menu with seat utilities
  - Added serialization support for sections (`to_dict`)
  - Improved undo/redo and enhanced UI controls
  - Expanded test coverage: new unit tests for model and UI behaviors
  - Updated documentation and user guide