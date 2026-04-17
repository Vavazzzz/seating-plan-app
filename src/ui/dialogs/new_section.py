"""Dialog for creating a new section."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QCheckBox, QDialogButtonBox, QMessageBox
)


class NewSectionDialog(QDialog):
    """Dialog for creating a new section."""
    
    def __init__(self, parent=None, existing_sections=None):
        """Initialize new section dialog.
        
        Args:
            parent: Parent widget
            existing_sections: Set or list of existing section names for validation
        """
        super().__init__(parent)
        self.setWindowTitle("New Section")
        self.existing_sections = set(existing_sections or [])
        
        # Section name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Section name")
        
        # GA checkbox
        self.is_ga_cb = QCheckBox("Is General Admission (GA)?")
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.is_ga_cb)
        layout.addWidget(buttons)
        
        self.setMinimumWidth(300)
    
    def get_values(self):
        """Get dialog values.
        
        Returns:
            Tuple of (name, is_ga) or (None, None) if cancelled
        """
        if self.exec() != QDialog.DialogCode.Accepted:
            return None, None
        
        name = self.name_edit.text().strip()
        
        # Validate
        if not name:
            QMessageBox.warning(self.parent(), "Invalid", "Section name cannot be empty.")
            return self.get_values()  # Re-show dialog
        
        if name in self.existing_sections:
            QMessageBox.warning(self.parent(), "Exists", "Section with that name already exists.")
            return self.get_values()  # Re-show dialog
        
        is_ga = self.is_ga_cb.isChecked()
        return name, is_ga
