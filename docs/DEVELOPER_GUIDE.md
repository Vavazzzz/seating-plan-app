# Developer Guide

This guide is for contributors who want to understand the architecture and make modifications to the Seating Plan Application.

## Architecture Overview

The application follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│ UI Layer (PyQt6)                          src/ui/        │
│ • MainWindow, SectionView, dialogs, widgets              │
├─────────────────────────────────────────────────────────┤
│ Application Layer                         src/application/│
│ • services/  validated operations returning Result       │
│ • commands/  command pattern for undo/redo               │
│ • handlers/  CommandHandler (undo/redo stacks)           │
│ • use_cases.py  import/export/save/load orchestration    │
│ • result.py  Result[T, E] type                           │
├─────────────────────────────────────────────────────────┤
│ Domain Layer                              src/domain/     │
│ • models/  SeatingPlan, Section, Seat                     │
│ • utils/  alphanumeric range and sort helpers             │
│ • exceptions.py  SeatingPlanException hierarchy           │
├─────────────────────────────────────────────────────────┤
│ Infrastructure Layer                      src/infrastructure/│
│ • import_export/  JSON, Excel, Avail XML adapters         │
│ • persistence/  SeatingPlanRepository + JSONRepository    │
└─────────────────────────────────────────────────────────┘
```

### Layer Import Rules

| Layer | May import | Must not import |
|---|---|---|
| `domain/` | other `domain/` | `application/`, `infrastructure/`, `ui/`, PyQt6 |
| `application/` | `domain/`, other `application/` | `infrastructure/` concrete classes, `ui/`, PyQt6 |
| `infrastructure/` | `domain/` | `application/`, `ui/`, PyQt6 |
| `ui/` | `application/services/`, `application/result.py`, `domain/models/` | `infrastructure/` directly — go through services |

## Project Structure

See the file tree in `README.md`; it is kept up to date with the repository.

## Key Patterns

### Command Pattern (undo/redo)

All state mutations go through `CommandHandler.execute()`
(`src/application/handlers/command_handler.py`). Commands inherit from
`Command` (`src/application/commands/base.py`):

- `execute()` must snapshot whatever state `undo()` needs **as instance
  variables** before/while mutating.
- `undo()` replays those captured values — it never recomputes them.
- Seat-level commands live in `seat_commands.py`, section-level commands in
  `section_commands.py`.
- The UI never calls domain model methods directly for mutations; it calls a
  service, which wraps the operation in a command.

### Result Type

Every public method in `src/application/services/` returns
`Result[T, ValidationErrors]` — no exceptions, no bare values:

```python
result = section_service.add_section("Balcony", is_ga=False)
if result.is_success():
    print(result.value)      # "Balcony"
else:
    print(result.error)      # ValidationErrors (str() joins messages)
```

In UI code, always branch on `result.is_success()`; never discard a result.

### Services

`BaseService` (`src/application/services/base.py`) provides the validation
helpers. The pattern for a new service method:

```python
def my_operation(self, name: str) -> Result[None, ValidationErrors]:
    self.clear_validation_errors()
    if not name or not name.strip():
        self.validate(False, "Name cannot be empty")
    if self.has_validation_errors():
        return Result.failure(self.get_validation_errors())
    try:
        self.command_handler.execute(MyCommand(self.seating_plan, name))
        return Result.success(None)
    except Exception as e:
        errors = ValidationErrors()
        errors.add(f"Failed: {e}")
        return Result.failure(errors)
```

### Importers / Exporters

Inherit from `Importer`/`Exporter` in
`src/infrastructure/import_export/abstract.py`, declare
`SUPPORTED_EXTENSIONS`, and register the instance in the services config in
`src/ui/main_window.py`. No PyQt6 imports in infrastructure — file pickers
belong in `src/ui/dialogs/seat_dialogs.py` (`FileDialog`).

### Dialogs

Dialogs collect and return data only — no service calls, no state mutation.
Section dialogs live in `src/ui/dialogs/section_dialogs.py`, seat/row/file
dialogs in `src/ui/dialogs/seat_dialogs.py`, shared bases
(`InputDialog`, `CheckboxDialog`) in `src/ui/dialogs/base.py`.

## Coding Standards

- PEP 8; type hints on every new public method (`str | None`, `list[str]` —
  modern syntax, not `Optional`/`List`).
- No `print()` in non-test code; no bare `except:`.
- Iteration order of `SeatingPlan.sections` is meaningful (insertion order) —
  never `sorted()` it when listing sections.
- `copy.deepcopy` on `SeatingPlan`/`Section` is not allowed outside tests;
  commands snapshot by keeping references or via `Section.clone()`.

## Adding a New Undoable Operation

1. Add domain logic to the model if business rules change.
2. Create a command in `seat_commands.py` or `section_commands.py`; export it
   from `src/application/commands/__init__.py`.
3. Add a validated service method returning `Result`.
4. Wire the UI: dialog (if input is needed) + signal/slot in the panel or
   view, always branching on the result.
5. Add or update tests in `tests/unit/domain/` (model behavior) and, where
   useful, command-level tests.

## Running Tests

```bash
python -m pytest tests/ -v

# By area
python -m pytest tests/unit/domain/ -v
python -m pytest tests/ui/ -v
```

Tests import with `src/` as the path root (configured via
`pythonpath = ["src"]` in `pyproject.toml`):

```python
from domain.models.seating_plan import SeatingPlan   # correct
# not: from src.domain.models.seating_plan import SeatingPlan
```

No PyQt6 in tests — `tests/ui/` exercises the model-level behavior behind UI
features without creating windows.

## Running the App in Development

```bash
python run.py
```

## Releases & Packaging

See `docs/RELEASE.md`. Tagged releases (`v*`) and pushes to `develop` are
built by the GitHub Actions workflows in `.github/workflows/` using
PyInstaller (`SeatingPlan.spec`).
