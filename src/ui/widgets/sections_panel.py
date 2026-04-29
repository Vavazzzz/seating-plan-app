"""Section management panel widget."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import pyqtSignal, Qt
from typing import TYPE_CHECKING, Optional

from .base import BasePanel
from ..dialogs import (
    AddSectionDialog,
    RenameSectionDialog,
    CloneSectionDialog,
    CloneSectionManyDialog,
    MergeSectionsDialog,
)

if TYPE_CHECKING:
    from application.services import SectionService


class SectionsPanel(BasePanel):
    """Panel for managing sections."""
    
    # Signals
    section_selected = pyqtSignal(str)  # Emits section name
    section_changed = pyqtSignal()  # Emits when sections list changes
    section_added = pyqtSignal(str)  # Emits name of newly created section
    
    def __init__(self, section_service: "SectionService", parent=None):
        super().__init__(parent)
        self.section_service = section_service
        # Track checkbox states: {section_name: bool}
        self.section_checks: dict[str, bool] = {}
        self._suppress_checkbox_signals = False
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Sections table with 3 columns: Select (checkbox), Section name, Seats
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(3)
        self.sections_table.setHorizontalHeaderLabels(["Select", "Section", "Seats"])
        self.sections_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.sections_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.sections_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.sections_table.verticalHeader().setVisible(False)
        self.sections_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.sections_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.sections_table.itemChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.sections_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        addsec_btn = QPushButton("Add Section")
        addsec_btn.clicked.connect(self._add_section)
        button_layout.addWidget(addsec_btn)
        
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self._rename_section)
        button_layout.addWidget(rename_btn)
        
        clone_btn = QPushButton("Clone")
        clone_btn.clicked.connect(self._clone_section)
        button_layout.addWidget(clone_btn)

        clone_many_btn = QPushButton("Clone Multiple")
        clone_many_btn.clicked.connect(self._clone_section_many)
        button_layout.addWidget(clone_many_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_section)
        button_layout.addWidget(delete_btn)
        
        merge_btn = QPushButton("Merge")
        merge_btn.clicked.connect(self._merge_sections)
        button_layout.addWidget(merge_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

        rename_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        rename_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        rename_shortcut.activated.connect(self._rename_section)

        add_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        add_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        add_shortcut.activated.connect(self._add_section)
    
    def refresh(self) -> None:
        """Refresh the sections table."""
        sections = self.section_service.get_section_names()
        seating_plan = self.section_service.seating_plan
        
        self.sections_table.setRowCount(len(sections))
        
        # Preserve previous checkbox states
        prev_checks = dict(self.section_checks)
        self.section_checks = {}
        
        self._suppress_checkbox_signals = True
        try:
            for row, section_name in enumerate(sections):
                # Column 0: Checkbox
                check_item = QTableWidgetItem()
                check_item.setFlags(check_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                checked = Qt.CheckState.Checked if prev_checks.get(section_name, False) else Qt.CheckState.Unchecked
                check_item.setCheckState(checked)
                self.sections_table.setItem(row, 0, check_item)
                
                # Column 1: Section name
                name_item = QTableWidgetItem(section_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.sections_table.setItem(row, 1, name_item)
                
                # Column 2: Seat count
                section = seating_plan.sections[section_name]
                seat_count = len(section.seats) if section.seats else 0
                count_item = QTableWidgetItem(str(seat_count))
                count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.sections_table.setItem(row, 2, count_item)
                
                # Update checkbox tracking
                self.section_checks[section_name] = (checked == Qt.CheckState.Checked)
        finally:
            self._suppress_checkbox_signals = False
    
    def get_selected_section(self) -> Optional[str]:
        """Get the currently selected section name for display."""
        index = self.sections_table.currentRow()
        if index >= 0:
            item = self.sections_table.item(index, 1)  # Column 1 is section name
            if item:
                return item.text()
        return None
    
    def select_section(self, name: str) -> None:
        """Select a section by name in the table."""
        for row in range(self.sections_table.rowCount()):
            item = self.sections_table.item(row, 1)
            if item and item.text() == name:
                self.sections_table.setCurrentCell(row, 1)
                break

    def get_checked_sections(self) -> list[str]:
        """Get all checked section names for multi-select operations."""
        return [name for name, checked in self.section_checks.items() if checked]
    
    def set_checked_sections(self, section_names: list[str]) -> None:
        """Set which sections should be checked."""
        self._suppress_checkbox_signals = True
        try:
            for row in range(self.sections_table.rowCount()):
                item = self.sections_table.item(row, 1)
                if item:
                    section_name = item.text()
                    checkbox_item = self.sections_table.item(row, 0)
                    if checkbox_item:
                        is_checked = section_name in section_names
                        checkbox_item.setCheckState(
                            Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
                        )
                        self.section_checks[section_name] = is_checked
        finally:
            self._suppress_checkbox_signals = False
    
    def clear_checked(self) -> None:
        """Uncheck all sections."""
        self.set_checked_sections([])
    
    def _on_checkbox_changed(self, item: QTableWidgetItem) -> None:
        """Handle checkbox state change in column 0."""
        if self._suppress_checkbox_signals or item.column() != 0:
            return
        
        row = self.sections_table.row(item)
        if row < 0:
            return
        
        section_item = self.sections_table.item(row, 1)
        if section_item:
            section_name = section_item.text()
            is_checked = item.checkState() == Qt.CheckState.Checked
            self.section_checks[section_name] = is_checked
    
    def _on_selection_changed(self) -> None:
        """Handle section selection change - display selected section."""
        section_name = self.get_selected_section()
        if section_name:
            self.section_selected.emit(section_name)
    
    def _add_section(self) -> None:
        """Add a new section."""
        dialog = AddSectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_value()
            is_ga = dialog.is_checked()
            
            result = self.section_service.add_section(name, is_ga)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.section_added.emit(name)
                self.show_success(f"Section '{name}' added")
            else:
                self.show_error("Error", str(result.error))
    
    def _delete_section(self) -> None:
        """Delete selected section(s) - supports multi-delete via checkboxes."""
        # Get checked sections for multi-delete
        checked = self.get_checked_sections()
        # Get selected section for single-delete fallback
        selected = self.get_selected_section()
        
        # Determine which sections to delete
        to_delete = checked if checked else ([selected] if selected else [])
        
        if not to_delete:
            self.show_warning("Warning", "No section selected")
            return
        
        # Confirm deletion
        if len(to_delete) > 1:
            msg = f"Delete {len(to_delete)} sections?"
        else:
            msg = f"Delete section '{to_delete[0]}'?"
        
        if not self.confirm("Confirm Delete", msg):
            return
        
        # Delete all selected sections
        failed = []
        for section_name in to_delete:
            result = self.section_service.delete_section(section_name)
            if not result.is_success():
                failed.append((section_name, str(result.error)))
        
        # Update UI
        self.refresh()
        self.section_changed.emit()
        
        # Provide feedback
        if failed:
            error_msg = "\n".join([f"{name}: {err}" for name, err in failed])
            self.show_error("Some deletions failed", error_msg)
        else:
            msg = f"Deleted {len(to_delete)} section(s)"
            self.show_success(msg)
    
    def _rename_section(self) -> None:
        """Rename the selected section."""
        old_name = self.get_selected_section()
        if not old_name:
            self.show_warning("Warning", "No section selected")
            return

        dialog = RenameSectionDialog(old_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_value()
            if old_name != new_name:
                result = self.section_service.rename_section(old_name, new_name)
                if result.is_success():
                    self.refresh()
                    self.section_changed.emit()
                    self.show_success(f"Section renamed to '{new_name}'")
                else:
                    self.show_error("Error", str(result.error))
    
    def _clone_section(self) -> None:
        """Clone the selected section."""
        index = self.sections_table.currentRow()
        if index < 0:
            self.show_warning("Warning", "No section selected")
            return
        
        # Column 1 is the section name (column 0 is checkbox)
        source_item = self.sections_table.item(index, 1)
        if not source_item:
            self.show_warning("Warning", "No section selected")
            return
        
        source_name = source_item.text()
        dialog = CloneSectionDialog(source_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            clone_name = dialog.get_clone_name()
            result = self.section_service.clone_section(source_name, clone_name)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.show_success(f"Section cloned to '{clone_name}'")
            else:
                self.show_error("Error", str(result.error))
    
    def _clone_section_many(self) -> None:
        """Clone the selected section multiple times with auto-generated names."""
        index = self.sections_table.currentRow()
        if index < 0:
            self.show_warning("Warning", "No section selected")
            return

        source_item = self.sections_table.item(index, 1)
        if not source_item:
            self.show_warning("Warning", "No section selected")
            return

        source_name = source_item.text()
        dialog = CloneSectionManyDialog(source_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            count = dialog.get_count()
            result = self.section_service.clone_section_many(source_name, count)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                names = result.value
                self.show_success(f"Created {len(names)} clone(s): {', '.join(names)}")
            else:
                self.show_error("Error", str(result.error))

    def _merge_sections(self) -> None:
        """Merge checked sections into a new named section."""
        checked = self.get_checked_sections()

        if len(checked) < 2:
            self.show_warning("Warning", "Select at least 2 sections to merge")
            return

        dialog = MergeSectionsDialog(checked, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_new_name()
            delete_sources = dialog.delete_sources_checked()

            if not new_name:
                self.show_warning("Warning", "New section name cannot be empty")
                return

            result = self.section_service.merge_sections(checked, new_name, delete_sources)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.show_success(f"Merged {len(checked)} sections into '{new_name}'")
            else:
                self.show_error("Error", str(result.error))
