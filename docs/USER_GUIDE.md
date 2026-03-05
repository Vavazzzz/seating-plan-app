# Seating Plan Application - User Guide

This document is intended for end users of the Seating Plan Application. It describes how to install, run, and use the application's features.

## Installation
1. Ensure you have Python 3.10 or newer installed.
2. Clone or download the repository from GitHub:
   ```bash
   git clone <repository-url>
   cd seating-plan-app
   ```
3. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   . .venv/Scripts/Activate.ps1   # Windows PowerShell
   ```
4. Install dependencies:
   ```bash
   pip install -r ./requirements/base.txt
   pip install -r ./requirements/gui.txt
   ```

## Starting the Application
Run the following command from the project root:
```bash
python -m src.ui.main_window
```

## Interface Overview
- **Sections Dock** (left/right): list of all sections with a checkbox column for bulk actions. Use drag & drop to reorder.
- **Main View**: graphical seat layout of the selected section. Click and drag to select seats. Middle-click to pan; Ctrl+wheel to zoom.
- **Controls Bar** above view: buttons for adding rows, deleting seats/rows, renumbering, collapse/expand.
- **Status Bar**: shows current section, total seats, and selected seat count.

## Editing Seats and Sections
- Click a row in the sections table (not the checkbox) to load the section.
- Use the *Add* buttons to create seats by range or custom rows.
- Select seats by clicking or rubber-band drag; hold Ctrl to add to selection.

### Context Menu (Right-click) on Seats
Right-click anywhere in the view to open a menu. Options include:
- Delete selected seats or rows
- Move selected seats to another section (or create new section)
- Select all seats in the current row or section
- Deselect all
> The menu opens even if you click away from seats as long as some seats are selected.

### Reordering Sections
Drag a row in the sections table to a new position to change ordering. This order is preserved in file exports and undo/redo.

## Shortcuts
- **Del**: delete selected seats
- **Shift+Del**: delete rows containing selected seats
- **Ctrl+A**: select all seats in the current section
- **Ctrl+N**: add a new section (also starts new project)
- **F5**: refresh the view

## Import/Export
- **File ▶ Import**: load from `.seatproj` (JSON), Excel, or Avail XML.
- **File ▶ Export**: save current plan to `.seatproj` or Excel.

## Undo/Redo
Use the toolbar or keyboard (Ctrl+Z/Ctrl+Y) to undo/redo modifications. The application stores up to 50 snapshots.

## Advanced
General admission (GA) sections treat all seats as unnumbered; useful for festival grounds.

## Troubleshooting
- Missing PyQt6: ensure `requirements/gui.txt` is installed.
- If the UI doesn't open, run from command line to see errors.

## Support
Open issues in GitHub for bugs or feature requests. See the `tests/` directory for examples of programmatic usage.
