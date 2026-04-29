# Seating Plan Application - User Guide

This document is intended for end users of the Seating Plan Application. It describes how to install, run, and use the application's features.

## Installation

### Requirements
- Python 3.8 or newer
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd seating-plan-app
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   
   **Windows (PowerShell)**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   **Windows (Command Prompt)**:
   ```cmd
   .venv\Scripts\activate
   ```
   
   **macOS/Linux**:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements/base.txt
   pip install -r requirements/gui.txt
   ```

## Starting the Application

From the project root:

```bash
python run.py
```

Or using Python module syntax:

```bash
python -m src.ui.main_window
```

## User Interface Overview

The Seating Plan Application provides an intuitive interface for managing seating arrangements:

### Main Components

- **Sections Panel** (left side): Lists all sections in your seating plan with drag-and-drop reordering
- **Main Seat View** (center): Graphical representation of seats in the selected section
- **Controls Bar** (top): Quick-access buttons for common operations
- **Status Bar** (bottom): Shows real-time information about the current section and selection

### Key Features

**Multiple View Modes**
- Click any section name to view and edit that section
- Use checkboxes for bulk operations across multiple sections
- Drag rows to reorder sections (order is preserved in saves)

**Graphical Seat Layout**
- Seats displayed in a grid organized by rows
- Clear visual hierarchy showing section structure
- Color-coded indicators for seat selection and status

**Responsive Controls**
- All operations update immediately
- Visual feedback for all user actions
- Error messages clearly indicate problems

## Editing Seats and Sections

### Adding a Section

1. Click the **Add Section** button in the menu
2. Enter a section name
3. Optionally check "General Admission" if this is a GA section
4. Click OK

### Renaming a Section

1. Right-click on the section name
2. Choose **Rename Section**
3. Enter the new name
4. Click OK

### Cloning a Section

To create copies of an existing section:

1. Right-click on the section
2. Choose **Clone Section** (creates one copy) or **Clone Multiple** (creates many)
3. For single clone: enter the new section name
4. For multiple clones: specify count (auto-generates names like "Section A_1", "Section A_2")

### Merging Sections

To combine multiple sections into one:

1. Right-click on a source section
2. Choose **Merge Sections**
3. Select which sections to merge into the target
4. Click OK

### Adding Seats

**Individual Seats**
1. Click **Add Seat** button
2. Enter row number and seat label (e.g., row "1", seat "A")
3. Click OK

**Seat Ranges**
1. Click **Add Seat Range** button
2. Specify starting and ending rows and seat numbers
3. Optionally add prefixes/suffixes to seat labels
4. Click OK

Example: Rows 1-3, Seats 1-10 with no filter creates seats 1A-1J, 2A-2J, 3A-3J

### Deleting Seats

1. Click to select seats (or use Ctrl+Click for multiple)
2. Press **Delete** to remove selected seats
3. Or press **Shift+Delete** to remove entire rows

### Moving Seats Between Sections

1. Select the seats to move
2. Right-click and choose **Move to Section**
3. Select target section (or create new)
4. Confirm

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Delete** | Delete selected seats |
| **Shift+Delete** | Delete entire rows of selected seats |
| **Ctrl+A** | Select all seats in current section |
| **Ctrl+Z** | Undo last operation |
| **Ctrl+Y** | Redo last undone operation |
| **Ctrl+N** | Create new seating plan |
| **F5** | Refresh current view |

## Working with Files

### Creating a New Plan

1. Use **File** → **New**
2. Give your plan a name
3. Start adding sections and seats

### Saving a Plan

**Save** (Ctrl+S):
- Saves to the current file (`.seatproj` format)

**Save As**:
- Save with a new filename or location

Plans are saved in JSON format (`.seatproj` extension) for easy sharing and backup.

### Opening an Existing Plan

1. Use **File** → **Open**
2. Browse to your `.seatproj` file
3. Click Open

### Importing from Other Formats

1. Use **File** → **Import**
2. Select source format:
   - **JSON**: Previously exported `.seatproj` files
   - **Excel**: `.xlsx` files with section/seat details
   - **Avail XML**: Avail manager export files
3. Select the file and confirm
4. The plan will be imported into the current project

### Exporting to Other Formats

1. Use **File** → **Export**
2. Choose target format:
   - **JSON**: Standard seatproj format
   - **Excel**: For sharing with other tools
3. Choose location and confirm

## Navigation & Selection

### Selecting Seats

**Basic Selection**
- Click on a seat to select it
- Hold **Ctrl** and click to add/remove seats from selection
- Hold **Shift** and click to select range

**Visual Feedback**
- Selected seats are highlighted in blue
- Hover over seats shows interactivity
- Status bar shows count of selected seats

### Reordering Sections

1. In the Sections panel, click and hold a section row
2. Drag to the desired position
3. Release to drop
4. Order is saved with your project

### Viewing Section Details

- Click a section name to view its seats
- Checkbox column allows bulk operations
- Drag handles on row left border for drag-and-drop

## Troubleshooting

### Seats Not Showing
- **Check**: Is the section selected? Click on section name in panel
- **Check**: Do seats exist? Add using Add Seat button
- **Action**: If file corrupted, try importing from backup

### Can't Add Seats to General Admission Section
- General Admission sections don't display individual seats
- Convert to regular section (uncheck GA option)
- Then add seats normally

### Undo Not Working
- Undo/Redo tracks up to 100 recent operations
- Very old operations are automatically cleared
- File → New clears undo history

### File Won't Open
- **Check**: File is valid `.seatproj` (JSON format)
- **Check**: File wasn't corrupted
- **Action**: If corrupted, reimport from Excel/Avail backup

## Tips & Tricks

1. **Quick Planning**: Use Clone Section to quickly create multiple identical sections
2. **Bulk Rename**: Export to Excel, modify in spreadsheet, re-import
3. **Backup**: Export regularly to Excel as backup format
4. **Large Plans**: Define section templates, clone them, then customize
5. **Sharing**: JSON files are text-based, easy to version control with Git

## Support & Resources

- **Documentation**: See `README.md` for feature overview
- **Architecture**: See `docs/DEVELOPER_GUIDE.md` for technical details
- **Release Notes**: Check `CHANGELOG.md` for version history
- **Issues**: Report bugs or request features via GitHub issues

## Next Steps

- Explore the graphical seat layout interface
- Try different seat and section configurations
- Export your plan to different formats
- Use undo/redo to experiment safely

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
