# Developer Guide

This guide is for contributors who want to understand the internals of the Seating Plan Application and make modifications.

## Project Layout
```
src/
  ui/
    main_window.py    # QMainWindow subclass and UI wiring
    section_view.py   # QWidget containing QGraphicsView and seat logic
  models/
    seating_plan.py   # SeatingPlan model with sections dict and serialization
    section.py        # Section model managing seat map and operations
    seat.py           # Simple Seat class
  utils/
    alphanum_handler.py  # Helpers for alphanumeric ranges and conversions
    json_io.py           # Import/export dialogs

tests/                # unit tests for models and UI-like operations
requirements/         # dependency groups
README.md             # user-facing documentation
pyproject.toml        # project metadata and version

```

## Coding Standards
- Follow PEP 8 and use descriptive names.
- UI code uses PyQt6; signal/slot patterns connect in MainWindow.__init__ or 
  SectionView.
- Model classes should not import Qt; keep them pure Python for easier testing.

## New Features Workflow
1. Add model logic first (in `models/`).
2. Write unit tests under `tests/` exercising the new behavior.
3. Update UI (`src/ui`) to call model methods; keep UI logic separate.
4. Add or update documentation in `docs/` and README.
5. Run `python -m pytest -q` to ensure tests pass.

## Serialization
`SeatingPlan.to_dict()` and `from_dict()` transform the plan to/from nested dicts. 
`Section.to_dict()` serializes rows + seats; `Section.from_dict()` deserializes.
Ensure backward compatibility if structure changes.

## Undo/Redo
Undo snapshots are deep copies of `SeatingPlan` stored on a list in `MainWindow`.
Emit `aboutToModify` signal from `SectionView` before any mutating operation.

## Drag & Drop
`DragDropSectionTable` (subclass of `QTableWidget`) intercepts `mousePressEvent` and
`dropEvent` to compute new ordering. When sections are reordered, `MainWindow.on_sections_reordered`
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
