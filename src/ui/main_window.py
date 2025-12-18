import sys
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QInputDialog, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QStatusBar, QLabel, QCheckBox,
    QDialog, QLineEdit, QDialogButtonBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from ..models.seating_plan import SeatingPlan
from ..utils.json_io import import_project_dialog, import_from_excel_dialog, import_from_avail_dialog, export_project_dialog, export_to_excel_dialog
from .section_view import SectionView

class MainWindow(QMainWindow):
    """The application's main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seating Plan Editor")
        self.resize(1100, 750)

        self.seating_plan = SeatingPlan(name="Untitled")
        self.current_project = None

        # Undo/redo stacks (store deep copies of SeatingPlan)
        self.undo_stack = []
        self.redo_stack = []

        # --- Central Section View ---
        self.section_view = SectionView(self)
        self.setCentralWidget(self.section_view)
        self.section_view.selectionChanged.connect(self.update_selected_count)
        self.section_view.sectionModified.connect(self.refresh_section_table)
        self.section_view.aboutToModify.connect(self.push_undo_snapshot)

        # --- Dock: Sections table ---
        self.section_table = QTableWidget(0, 2)
        self.section_table.setHorizontalHeaderLabels(["Section", "Seats"])
        self.section_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.section_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.section_table.verticalHeader().setVisible(False)
        self.section_table.setSelectionBehavior(self.section_table.SelectionBehavior.SelectRows)
        self.section_table.setEditTriggers(self.section_table.EditTrigger.NoEditTriggers)

        # Add section button
        dock_widget_container = QWidget()
        dock_layout = QVBoxLayout()
        self.add_section_btn = QPushButton("\u2795 Add Section")
        self.add_section_btn.setToolTip("Add a new section (Ctrl+N creates a new project; add section here)")
        dock_layout.addWidget(self.add_section_btn)
        dock_layout.addWidget(self.section_table)
        dock_widget_container.setLayout(dock_layout)

        self.section_dock = QDockWidget("Sections", self)
        self.section_dock.setWidget(dock_widget_container)
        self.section_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.section_dock)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        self.setStatusBar(self.status_bar)

        # --- Menus & Actions ---
        self._build_actions()
        self._connect_signals()

    # ---------- Menu and Signals ----------
    def _build_actions(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # New project (also Ctrl+N)
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setToolTip("Create a new project (Ctrl+N)")
        new_action.triggered.connect(self.new_project_dialog)
        file_menu.addAction(new_action)

        # Save project (Ctrl+S)
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Save current project (Ctrl+S)")
        save_action.triggered.connect(self.save_project_dialog)
        file_menu.addAction(save_action)

        # Import seating plan (Ctrl+O)
        import_action = QAction("Import seating plan...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.setToolTip("Import seating plan (Ctrl+O)")
        import_action.triggered.connect(self.import_project)
        file_menu.addAction(import_action)

        # Import seating plan from Excel
        import_excel_action = QAction("Import from Excel...", self)
        import_excel_action.setToolTip("Import seating plan from Excel")
        import_excel_action.triggered.connect(self.import_from_excel)
        file_menu.addAction(import_excel_action)

        # Import seating plan from Avail file
        import_avail_action = QAction("Import from avail (XML)...", self)
        import_avail_action.setToolTip("Import seating plan from Avail file")
        import_avail_action.triggered.connect(self.import_from_avail)
        file_menu.addAction(import_avail_action)

        # Export seating plan to Excel
        export_excel_action = QAction("Export Excel...", self)
        export_excel_action.setToolTip("Export seating plan to Excel")
        export_excel_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_excel_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        add_section_action = QAction("Add Section", self)
        add_section_action.setToolTip("Add a new section")
        add_section_action.setShortcut("Ctrl+B")
        add_section_action.triggered.connect(self.add_section_dialog)
        edit_menu.addAction(add_section_action)

        clone_section_action = QAction("Clone Section", self)
        clone_section_action.setToolTip("Clone selected section")
        clone_section_action.triggered.connect(self.clone_section_dialog)
        edit_menu.addAction(clone_section_action)

        # New: clone multiple
        clone_many_action = QAction("Clone Section Multiple...", self)
        clone_many_action.setToolTip("Clone selected section multiple times")
        clone_many_action.triggered.connect(self.clone_section_many_dialog)
        edit_menu.addAction(clone_many_action)

        delete_section_action = QAction("Delete Section", self)
        delete_section_action.setToolTip("Delete selected section")
        delete_section_action.triggered.connect(self.delete_section)
        edit_menu.addAction(delete_section_action)

        rename_section_action = QAction("Rename Section", self)
        rename_section_action.setToolTip("Rename selected section")
        rename_section_action.triggered.connect(self.rename_section_dialog)
        edit_menu.addAction(rename_section_action)

        # Undo / Redo actions
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setToolTip("Undo last change (Ctrl+Z)")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setToolTip("Redo last undone change (Ctrl+Shift+Z)")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        self.toggle_sections_action = QAction("Sections Panel", self, checkable=True)
        self.toggle_sections_action.setChecked(True)
        self.toggle_sections_action.triggered.connect(self.toggle_sections_panel)
        view_menu.addAction(self.toggle_sections_action)

        # Refresh
        refresh_action = QAction("Refresh View", self)
        refresh_action.setShortcut("F5")
        refresh_action.setToolTip("Refresh the view (F5)")
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)

    def _connect_signals(self):
        self.add_section_btn.clicked.connect(self.add_section_dialog)
        self.section_table.cellClicked.connect(self.on_section_selected)
        self.section_dock.visibilityChanged.connect(lambda visible: self.toggle_sections_action.setChecked(visible))

    # ---------- Undo/Redo handling ----------
    def push_undo_snapshot(self, description: str | None = None):
        """Push a deep copy snapshot of the current SeatingPlan to the undo stack.
           Clear redo stack because a new action branch is created."""
        try:
            snapshot = copy.deepcopy(self.seating_plan)
            self.undo_stack.append(snapshot)
            # limit stack to reasonable size (e.g., 50)
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            # optionally show status
            if description:
                self.status_label.setText(f"Snapshot: {description}")
            else:
                self.status_label.setText("Snapshot saved for undo")
        except Exception as e:
            print("Could not push undo snapshot:", e)

    def undo(self):
        if not self.undo_stack:
            self.status_label.setText("Nothing to undo")
            return
        try:
            current = copy.deepcopy(self.seating_plan)
            self.redo_stack.append(current)
            snapshot = self.undo_stack.pop()
            self.seating_plan = copy.deepcopy(snapshot)
            # refresh UI
            self.refresh_section_table()
            if self.section_view.section and self.section_view.section.name in self.seating_plan.sections:
                self.section_view.load_section(self.seating_plan.sections[self.section_view.section.name])
            else:
                self.section_view.load_section(None)
            self.status_label.setText("\u21a9\ufe0f Undid last action")
        except Exception as e:
            QMessageBox.warning(self, "Undo failed", str(e))

    def redo(self):
        if not self.redo_stack:
            self.status_label.setText("Nothing to redo")
            return
        try:
            current = copy.deepcopy(self.seating_plan)
            self.undo_stack.append(current)
            snapshot = self.redo_stack.pop()
            self.seating_plan = copy.deepcopy(snapshot)
            self.refresh_section_table()
            if self.section_view.section and self.section_view.section.name in self.seating_plan.sections:
                self.section_view.load_section(self.seating_plan.sections[self.section_view.section.name])
            else:
                self.section_view.load_section(None)
            self.status_label.setText("\u21aa\ufe0f Redid action")
        except Exception as e:
            QMessageBox.warning(self, "Redo failed", str(e))

    # ---------- Core logic ----------
    def refresh_section_table(self):
        """Refresh section list with seat counts."""
        self.section_table.setRowCount(len(self.seating_plan.sections))
        for row_idx, (name, section) in enumerate(self.seating_plan.sections.items()):
            name_item = QTableWidgetItem(name)
            count_item = QTableWidgetItem(str(len(section.seats)))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.section_table.setItem(row_idx, 0, name_item)
            self.section_table.setItem(row_idx, 1, count_item)
        self.section_table.resizeColumnsToContents()

    def new_project(self, name):
        # new project resets plan; push snapshot first
        self.push_undo_snapshot("create new project")
        self.seating_plan = SeatingPlan(name)
        self.current_project = None
        self.section_view.load_section(None)
        self.refresh_section_table()
        self.status_label.setText("\ud83c\udd95 New project created")

    def new_project_dialog(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if not ok or not name:
            return
        self.new_project(name.strip())

    def save_project_dialog(self):
        # suggest filename using utils json helper behavior
        suggested = f"{self.seating_plan.name.replace(' ', '_').lower()}.seatproj"
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", suggested, "SeatProj (*.seatproj);;JSON (*.json);;All Files (*)")
        if not path:
            return
        # ensure extension
        if not path.lower().endswith((".json", ".seatproj")):
            path += ".seatproj"
        try:
            self.seating_plan.export_project(path)
            self.status_label.setText(f"\ud83d\udcbe Saved project: {Path(path).name} (Ctrl+S)")
        except Exception as e:
            QMessageBox.warning(self, "Save failed", str(e))

    def import_project(self):
        # import JSON as a new plan - push undo first
        self.push_undo_snapshot("import")
        sp = import_project_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_table()
            self.refresh_view()
            self.status_label.setText("\ud83d\udcc2 Imported seating plan")
    
    def import_from_excel(self):
        # import Excel as a new plan - push undo first
        self.push_undo_snapshot("import from Excel")
        sp = import_from_excel_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_table()
            self.refresh_view()
            self.status_label.setText("\ud83d\udcc2 Imported seating plan from Excel")

    def import_from_avail(self):
        # import Avail XML as a new plan - push undo first
        self.push_undo_snapshot("import from Avail")
        sp = import_from_avail_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_table()
            self.refresh_view()
            self.status_label.setText("\ud83d\udcc2 Imported seating plan from Avail file")

    def export_project(self):
        export_project_dialog(self, self.seating_plan)
        self.status_label.setText("\ud83d\udcbe Exported seating plan")

    def export_to_excel(self):
        export_to_excel_dialog(self, self.seating_plan)
        self.status_label.setText("\ud83d\udcbe Exported seating plan to Excel")

    def add_section_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("New section")
        layout = QVBoxLayout(dlg)

        name_edit = QLineEdit(dlg)
        name_edit.setPlaceholderText("Section name")
        layout.addWidget(name_edit)

        is_ga_cb = QCheckBox("Is General Admission (GA)?", dlg)
        layout.addWidget(is_ga_cb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dlg
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Section name cannot be empty.")
            return
        if name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return

        # push snapshot before modifying plan
        self.push_undo_snapshot(f"Add section '{name}'")

        # create section
        if is_ga_cb.isChecked():
            self.seating_plan.add_section(name=name, is_ga=True)
        else:
            self.seating_plan.add_section(name=name, is_ga=is_ga_cb.isChecked())

            # Load the newly created section into the view
            section_obj = self.seating_plan.sections.get(name)
            if section_obj:
                self.section_view.load_section(section_obj)
                try:
                    self.section_view.add_row_range_dialog()
                except Exception as e:
                    QMessageBox.warning(self, "Add rows", f"Could not open advanced dialog: {e}")

        # refresh UI to show added rows/seats
        self.refresh_section_table()
        section_obj = self.seating_plan.sections.get(name)
        if section_obj:
            self.section_view.load_section(section_obj)
        self.status_label.setText(f"Added section '{name}'")

    def clone_section_dialog(self):
        row = self.section_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a section to clone.")
            return
        src_name = self.section_table.item(row, 0).text()
        new_name, ok = QInputDialog.getText(self, "Clone section", "New section name:")
        if not ok or not new_name:
            return
        if new_name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return

        # snapshot before cloning
        self.push_undo_snapshot(f"Clone section '{src_name}' to '{new_name}'")

        self.seating_plan.clone_section(src_name, new_name)
        self.refresh_section_table()
        self.status_label.setText(f"Cloned '{src_name}' to '{new_name}'")

    def clone_section_many_dialog(self):
        """Clone the selected section multiple times with incrementing names."""
        row = self.section_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a section to clone.")
            return
        src_name = self.section_table.item(row, 0).text()

        num, ok = QInputDialog.getInt(self, "Clone section multiple", "Number of clones to create:", 1, 1, 500)
        if not ok or num <= 0:
            return

        # snapshot before cloning
        self.push_undo_snapshot(f"Clone section '{src_name}' x{num}")

        created = self.seating_plan.clone_section_many(src_name, num)
        self.refresh_section_table()
        if created:
            self.status_label.setText(f"Cloned '{src_name}' {len(created)} times: {', '.join(created)}")
        else:
            self.status_label.setText(f"No clones created for '{src_name}'")

    def delete_section(self):
        row = self.section_table.currentRow()
        if row < 0:
            return
        name = self.section_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Delete", f"Delete section '{name}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            # snapshot before deletion
            self.push_undo_snapshot(f"Delete section '{name}'")

            self.seating_plan.delete_section(name)
            self.refresh_section_table()
            self.section_view.load_section(None)
            self.status_label.setText(f"\ud83d\uddd1 Deleted section '{name}'")

    def rename_section_dialog(self):
        row = self.section_table.currentRow()
        if row < 0:
            return
        old = self.section_table.item(row, 0).text()
        new, ok = QInputDialog.getText(self, "Rename section", "New name:", text=old)
        if not ok or not new or new == old:
            return
        if new in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return

        # snapshot before rename
        self.push_undo_snapshot(f"Rename section '{old}' to '{new}'")

        self.seating_plan.rename_section(old, new)
        self.refresh_section_table()
        self.status_label.setText(f"\u270f\ufe0f Renamed section '{old}' to '{new}'")

    def toggle_sections_panel(self, checked):
        self.section_dock.setVisible(checked)

    def on_section_selected(self, row, col):
        """Triggered when a row is clicked in the table."""
        name_item = self.section_table.item(row, 0)
        if not name_item:
            return
        section = self.seating_plan.sections.get(name_item.text())
        if section:
            self.section_view.load_section(section)
            self.status_label.setText(f"\ud83d\udccd Loaded section '{name_item.text()}' ({len(section.seats)} seats)")
            # reset selected counter
            self.update_selected_count(0)

    def update_selected_count(self, selected_count: int):
        """Update selected seat count in status bar."""
        section_name = "None"
        total_seats = 0
        if self.section_view.section:
            section_name = self.section_view.section.name
            total_seats = len(self.section_view.section.seats)
        self.status_label.setText(
            f"Section: {section_name}  |  Seats: {total_seats}  |  Selected: {selected_count}"
        )

    def refresh_view(self):
        """Force redraw / reload current section to reflect model state."""
        if self.section_view.section and self.section_view.section.name in self.seating_plan.sections:
            self.section_view.load_section(self.seating_plan.sections[self.section_view.section.name])
            self.status_label.setText("\ud83d\udd04 View refreshed")
        else:
            self.section_view.load_section(None)
            self.status_label.setText("\ud83d\udd04 View refreshed (no section)")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()