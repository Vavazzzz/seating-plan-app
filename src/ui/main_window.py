# src/ui/main_window.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QDockWidget, QInputDialog,
    QFileDialog, QMessageBox, QAction
)
from PyQt6.QtCore import Qt
from ..models.seating_plan import SeatingPlan
from ..models.section import Section
from .section_view import SectionView
from ..utils.json_io import import_json_dialog, export_json_dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seating Plan Editor")
        self.resize(1000, 700)

        self.seating_plan = SeatingPlan()

        # central widget - section view
        self.section_view = SectionView(self)
        self.setCentralWidget(self.section_view)

        # dock - sections list
        self.section_list = QListWidget()
        dock = QDockWidget("Sections", self)
        dock.setWidget(self.section_list)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        # toolbar/menu
        self._build_actions()
        self._connect_signals()

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

    def _connect_signals(self):
        self.section_list.currentTextChanged.connect(self.on_section_selected)
        self.section_list.itemDoubleClicked.connect(self.on_section_double_clicked)

    def refresh_section_list(self):
        self.section_list.clear()
        for name in self.seating_plan.sections.keys():
            self.section_list.addItem(name)

    def new_plan(self):
        self.seating_plan = SeatingPlan()
        self.section_view.load_section(None)
        self.refresh_section_list()

    def import_json(self):
        sp = import_json_dialog(self)
        if sp:
            self.seating_plan = sp
            self.refresh_section_list()
            QMessageBox.information(self, "Imported", "Seating plan imported.")

    def export_json(self):
        export_json_dialog(self, self.seating_plan)

    def add_section_dialog(self):
        name, ok = QInputDialog.getText(self, "New section", "Section name:")
        if not ok or not name:
            return
        if name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return
        self.seating_plan.add_section(name)
        self.refresh_section_list()

    def clone_section_dialog(self):
        current = self.section_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No selection", "Select a section to clone.")
            return
        src_name = current.text()
        new_name, ok = QInputDialog.getText(self, "Clone section", "New section name:")
        if not ok or not new_name:
            return
        if new_name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return
        self.seating_plan.clone_section(src_name, new_name)
        self.refresh_section_list()

    def delete_section(self):
        current = self.section_list.currentItem()
        if not current:
            return
        name = current.text()
        confirm = QMessageBox.question(self, "Delete", f"Delete section '{name}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.seating_plan.delete_section(name)
            self.refresh_section_list()
            self.section_view.load_section(None)

    def rename_section_dialog(self):
        current = self.section_list.currentItem()
        if not current:
            return
        old = current.text()
        new, ok = QInputDialog.getText(self, "Rename section", "New name:", text=old)
        if not ok or not new or new == old:
            return
        if new in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return
        self.seating_plan.rename_section(old, new)
        self.refresh_section_list()

    def on_section_selected(self, name):
        if not name:
            self.section_view.load_section(None)
            return
        section = self.seating_plan.sections.get(name)
        if section:
            self.section_view.load_section(section)

    def on_section_double_clicked(self, item):
        self.on_section_selected(item.text())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
