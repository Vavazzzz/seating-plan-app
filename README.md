# Seating Plan Application

## Overview
The Seating Plan Application is a GUI-based tool designed to help users create and manage seating arrangements for various events. Users can create seating plans, define sections, add seats, and export or import seating plans in JSON format.

## Features
- Create and manage seating plans and sections
- Add, delete, and rename sections
- **Drag & drop reorder** sections via the sections table
- Add and delete individual seats or ranges of seats (numeric and alpha)
- Clone sections (single or many copies)
- Change row and seat numbers, delete entire rows
- Move selected seats between sections with right-click context menu
- Select seats by row, select all seats in section, or deselect via context menu
- Export seating plans to JSON (`.seatproj`) or Excel
- Import seating plans from JSON, Excel, or Avail XML
- Undo/redo support and deep copy snapshots
- General‑admission sections and seat counts

## User Interface Highlights
- Central graphics view with zoom, pan, and multi‑select
- Right-click context menu on seats with utilities while preserving selection
- Sections panel with checkboxes for bulk operations
- Status bar shows current section, seat counts, and selected seat tally

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd seating-plan-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the application from the workspace root:
```bash
python -m src.ui.main_window
```

Keyboard shortcuts:
- **Del**: Delete selected seats
- **Shift+Del**: Delete rows of selected seats
- **Ctrl+A**: Select all seats (in section view)
- **Ctrl+N**: Add section / new project
- **F5**: Refresh view

A floating zoom slider appears in the bottom right of the section view.

## Testing
Unit tests are located under the `tests/` directory. Run them with:
```bash
python -m pytest -q
```
Tests cover models and UI-related behaviors (order, serialization, batch operations).

## Project Structure
```
seating-plan-app
├── src
│   ├── ui
│   │   ├── __init__.py     # UI module initialization
│   │   ├── main_window.py   # Main window layout and event handling
│   │   └── section_view.py  # Detailed view of a section
│   ├── models
│   │   ├── __init__.py     # Models module initialization
│   │   ├── seating_plan.py  # SeatingPlan model
│   │   ├── section.py       # Section model
│   │   └── seat.py          # Seat model
│   └── utils
│       ├── __init__.py          # Utils module initialization
|       ├── alphanum_handler.py  # Handling of alphanumeric ranges
│       └── json_io.py           # Project import/export functions
├── examples
│   └── seating_plan_example.json  # Example seating plan
├── tests
│   ├── test_seating_plan.py  # Unit tests for SeatingPlan
│   └── test_section.py       # Unit tests for Section
├── requirements.txt           # Project dependencies
├── pyproject.toml            # Project configuration
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Project documentation
```

## Contributing
Contributions are welcome! You can:

1. Fork the repository and create a new branch for your feature or fix.
2. Add or update tests under `tests/` corresponding to your changes.
3. Submit a pull request with a clear description of your changes.
4. Run `python -m pytest -q` to ensure all tests pass before requesting review.

### Release Process
A maintainer can tag a new release by updating `pyproject.toml` version and creating a
Git tag (e.g., `v1.1.8`). A `CHANGELOG.md` file can be appended with the list of changes.

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