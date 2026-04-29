"""Dialogs for section management operations."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QCheckBox, QDialogButtonBox,
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
    """Dialog to merge checked sections into a new named section."""

    def __init__(self, source_names: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Sections")
        self.setModal(True)

        layout = QVBoxLayout()

        sources_text = ", ".join(source_names) if source_names else "—"
        layout.addWidget(QLabel(f"Merging: {sources_text}"))
        layout.addWidget(QLabel("New section name:"))

        self.name_field = QLineEdit()
        layout.addWidget(self.name_field)

        self.delete_sources_check = QCheckBox("Delete source sections after merge")
        self.delete_sources_check.setChecked(True)
        layout.addWidget(self.delete_sources_check)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.name_field.setFocus()

    def get_new_name(self) -> str:
        return self.name_field.text().strip()

    def delete_sources_checked(self) -> bool:
        return self.delete_sources_check.isChecked()


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
