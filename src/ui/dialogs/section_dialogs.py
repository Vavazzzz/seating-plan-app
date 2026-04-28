"""Dialogs for section management operations."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QCheckBox, QDialogButtonBox, QComboBox
)
from .base import InputDialog, CheckboxDialog


class AddSectionDialog(CheckboxDialog):
    """Dialog to add a new section."""
    
    def __init__(self, parent=None):
        super().__init__(
            "Add Section",
            "Section name:",
            "General Admission",
            parent
        )


class RenameSectionDialog(InputDialog):
    """Dialog to rename a section."""
    
    def __init__(self, current_name: str, parent=None):
        super().__init__(
            "Rename Section",
            "New name:",
            parent,
            current_name
        )


class MergeSectionsDialog(QDialog):
    """Dialog to merge sections."""
    
    def __init__(self, available_sections: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Sections")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Source sections selection
        layout.addWidget(QLabel("Merge from (select one or more):"))
        # Note: In a real implementation, this would be a list widget allowing multi-select
        # For now, we'll simplify with spinboxes for demonstration
        
        layout.addWidget(QLabel("Merge into:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(available_sections)
        layout.addWidget(self.target_combo)
        
        layout.addWidget(QLabel(""))  # Spacer
        
        self.delete_sources = QCheckBox("Delete source sections after merge")
        self.delete_sources.setChecked(True)
        layout.addWidget(self.delete_sources)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_target(self) -> str:
        """Get target section name."""
        return self.target_combo.currentText()
    
    def delete_sources_checked(self) -> bool:
        """Check if delete sources is enabled."""
        return self.delete_sources.isChecked()


class CloneSectionManyDialog(QDialog):
    """Dialog to clone a section multiple times with auto-generated names."""

    def __init__(self, source_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clone Section Multiple Times")
        self.setModal(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Source section: {source_name}"))
        layout.addWidget(QLabel("Number of clones:"))

        self.count_spinbox = QSpinBox()
        self.count_spinbox.setMinimum(1)
        self.count_spinbox.setMaximum(99)
        self.count_spinbox.setValue(1)
        layout.addWidget(self.count_spinbox)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.count_spinbox.setFocus()

    def get_count(self) -> int:
        return self.count_spinbox.value()


class CloneSectionDialog(QDialog):
    """Dialog to clone a section."""
    
    def __init__(self, source_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clone Section")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Cloning from: {source_name}"))
        layout.addWidget(QLabel("Clone name:"))
        
        self.name_field = QLineEdit()
        self.name_field.setText(f"{source_name}_copy")
        layout.addWidget(self.name_field)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.name_field.setFocus()
    
    def get_clone_name(self) -> str:
        """Get the clone name."""
        return self.name_field.text().strip()
