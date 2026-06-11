# Seating Plan Application

A PyQt6 desktop application for creating and managing seating plans, built on a clean layered architecture.

## Overview

The Seating Plan Application is a GUI tool for event organizers to create and manage seating arrangements. It supports multiple sections, flexible seat/row labeling, file import/export, and full undo/redo.

**Architecture**: Layered, with clear separation of concerns:
- **Domain Layer** — business entities and logic, no external dependencies
- **Application Layer** — use cases, services, and command pattern for undo/redo
- **Infrastructure Layer** — persistence and file import/export
- **Presentation Layer** — PyQt6 UI with dialogs and widgets

## Features

### Section Management
- Add, rename, delete, clone, and merge sections
- Clone a section once or multiple times with automatic sequential naming
- Merge multiple sections into a new section (conflict detection included)
- Checkbox multi-select for batch operations (delete, merge)

### Seat Management
- Add seats individually, by row range, or by custom row list
- Numeric and alphanumeric seat/row labels with optional prefix/suffix
- Even/odd seat filters and continuous numbering across rows
- Delete seats or entire rows
- Move selected seats to another section (or a new one created on the fly)
- Renumber rows with a custom start value

### File Operations
- **Save/Load**: JSON-based project persistence
- **Import**: JSON, Excel (`.xlsx`), Avail XML
- **Export**: JSON, Excel
- Full **undo/redo** for all mutating operations

### User Interface
- Section view with zoom (slider + Ctrl+scroll), pan (middle-mouse drag), and rubber-band multi-select
- Right-click context menu for seat operations
- Sections panel with checkbox multi-select
- Status bar feedback on every operation
- Keyboard shortcuts for common actions

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd seating-plan-app
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv-gui

   # Windows (PowerShell)
   .\.venv-gui\Scripts\Activate.ps1

   # Windows (Command Prompt)
   .venv-gui\Scripts\activate

   # macOS / Linux
   source .venv-gui/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements/gui.txt
   ```

## Running the Application

```bash
python run.py
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | Create new plan |
| `Ctrl+O` | Open plan |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+E` | Export |
| `Ctrl+I` | Import |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+A` | Select all seats in current section |
| `Escape` | Deselect all seats |
| `Del` | Delete selected seats |
| `Shift+Del` | Delete rows of selected seats |
| `Ctrl+0` | Reset zoom to 100% |
| `Ctrl+Q` | Quit |

## Testing

```bash
# All tests
python -m pytest tests/ -v

# Domain model tests only
python -m pytest tests/unit/domain/ -v

# UI tests only
python -m pytest tests/ui/ -v
```

Tests use `src/` as the Python path root (configured in `pyproject.toml`). Import as:
```python
from domain.models.seating_plan import SeatingPlan  # correct
# not: from src.domain.models.seating_plan import SeatingPlan
```

## Project Structure

```
seating-plan-app/
├── run.py                           # Application entry point
├── pyproject.toml                   # Project config and pytest settings
├── CHANGELOG.md
├── README.md
│
├── src/
│   ├── domain/                      # Business logic — no external deps
│   │   ├── models/
│   │   │   ├── seating_plan.py      # SeatingPlan aggregate
│   │   │   ├── section.py           # Section entity
│   │   │   └── seat.py              # Seat value object
│   │   ├── utils/
│   │   │   └── alphanum_handler.py  # Alphanumeric sort and range utilities
│   │   └── exceptions.py            # Domain exceptions
│   │
│   ├── application/                 # Use cases and services
│   │   ├── commands/
│   │   │   ├── base.py              # Abstract Command
│   │   │   ├── seat_commands.py     # Seat-level commands (add, delete, move, …)
│   │   │   └── section_commands.py  # Section-level commands (add, clone, merge, …)
│   │   ├── handlers/
│   │   │   └── command_handler.py   # Undo/redo stack
│   │   ├── services/
│   │   │   ├── base.py              # BaseService with validation helpers
│   │   │   ├── seating_plan_service.py
│   │   │   ├── section_service.py
│   │   │   └── seat_service.py
│   │   ├── result.py                # Result[T, E] — explicit error handling
│   │   └── use_cases.py             # Import/export/save/load use cases
│   │
│   ├── infrastructure/              # Persistence and file I/O
│   │   ├── import_export/
│   │   │   ├── abstract.py          # Importer / Exporter base classes
│   │   │   ├── json_importer.py
│   │   │   ├── json_exporter.py
│   │   │   ├── excel_importer.py
│   │   │   ├── excel_exporter.py
│   │   │   └── avail_importer.py
│   │   └── persistence/
│   │       ├── abstract.py          # SeatingPlanRepository interface
│   │       └── json_repository.py
│   │
│   └── ui/                          # PyQt6 presentation layer
│       ├── main_window.py            # Main window
│       ├── section_view.py           # Section graphics view
│       ├── dialogs/
│       │   ├── base.py               # InputDialog, CheckboxDialog
│       │   ├── section_dialogs.py    # Section operation dialogs
│       │   └── seat_dialogs.py       # Seat, row-range, and file dialogs
│       └── widgets/
│           ├── base.py               # BasePanel
│           └── sections_panel.py     # Sections management panel
│
├── tests/
│   ├── unit/
│   │   └── domain/
│   │       ├── test_seating_plan.py
│   │       └── test_section.py
│   └── ui/
│       └── test_ui_features.py
│
└── docs/
    ├── DEVELOPER_GUIDE.md
    ├── USER_GUIDE.md
    └── RELEASE.md
```

## Architecture Notes

### Command Pattern (undo/redo)
All state mutations go through `CommandHandler.execute()`. Each command snapshots its before-state in `execute()` so `undo()` can replay it exactly — no recomputation.

### Result Type
Every public service method returns `Result[T, E]`:
```python
result = section_service.add_section("Balcony")
if result.is_success():
    print(result.value)   # section name
else:
    print(result.error)   # ValidationErrors
```

### Layer Import Rules
| Layer | May import | Must not import |
|---|---|---|
| `domain/` | other `domain/` | `application/`, `infrastructure/`, `ui/`, PyQt6 |
| `application/` | `domain/`, other `application/` | `infrastructure/` concrete classes, `ui/`, PyQt6 |
| `infrastructure/` | `domain/` | `application/`, `ui/`, PyQt6 |
| `ui/` | `application/services/`, `application/result.py`, `domain/models/` | `infrastructure/` directly |

## License

MIT License — see LICENSE file for details.

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Release Process](docs/RELEASE.md)
