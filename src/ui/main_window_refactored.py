"""Refactored MainWindow using Application Services Layer."""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget,
    QStatusBar, QLabel, QMessageBox, QDialog
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

from domain.models.seating_plan import SeatingPlan
from application.handlers import CommandHandler
from application.services import (
    SeatingPlanService,
    SectionService,
    SeatService,
)
from infrastructure.import_export import (
    JSONImporter,
    ExcelImporter,
    AvailImporter,
    JSONExporter,
    ExcelExporter,
)
from infrastructure.persistence import JSONRepository
from .widgets import SectionsPanel
from .section_view import SectionView
from .dialogs import FileDialog, NewPlanDialog


class RefactoredMainWindow(QMainWindow):
    """Lean MainWindow using services layer (< 250 lines)."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seating Plan Editor (Refactored)")
        self.resize(1200, 800)
        
        # Initialize domain and services
        self.seating_plan = SeatingPlan("Untitled")
        self.command_handler = CommandHandler()
        
        # Configure services with importers/exporters
        services_config = {
            "importers": [JSONImporter(), ExcelImporter(), AvailImporter()],
            "exporters": [JSONExporter(), ExcelExporter()],
            "repository": JSONRepository(),
        }
        
        self.plan_service = SeatingPlanService(
            self.seating_plan,
            self.command_handler,
            services_config
        )
        self.section_service = self.plan_service.get_section_service()
        self.seat_service = SeatService(self.seating_plan, self.command_handler)
        
        self.current_project_path = None
        
        # Build UI
        self._create_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
        # Connect service callbacks
        self._setup_callbacks()
        
        # Initial load
        self._refresh_ui()
    
    def _create_ui(self) -> None:
        """Create main UI layout."""
        central = QWidget()
        layout = QHBoxLayout()
        
        # Sections panel (left)
        self.sections_panel = SectionsPanel(self.section_service, self)
        self.sections_panel.section_changed.connect(self._on_sections_changed)
        self.sections_panel.section_selected.connect(self._on_section_selected)
        self.sections_panel.section_added.connect(self._on_section_added)
        layout.addWidget(self.sections_panel, 0)
        
        # Section view (right) - shows seat grid
        self.section_view = SectionView(self)
        self.section_view.set_seat_service(self.seat_service)
        self.section_view.sectionModified.connect(self._refresh_ui)
        layout.addWidget(self.section_view, 2)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
    
    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_plan)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_plan)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_plan)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_plan_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_plan)
        file_menu.addAction(export_action)

        import_action = QAction("Import...", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self._import_plan)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
    
    def _create_toolbar(self) -> None:
        """Create toolbar (optional)."""
        # Can be extended with common actions
        pass
    
    def _create_status_bar(self) -> None:
        """Create status bar."""
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label, 1)
    
    def _setup_callbacks(self) -> None:
        """Setup service callbacks."""
        # Error messages to status bar
        def on_error(msg):
            self.status_label.setText(f"Error: {msg}")
        
        self.sections_panel.set_error_callback(on_error)
    
    def _refresh_ui(self) -> None:
        """Refresh all UI elements."""
        info = self.plan_service.get_plan_info()
        self.setWindowTitle(f"Seating Plan: {info['name']}")
        self.sections_panel.refresh()
        self.status_label.setText(
            f"{info['sections']} sections, {info['total_seats']} seats"
        )
        
        # Re-display currently selected section
        selected = self.sections_panel.get_selected_section()
        if selected and selected in self.seating_plan.sections:
            section = self.seating_plan.sections[selected]
            self.section_view.load_section(section)
    
    # File operations
    
    def _new_plan(self) -> None:
        """Create a new plan."""
        dialog = NewPlanDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            plan_name = dialog.get_value()
            if plan_name:  # get_value() strips whitespace
                result = self.plan_service.create_new_plan(plan_name)
                if result.is_success():
                    self.current_project_path = None
                    self._refresh_ui()
                    self.status_label.setText("New plan created")
                else:
                    QMessageBox.critical(self, "Error", str(result.error))
            else:
                QMessageBox.warning(self, "Validation", "Plan name cannot be empty")
        # If dialog is rejected (Cancel clicked), do nothing
    
    def _open_plan(self) -> None:
        """Open a seating plan file."""
        path = FileDialog.get_open_path(
            self,
            "Open Seating Plan",
            "Seating Files (*.json *.xlsx);;All Files (*)"
        )
        
        if path:
            result = self.plan_service.load_seating_plan(path)
            if result.is_success():
                self.current_project_path = path
                self._refresh_ui()
                self.status_label.setText(f"Loaded: {Path(path).name}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to load: {result.error}")
    
    def _save_plan(self) -> None:
        """Save the current plan."""
        if not self.current_project_path:
            self._save_plan_as()
            return
        
        result = self.plan_service.save_seating_plan(self.current_project_path)
        if result.is_success():
            self.status_label.setText("Saved")
        else:
            QMessageBox.critical(self, "Error", f"Failed to save: {result.error}")
    
    def _save_plan_as(self) -> None:
        """Save the plan with a new path."""
        path = FileDialog.get_save_path(
            self,
            "Save Seating Plan",
            "JSON Files (*.json)"
        )
        
        if path:
            result = self.plan_service.save_seating_plan(path)
            if result.is_success():
                self.current_project_path = path
                self.status_label.setText(f"Saved: {Path(path).name}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save: {result.error}")
    
    def _import_plan(self) -> None:
        """Import a seating plan from file."""
        path = FileDialog.get_open_path(
            self,
            "Import Seating Plan",
            "All Formats (*.json *.xlsx *.xml);;JSON (*.json);;Excel (*.xlsx);;Avail (*.xml)"
        )
        
        if path:
            result = self.plan_service.import_seating_plan(path)
            if result.is_success():
                self.current_project_path = None
                self._refresh_ui()
                self.status_label.setText(f"Imported: {Path(path).name}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to import: {result.error}")
    
    def _export_plan(self) -> None:
        """Export the plan to a file."""
        path = FileDialog.get_save_path(
            self,
            "Export Seating Plan",
            "Excel Files (*.xlsx)"
        )
        
        if path:
            result = self.plan_service.export_seating_plan(path)
            if result.is_success():
                self.status_label.setText(f"Exported: {Path(path).name}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to export: {result.error}")
    
    # Edit operations
    
    def _undo(self) -> None:
        """Undo the last operation."""
        result = self.plan_service.undo()
        if result.is_success():
            self._refresh_ui()
            self.status_label.setText("Undo")
        elif result.error and result.error.has_errors():
            self.status_label.setText(str(result.error))
    
    def _redo(self) -> None:
        """Redo the last undone operation."""
        result = self.plan_service.redo()
        if result.is_success():
            self._refresh_ui()
            self.status_label.setText("Redo")
        elif result.error and result.error.has_errors():
            self.status_label.setText(str(result.error))
    
    def _on_sections_changed(self) -> None:
        """Handle sections change."""
        self._refresh_ui()
    
    def _on_section_selected(self, section_name: str) -> None:
        """Handle section selection - display in SectionView."""
        if section_name in self.seating_plan.sections:
            section = self.seating_plan.sections[section_name]
            self.section_view.load_section(section)
            self.status_label.setText(f"Section: {section_name}")

    def _on_section_added(self, section_name: str) -> None:
        """Select the new section and immediately open the row range dialog."""
        self.sections_panel.select_section(section_name)
        if section_name in self.seating_plan.sections:
            self.section_view.load_section(self.seating_plan.sections[section_name])
        self.section_view.add_row_range_dialog()


def main():
    """Application entry point."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = RefactoredMainWindow()
    window.show()
    sys.exit(app.exec())
