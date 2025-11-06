# src/ui/main_window.py
import sys
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QInputDialog, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QStatusBar, QLabel 
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from string import ascii_uppercase
from ..models.seating_plan import SeatingPlan
from ..utils.json_io import import_project_dialog, export_project_dialog
from .section_view import SectionView, RangeInputDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seating Plan Editor")
        self.resize(1100, 750)

        self.seating_plan = SeatingPlan()
        self.current_project = None

        # Undo/Redo stacks (store deep copies of SeatingPlan)
        self.undo_stack = []
        self.redo_stack = []

        # --- Central Section View ---
        self.section_view = SectionView(self)
        self.setCentralWidget(self.section_view)
        self.section_view.selectionChanged.connect(self.update_selected_count)
        # when a change is already done we refresh table; we also want to capture pre-change snapshots
        self.section_view.sectionModified.connect(self.refresh_section_table)
        # when section_view is about to modify, push an undo snapshot
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
        self.add_section_btn = QPushButton("➕ Add Section")
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
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        # Save project (Ctrl+S)
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Save current project (Ctrl+S)")
        save_action.triggered.connect(self.save_project_dialog)
        file_menu.addAction(save_action)

        import_action = QAction("Import seating plan...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.setToolTip("Import seating plan (Ctrl+O)")
        import_action.triggered.connect(self.import_project)
        file_menu.addAction(import_action)

        export_action = QAction("Export JSON...", self)
        export_action.setToolTip("Export seating plan JSON")
        export_action.triggered.connect(self.export_project)
        file_menu.addAction(export_action)

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
            # if a section is loaded, reload it (choose same name if exists)
            if self.section_view.section and self.section_view.section.name in self.seating_plan.sections:
                self.section_view.load_section(self.seating_plan.sections[self.section_view.section.name])
            else:
                self.section_view.load_section(None)
            self.status_label.setText("↩️ Undid last action")
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
            self.status_label.setText("↪️ Redid action")
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

    def new_project(self):
        # new project resets plan; push snapshot first
        self.push_undo_snapshot("create new project")
        self.seating_plan = SeatingPlan()
        self.current_project = None
        self.section_view.load_section(None)
        self.refresh_section_table()
        self.status_label.setText("🆕 New project created")

    def save_project_dialog(self):
        # suggest filename using utils json helper behavior
        suggested = "seating_plan.seatproj"
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", suggested, "SeatProj (*.seatproj);;JSON (*.json);;All Files (*)")
        if not path:
            return
        # ensure extension
        if not path.lower().endswith((".json", ".seatproj")):
            path += ".seatproj"
        try:
            self.seating_plan.export_to_json(path)
            self.status_label.setText(f"💾 Saved project: {Path(path).name} (Ctrl+S)")
        except Exception as e:
            QMessageBox.warning(self, "Save failed", str(e))

    def import_project(self):
        # import JSON as a new plan - push undo first
        self.push_undo_snapshot("import")
        sp = import_project_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_table()
            self.status_label.setText("📂 Imported seating plan")

    def export_project(self):
        export_project_dialog(self, self.seating_plan)
        self.status_label.setText("💾 Exported seating plan")

    def add_section_dialog(self):
        name, ok = QInputDialog.getText(self, "New section", "Section name:")
        if not ok or not name:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Section name cannot be empty.")
            return
        if name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return

        # push snapshot before modifying plan
        self.push_undo_snapshot(f"Add section '{name}'")

        # create section
        self.seating_plan.add_section(name)

        # Load the newly created section into the view and immediately open the row-range dialog
        section_obj = self.seating_plan.sections.get(name)
        if section_obj:
            self.section_view.load_section(section_obj)

            # call the SectionView dialog to add rows/seats (fallback to simple inputs on error)
            try:
                self.section_view.add_row_range_dialog()
            except Exception as e:
                QMessageBox.warning(self, "Add rows", f"Could not open advanced dialog: {e}")
                sr, ok1 = QInputDialog.getText(self, "Start row", "Start row label:")
                if ok1:
                    er, ok2 = QInputDialog.getText(self, "End row", "End row label:")
                    if ok2:
                        ss, ok3 = QInputDialog.getInt(self, "Start seat", "Start seat number:", 1, 1)
                        if ok3:
                            es, ok4 = QInputDialog.getInt(self, "End seat", "End seat number:", 1, 1)
                            if ok4:
                                try:
                                    s = int(sr); e = int(er)
                                    rows = [str(i) for i in range(min(s, e), max(s, e) + 1)]
                                except ValueError:
                                    try:
                                        si = ascii_uppercase.index(sr.upper())
                                        ei = ascii_uppercase.index(er.upper())
                                        rows = list(ascii_uppercase[min(si, ei):max(si, ei) + 1])
                                    except Exception:
                                        rows = []
                                for r in rows:
                                    self.seating_plan.sections[name].add_seat_range(r, min(ss, es), max(ss, es))

        # refresh UI to show added rows/seats
        self.refresh_section_table()
        # automatically load the new section in the view
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
            self.status_label.setText(f"🗑 Deleted section '{name}'")

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
        self.status_label.setText(f"✏️ Renamed section '{old}' to '{new}'")

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
            self.status_label.setText(f"📍 Loaded section '{name_item.text()}' ({len(section.seats)} seats)")
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
            self.status_label.setText("🔄 View refreshed")
        else:
            self.section_view.load_section(None)
            self.status_label.setText("🔄 View refreshed (no section)")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
