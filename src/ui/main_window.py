import sys
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QInputDialog, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QStatusBar, QLabel, QCheckBox,
    QDialog, QLineEdit, QDialogButtonBox
)
from PyQt6.QtGui import QAction, QColor, QBrush
from PyQt6.QtCore import Qt, QMimeData, QByteArray
from ..models.seating_plan import SeatingPlan, MergeConflictError
from ..utils.json_io import import_project_dialog, import_from_excel_dialog, import_from_avail_dialog, export_project_dialog, export_to_excel_dialog
from .section_view import SectionView

class DragDropSectionTable(QTableWidget):
    """Custom QTableWidget that supports drag & drop to reorder sections."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disabilitare il drag drop automatico di PyQt per gestirlo manualmente
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.drag_source_row = None
        self.main_window = None  # Will be set by MainWindow
    
    def mousePressEvent(self, event):
        """Override mouse press to track drag source row."""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                # Only allow selection of non-checkbox columns for drag operations
                col = self.column(item)
                if col != 0:  # Not checkbox column
                    self.drag_source_row = self.row(item)
        super().mousePressEvent(event)
    
    def dropEvent(self, event):
        """Handle drop event to reorder sections."""
        if event.source() is not self:
            event.ignore()
            return
        
        # Get drop position (use position() instead of pos() for QDropEvent)
        drop_pos = event.position().toPoint()
        drop_index = self.indexAt(drop_pos).row()
        if drop_index < 0:
            drop_index = self.rowCount()
        
        if self.drag_source_row is not None and self.drag_source_row != drop_index:
            # Get section names in current order
            section_names = []
            for row in range(self.rowCount()):
                item = self.item(row, 1)
                if item:
                    section_names.append(item.text())
            
            # Calculate actual drop index (consider the drag source position)
            actual_drop_index = drop_index
            if drop_index > self.drag_source_row:
                actual_drop_index = drop_index - 1
            
            # Move the dragged section in the list
            if self.drag_source_row < len(section_names):
                dragged_name = section_names.pop(self.drag_source_row)
                section_names.insert(actual_drop_index, dragged_name)
                
                # Call reorder method on MainWindow
                if self.main_window:
                    self.main_window.on_sections_reordered(section_names)
        
        self.drag_source_row = None
        # Deselect all rows after drop
        self.clearSelection()
        event.accept()

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
        # Now includes a checkbox column for multi-selection
        self.section_table = DragDropSectionTable(0, 3)
        self.section_table.setHorizontalHeaderLabels(["Select", "Section", "Seats"])
        # Resize: checkbox small, section stretch, seats fit contents
        self.section_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.section_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.section_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.section_table.verticalHeader().setVisible(False)
        self.section_table.setEditTriggers(self.section_table.EditTrigger.NoEditTriggers)

        # Set reference to MainWindow in the table for callbacks
        self.section_table.main_window = self

        # track checked state between refreshes: {section_name: bool}
        self.section_checks: dict[str, bool] = {}
        # used to suppress itemChanged handling during programmatic updates
        self._suppress_section_table_signals = False

        # --- Total row (pinned at bottom) ---
        self.section_total_table = QTableWidget(1, 2)
        self.section_total_table.horizontalHeader().setVisible(False)
        self.section_total_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.section_total_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.section_total_table.verticalHeader().setVisible(False)
        self.section_total_table.setMaximumHeight(50)
        self.section_total_table.setSelectionBehavior(self.section_total_table.SelectionBehavior.SelectRows)
        self.section_total_table.setEditTriggers(self.section_total_table.EditTrigger.NoEditTriggers)

        # Add section button
        dock_widget_container = QWidget()
        dock_layout = QVBoxLayout()
        self.add_section_btn = QPushButton("\u2795 Add Section")
        self.add_section_btn.setToolTip("Add a new section (Ctrl+N creates a new project; add section here)")
        dock_layout.addWidget(self.add_section_btn)
        dock_layout.addWidget(self.section_table)
        dock_layout.addWidget(self.section_total_table)
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

        merge_sections_action = QAction("Merge Sections...", self)
        merge_sections_action.setToolTip("Merge selected sections into a new section")
        merge_sections_action.triggered.connect(self.merge_sections_dialog)
        edit_menu.addAction(merge_sections_action)

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
        # keep track of checkbox changes to persist selections between refreshes
        try:
            self.section_table.itemChanged.connect(self.on_section_checkbox_changed)
        except Exception:
            # in some test contexts signals may not be available; guard defensively
            pass
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

        total_seats = 0
        # preserve previous check states for existing section names
        prev_checks = dict(self.section_checks)
        self.section_checks = {}

        # prevent handling itemChanged while we populate rows
        self._suppress_section_table_signals = True
        try:
            for row_idx, (name, section) in enumerate(self.seating_plan.sections.items()):
                # checkbox item
                check_item = QTableWidgetItem()
                check_item.setFlags(check_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                checked = Qt.CheckState.Checked if prev_checks.get(name, False) else Qt.CheckState.Unchecked
                check_item.setCheckState(checked)
                # name and count items
                name_item = QTableWidgetItem(name)
                seat_count = len(section.seats)
                count_item = QTableWidgetItem(str(seat_count))
                count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.section_table.setItem(row_idx, 0, check_item)
                self.section_table.setItem(row_idx, 1, name_item)
                self.section_table.setItem(row_idx, 2, count_item)

                # update bookkeeping
                self.section_checks[name] = (checked == Qt.CheckState.Checked)
                total_seats += seat_count
        finally:
            self._suppress_section_table_signals = False
        
        # Update total row at the bottom
        total_name_item = QTableWidgetItem("TOTAL")
        total_count_item = QTableWidgetItem(str(total_seats))
        total_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.section_total_table.setItem(0, 0, total_name_item)
        self.section_total_table.setItem(0, 1, total_count_item)
        
        self.section_table.resizeColumnsToContents()
        self.section_total_table.resizeColumnsToContents()

    def get_checked_section_names(self) -> list[str]:
        """Return a list of section names currently checked in the table."""
        return [name for name, checked in self.section_checks.items() if checked]

    def on_section_checkbox_changed(self, item: QTableWidgetItem):
        """Handle user toggling a checkbox in the first column."""
        if self._suppress_section_table_signals:
            return
        try:
            if item.column() != 0:
                return
        except Exception:
            # some test contexts may not provide column
            return
        # get corresponding section name from same row
        row = item.row()
        name_item = self.section_table.item(row, 1)
        if not name_item:
            return
        name = name_item.text()
        self.section_checks[name] = (item.checkState() == Qt.CheckState.Checked)
        # update status to show number of checked sections
        checked_count = len(self.get_checked_section_names())
        self.status_label.setText(f"Checked: {checked_count}")

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
        # prefer checkbox selection; fall back to current row
        checked = self.get_checked_section_names()
        if len(checked) == 1:
            src_name = checked[0]
        elif len(checked) > 1:
            QMessageBox.warning(self, "Multiple selected", "Select only one section to clone.")
            return
        else:
            row = self.section_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No selection", "Select a section to clone.")
                return
            src_name = self.section_table.item(row, 1).text()
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
        checked = self.get_checked_section_names()
        if len(checked) == 1:
            src_name = checked[0]
        elif len(checked) > 1:
            QMessageBox.warning(self, "Multiple selected", "Select only one section to clone multiple times.")
            return
        else:
            row = self.section_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No selection", "Select a section to clone.")
                return
            src_name = self.section_table.item(row, 1).text()

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
        # collect checked section names
        names = self.get_checked_section_names()
        if not names:
            QMessageBox.warning(self, "No selection", "Check one or more sections to delete.")
            return
        confirm = QMessageBox.question(self, "Delete", f"Delete selected sections: {', '.join(names)} ?")
        if confirm == QMessageBox.StandardButton.Yes:
            # snapshot before deletion
            self.push_undo_snapshot(f"Delete sections: {', '.join(names)}")
            for name in names:
                try:
                    self.seating_plan.delete_section(name)
                except Exception as e:
                    QMessageBox.warning(self, "Delete failed", f"Could not delete '{name}': {e}")
            self.refresh_section_table()
            # if current view was one of deleted, clear
            if self.section_view.section and self.section_view.section.name not in self.seating_plan.sections:
                self.section_view.load_section(None)
            self.status_label.setText(f"\ud83d\uddd1 Deleted sections: {', '.join(names)}")

    def rename_section_dialog(self):
        # prefer checkbox selection (exactly one); fall back to current row
        checked = self.get_checked_section_names()
        if len(checked) == 1:
            old = checked[0]
        elif len(checked) > 1:
            QMessageBox.warning(self, "Multiple selected", "Select only one section to rename.")
            return
        else:
            row = self.section_table.currentRow()
            if row < 0:
                return
            old = self.section_table.item(row, 1).text()
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

    def merge_sections_dialog(self):
        """Merge multiple selected sections into a new section."""
        # collect selected section names via checkboxes
        selected_names = self.get_checked_section_names()
        if len(selected_names) < 2:
            QMessageBox.warning(self, "Select sections", "Check two or more sections to merge.")
            return

        new_name, ok = QInputDialog.getText(self, "Merge Sections", "New section name:")
        if not ok or not new_name:
            return
        if new_name in self.seating_plan.sections:
            QMessageBox.warning(self, "Exists", "Section with that name already exists.")
            return

        # push undo snapshot before merging
        self.push_undo_snapshot(f"Merge sections: {', '.join(selected_names)} -> {new_name}")

        try:
            self.seating_plan.merge_sections(selected_names, new_name)
        except MergeConflictError as e:
            QMessageBox.warning(self, "Merge conflict", str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, "Merge failed", str(e))
            return

        # success: refresh and load merged section
        self.refresh_section_table()
        self.section_view.load_section(self.seating_plan.sections.get(new_name))
        self.status_label.setText(f"Merged sections into '{new_name}'")

    def toggle_sections_panel(self, checked):
        self.section_dock.setVisible(checked)

    def on_section_selected(self, row, col):
        """Triggered when a row is clicked in the table."""
        # ignore clicks on the checkbox column (column 0)
        if col == 0:
            return
        name_item = self.section_table.item(row, 1)
        if not name_item:
            return
        section = self.seating_plan.sections.get(name_item.text())
        if section:
            self.section_view.load_section(section)
            self.status_label.setText(f"\ud83d\udccd Loaded section '{name_item.text()}' ({len(section.seats)} seats)")
            # reset selected counter
            self.update_selected_count(0)

    def on_sections_reordered(self, section_names: list):
        """Reorder sections in SeatingPlan based on new order from drag & drop."""
        try:
            # Push undo snapshot BEFORE modifying
            self.push_undo_snapshot("Reorder sections")
            
            # Create new ordered dict
            new_sections = {}
            for name in section_names:
                if name in self.seating_plan.sections:
                    new_sections[name] = self.seating_plan.sections[name]
            
            # Update seating plan with new order
            self.seating_plan.sections = new_sections
            
            # Refresh the table to reflect new order
            self.refresh_section_table()
            
            self.status_label.setText("📝 Sections reordered")
        except Exception as e:
            QMessageBox.warning(self, "Reorder Failed", str(e))

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