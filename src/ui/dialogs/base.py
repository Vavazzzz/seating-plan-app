"""Base dialog classes for UI operations."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QDialogButtonBox
from PyQt6.QtCore import Qt


class InputDialog(QDialog):
    """Generic input dialog with validation."""
    
    def __init__(self, title: str, label: str, parent=None, default_value: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        
        self.input_field = QLineEdit()
        self.input_field.setText(default_value)
        layout.addWidget(self.input_field)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.input_field.setFocus()
    
    def get_value(self) -> str:
        """Get the input value."""
        return self.input_field.text().strip()


class CheckboxDialog(QDialog):
    """Dialog with input field and checkbox."""
    
    def __init__(self, title: str, label: str, checkbox_label: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)
        
        self.checkbox = QCheckBox(checkbox_label)
        layout.addWidget(self.checkbox)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.input_field.setFocus()
    
    def get_value(self) -> str:
        """Get the input value."""
        return self.input_field.text().strip()
    
    def is_checked(self) -> bool:
        """Get checkbox state."""
        return self.checkbox.isChecked()
