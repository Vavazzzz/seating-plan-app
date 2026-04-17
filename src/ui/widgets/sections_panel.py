"""Section management panel widget."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import TYPE_CHECKING, Optional

from .base import BasePanel
from ..dialogs import (
    AddSectionDialog,
    RenameSectionDialog,
    CloneSectionDialog,
    MergeSectionsDialog,
)

if TYPE_CHECKING:
    from ...application.services import SectionService


class SectionsPanel(BasePanel):
    """Panel for managing sections."""
    
    # Signals
    section_selected = pyqtSignal(str)  # Emits section name
    section_changed = pyqtSignal()  # Emits when sections list changes
    
    def __init__(self, section_service: "SectionService", parent=None):
        super().__init__(parent)
        self.section_service = section_service
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Sections table
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(1)
        self.sections_table.setHorizontalHeaderLabels(["Sections"])
        self.sections_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.sections_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.sections_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.sections_table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.sections_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Section")
        add_btn.clicked.connect(self._add_section)
        button_layout.addWidget(add_btn)
        
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self._rename_section)
        button_layout.addWidget(rename_btn)
        
        clone_btn = QPushButton("Clone")
        clone_btn.clicked.connect(self._clone_section)
        button_layout.addWidget(clone_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_section)
        button_layout.addWidget(delete_btn)
        
        merge_btn = QPushButton("Merge")
        merge_btn.clicked.connect(self._merge_sections)
        button_layout.addWidget(merge_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def refresh(self) -> None:
        """Refresh the sections table."""
        sections = self.section_service.get_section_names()
        
        self.sections_table.setRowCount(len(sections))
        for row, section_name in enumerate(sections):
            item = QTableWidgetItem(section_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.sections_table.setItem(row, 0, item)
    
    def get_selected_section(self) -> Optional[str]:
        """Get the currently selected section name."""
        index = self.sections_table.currentRow()
        if index >= 0:
            item = self.sections_table.item(index, 0)
            if item:
                return item.text()
        return None
    
    def _on_selection_changed(self) -> None:
        """Handle section selection change."""
        index = self.sections_table.currentRow()
        if index >= 0:
            item = self.sections_table.item(index, 0)
            if item:
                self.section_selected.emit(item.text())
    
    def _add_section(self) -> None:
        """Add a new section."""
        dialog = AddSectionDialog(self)
        if dialog.exec() == dialog.Accepted:
            name = dialog.get_value()
            is_ga = dialog.is_checked()
            
            result = self.section_service.add_section(name, is_ga)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.show_success(f"Section '{name}' added")
            else:
                self.show_error("Error", str(result.error))
    
    def _delete_section(self) -> None:
        """Delete the selected section."""
        index = self.sections_table.currentRow()
        if index < 0:
            self.show_warning("Warning", "No section selected")
            return
        
        name = self.sections_table.item(index, 0).text()
        if self.confirm("Confirm Delete", f"Delete section '{name}'?"):
            result = self.section_service.delete_section(name)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.show_success(f"Section '{name}' deleted")
            else:
                self.show_error("Error", str(result.error))
    
    def _rename_section(self) -> None:
        """Rename the selected section."""
        index = self.sections_table.currentRow()
        if index < 0:
            self.show_warning("Warning", "No section selected")
            return
        
        old_name = self.sections_table.item(index, 0).text()
        dialog = RenameSectionDialog(old_name, self)
        if dialog.exec() == dialog.Accepted:
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
        
        source_name = self.sections_table.item(index, 0).text()
        dialog = CloneSectionDialog(source_name, self)
        if dialog.exec() == dialog.Accepted:
            clone_name = dialog.get_clone_name()
            result = self.section_service.clone_section(source_name, clone_name)
            if result.is_success():
                self.refresh()
                self.section_changed.emit()
                self.show_success(f"Section cloned to '{clone_name}'")
            else:
                self.show_error("Error", str(result.error))
    
    def _merge_sections(self) -> None:
        """Merge sections."""
        sections = self.section_service.get_section_names()
        if len(sections) < 2:
            self.show_warning("Warning", "Need at least 2 sections to merge")
            return
        
        dialog = MergeSectionsDialog(sections, self)
        if dialog.exec() == dialog.Accepted:
            target = dialog.get_target()
            # Note: In a real implementation, we'd select source sections from a list
            # For now, we'll show a reminder
            self.show_warning("Info", "Select source sections from dialog to merge into " + target)
