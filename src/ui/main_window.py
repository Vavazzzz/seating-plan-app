# src/ui/main_window.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QInputDialog, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QStatusBar, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from string import ascii_uppercase
from ..models.seating_plan import SeatingPlan
from ..utils.json_io import import_json_dialog, export_json_dialog
from .section_view import SectionView, RangeInputDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seating Plan Editor")
        self.resize(1100, 750)

        self.seating_plan = SeatingPlan()

        # --- Central Section View ---
        self.section_view = SectionView(self)
        self.setCentralWidget(self.section_view)
        self.section_view.selectionChanged.connect(self.update_selected_count)
        self.section_view.sectionModified.connect(self.refresh_section_table)


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

        new_action = QAction("New Plan", self)
        new_action.triggered.connect(self.new_plan)
        file_menu.addAction(new_action)

        import_action = QAction("Import JSON...", self)
        import_action.triggered.connect(self.import_json)
        file_menu.addAction(import_action)

        export_action = QAction("Export JSON...", self)
        export_action.triggered.connect(self.export_json)
        file_menu.addAction(export_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        add_section_action = QAction("Add Section", self)
        add_section_action.triggered.connect(self.add_section_dialog)
        edit_menu.addAction(add_section_action)

        clone_section_action = QAction("Clone Section", self)
        clone_section_action.triggered.connect(self.clone_section_dialog)
        edit_menu.addAction(clone_section_action)

        delete_section_action = QAction("Delete Section", self)
        delete_section_action.triggered.connect(self.delete_section)
        edit_menu.addAction(delete_section_action)

        rename_section_action = QAction("Rename Section", self)
        rename_section_action.triggered.connect(self.rename_section_dialog)
        edit_menu.addAction(rename_section_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        self.toggle_sections_action = QAction("Sections Panel", self, checkable=True)
        self.toggle_sections_action.setChecked(True)
        self.toggle_sections_action.triggered.connect(self.toggle_sections_panel)
        view_menu.addAction(self.toggle_sections_action)

    def _connect_signals(self):
        self.add_section_btn.clicked.connect(self.add_section_dialog)
        self.section_table.cellClicked.connect(self.on_section_selected)
        self.section_dock.visibilityChanged.connect(lambda visible: self.toggle_sections_action.setChecked(visible))

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

    def new_plan(self):
        self.seating_plan = SeatingPlan()
        self.section_view.load_section(None)
        self.refresh_section_table()
        self.status_label.setText("🆕 New seating plan")

    def import_json(self):
        sp = import_json_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_table()
            self.status_label.setText("📂 Imported seating plan")

    def export_json(self):
        export_json_dialog(self, self.seating_plan)
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

        # create section
        self.seating_plan.add_section(name)

        # Load the newly created section into the view and immediately open the row-range dialog
        section_obj = self.seating_plan.sections.get(name)
        if section_obj:
            # ensure the view is operating on the section we just created
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
                                # add ranges directly to model
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
        # refresh UI and load created section
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


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
