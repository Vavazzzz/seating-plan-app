# Seating Plan Application - User Guide

This document is intended for end users of the Seating Plan Application. It describes how to install, run, and use the application's features.

## Installation

### Requirements
- Python 3.10 or newer
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd seating-plan-app
   ```

2. **Create and activate a virtual environment** (recommended):
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

## Starting the Application

From the project root:

```bash
python run.py
```

## User Interface Overview

- **Sections Panel** (left): table of all sections with a checkbox column for multi-select, the section name, and its seat count. Buttons below the table cover Add, Rename, Clone, Clone Multiple, Delete, and Merge. Drag the splitter between the panels to resize.
- **Section View** (right): graphical seat grid for the selected section, with buttons for Add Row Range, Add Custom Rows, Delete Seats, Delete Rows, Renumber Rows, and Collapse Section.
- **Status Bar** (bottom): plan totals on the left; current section, seat count, and selection count on the right.

## Managing Sections

- **Add Section**: click *Add Section* (or press `Ctrl+B`), enter a name, and optionally mark it as General Admission. After creation the row-range dialog opens automatically so you can fill the section with seats.
- **Rename**: select a section and click *Rename* (or press `F2`).
- **Clone**: select a section and click *Clone* to copy it under a new name, or *Clone Multiple* to create N copies with auto-incremented names (e.g. "Balcony 2", "Balcony 3", …).
- **Delete**: deletes the selected section, or every checked section at once. A confirmation is shown first.
- **Merge**: check at least two sections, click *Merge*, and enter a name for the new combined section. Conflicting seats (same row and seat present in more than one source) abort the merge. Optionally delete the source sections after merging.

## Managing Seats

- **Add Row Range**: creates a range of rows (numeric `1–10` or alphabetic `A–F`), each filled with a seat range. Supports row/seat prefixes and suffixes, even/odd seat filters, continuous numbering across rows, and unnumbered rows (`#` prefix).
- **Add Custom Rows**: same as above, but you type the row labels yourself, one per line.
- **Select seats** by clicking, rubber-band dragging, or `Ctrl+Click`. Press `Ctrl+A` to select the whole section, `Escape` to deselect.
- **Delete Seats / Delete Rows**: removes the selected seats, or every row that contains a selected seat (`Del` / `Shift+Del`).
- **Renumber Rows**: select seats in the rows to renumber, click *Renumber Rows*, and choose the new starting row label.
- **Move to Section**: right-click selected seats and choose *Move to Section…* to move them into another section (or a new one created on the spot). Seats already present in the target are skipped.
- **Collapse Section**: toggles a compact view that left-aligns each row's seats.

### Zoom and Pan

- Zoom with the slider in the bottom-right overlay or `Ctrl+Mouse Wheel`; `Ctrl+0` resets to 100%.
- Pan by dragging with the middle mouse button.

## Working with Files

- **New** (`Ctrl+N`): create an empty plan with a custom name.
- **Open** (`Ctrl+O`) / **Save** (`Ctrl+S`) / **Save As** (`Ctrl+Shift+S`): plans are stored as JSON (`.json` / `.seatproj`).
- **Import** (`Ctrl+I`): load from JSON, Excel (`.xlsx`), or Avail XML (`.xml`).
- **Export** (`Ctrl+E`): write the current plan to Excel.

Unsaved changes are marked with `*` in the window title, and you are asked to save before closing, opening, or starting a new plan.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | Create new plan |
| `Ctrl+O` | Open plan |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+E` | Export |
| `Ctrl+I` | Import |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Ctrl+A` | Select all seats in current section |
| `Escape` | Deselect all seats |
| `Del` | Delete selected seats |
| `Shift+Del` | Delete rows of selected seats |
| `Ctrl+0` | Reset zoom to 100% |
| `Ctrl+B` | Add section |
| `F2` | Rename selected section |
| `Ctrl+Q` | Quit |

## Undo/Redo

All seat and section modifications are undoable (`Ctrl+Z` / `Ctrl+Y`). The history keeps up to 100 operations and is cleared when a new plan is created, opened, or imported.

## Tips

1. **Quick planning**: create one template section, then *Clone Multiple* and customize.
2. **Bulk edits**: export to Excel, modify in a spreadsheet, re-import.
3. **Sharing**: saved plans are plain JSON — easy to back up and version control.
4. **General Admission** sections have no individual numbered seats; useful for standing areas.

## Troubleshooting

- **Seats not showing**: make sure a section is selected in the panel and it actually contains seats.
- **Missing PyQt6**: ensure `requirements/gui.txt` is installed in the active environment.
- **UI doesn't open**: run `python run.py` from a terminal to see the error output.

## Support

Open issues on GitHub for bugs or feature requests. See `README.md` for a feature overview and `docs/DEVELOPER_GUIDE.md` for technical details.
