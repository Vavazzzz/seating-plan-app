# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - refactor-plan branch

### Added (codebase cleanup)
- `LICENSE` file (MIT), previously referenced by README but missing
- CI now runs the test suite before building (develop and release workflows)
- Regression tests: `Section.clone()` GA flag, empty `renumber_rows()` input, `CommandHandler`-based undo/redo

### Fixed (codebase cleanup)
- `Section.clone()` dropped the General Admission flag — cloned GA sections silently became regular sections
- Undo history is now cleared on New/Open/Import; previously stale commands from the old plan could still be undone
- `test_sorting_logic_consistency` never ran (missing import) and encoded a wrong expected order
- `Section.renumber_rows()` returned `None` for empty input, which would crash `RenumberRowsCommand.undo()`
- Merge validation now requires at least two source sections, matching the domain model

### Removed (codebase cleanup)
- Dead files: `src/ui/styles/theme.qss` (never loaded), `requirements/api.txt` (no API exists), `CLEANUP_REPORT.md`, `MIGRATION_GUIDE.md` (historical one-off reports), leftover `src/utils/` byte-code remnants
- Dead code: `AddSeatCommand`, `DeleteSeatCommand`, `AddSeatRangeCommand` and the unused `SeatService` methods that wrapped them; `AddSeatDialog`, `AddSeatRangeDialog`; `aboutToModify` signal; `Result.map/flat_map`; `CommandHandler.get_history_summary`; `Command.timestamp`/`is_executed`; unused exceptions `SectionNotFoundError`, `DuplicateNameError`, `InvalidStateError`; `SectionService.section_exists`

### Changed (codebase cleanup)
- `main_window_refactored.py` / `RefactoredMainWindow` renamed to `main_window.py` / `MainWindow` (legacy counterpart no longer exists)
- `ui/dialogs/dialogs.py` dissolved: `RangeInputDialog` (row mode only) and `RenumberRowsDialog` moved to `seat_dialogs.py`
- The inline "Add Custom Rows" dialog in `SectionView` extracted to `AddCustomRowsDialog` in `seat_dialogs.py`
- Section commands snapshot via object references instead of `copy.deepcopy`
- Docs (README, USER_GUIDE, DEVELOPER_GUIDE) rewritten/corrected to match the current codebase; poetry dependencies completed; `.gitignore` `*.json` rule scoped to the repo root

### Added
- `CloneSectionManyDialog` and "Clone ×N" button — clone a section N times with auto-incremented names
- `MoveSeatsCommand` and `SeatService.move_seats()` — atomic, undoable seat move between sections
- Keyboard shortcuts on all menu actions (New, Open, Save, Save As, Export, Import, Quit, Undo, Redo)
- Section-view shortcuts: Ctrl+A (select all), Escape (deselect), Ctrl+0 (reset zoom)
- `section_added` signal on `SectionsPanel` — opens the row-range dialog immediately after a new section is created
- Success messages routed to status bar (previously triggered a system beep via `QMessageBox.information`)

### Fixed
- `QDialog.Accepted` → `QDialog.DialogCode.Accepted` (PyQt6 compatibility crash on "New Plan")
- Bug F: merge-sections validation was inverted — service required target to exist but domain model requires it to not exist
- `clone_section_many` regex never extracted trailing numbers (greedy match); clones now named correctly (e.g. "Section 2", not "Section 1 2")
- `move_selected_seats_dialog` used `self.parent()` which returned an intermediate `QWidget` after layout reparenting; replaced with `self.window()`
- `move_selected_seats_dialog` created new sections by calling the domain model directly (non-undoable); now uses `section_service.add_section()`
- `move_selected_seats_dialog` called `mainwindow.refresh_section_table()` which does not exist on the refactored window

### Changed
- `MergeSectionsDialog` redesigned: combo box of existing sections replaced with a text input for the new merged section name
- Removed unused imports across 5 files

## [1.1.8] - 2026-02-26
### Added
- Drag & drop ordering of sections in UI
- Right-click context menu on seats with utilities
- Serialization support (`Section.to_dict` and improved SeatingPlan)
- New unit tests covering drag/drop, context menu operations, and serialization
- Documentation (USER_GUIDE, DEVELOPER_GUIDE, RELEASE instructions)

### Changed
- Radio-button selection replaced with checkbox column for sections
- Updated README with detailed features and usage

### Fixed
- Serialization bug causing AttributeError


