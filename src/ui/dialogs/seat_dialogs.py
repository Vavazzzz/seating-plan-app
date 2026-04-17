"""Dialogs for seat management and file operations."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QFileDialog
from PyQt6.QtCore import Qt
from .base import InputDialog


class AddSeatDialog(InputDialog):
    """Dialog to add a seat with row and seat number."""
    
    def __init__(self, parent=None):
        super().__init__(
            "Add Seat",
            "Row and seat (e.g., 'A 5'):",
            parent
        )
    
    def get_row_and_seat(self) -> tuple:
        """Parse and return (row, seat) tuple."""
        parts = self.get_value().split()
        if len(parts) >= 2:
            return (parts[0], parts[1])
        return None


class AddSeatRangeDialog(QDialog):
    """Dialog to add a range of seats."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Seat Range")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Row:"))
        self.row_field = QLineEdit()
        layout.addWidget(self.row_field)
        
        layout.addWidget(QLabel("Start seat:"))
        self.start_field = QLineEdit()
        layout.addWidget(self.start_field)
        
        layout.addWidget(QLabel("End seat (e.g., '5' or 'Z'):"))
        self.end_field = QLineEdit()
        layout.addWidget(self.end_field)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.row_field.setFocus()
    
    def get_values(self) -> tuple:
        """Return (row, start_seat, end_seat) tuple."""
        return (
            self.row_field.text().strip(),
            self.start_field.text().strip(),
            self.end_field.text().strip()
        )


class FileDialog:
    """Static file dialog helper methods."""
    
    @staticmethod
    def get_save_path(parent, caption="Save File", file_filter="JSON Files (*.json)"):
        """Get a file save path."""
        path, _ = QFileDialog.getSaveFileName(
            parent,
            caption,
            "",
            file_filter
        )
        return path if path else None
    
    @staticmethod
    def get_open_path(parent, caption="Open File", file_filter="All Files (*)"):
        """Get a file open path."""
        path, _ = QFileDialog.getOpenFileName(
            parent,
            caption,
            "",
            file_filter
        )
        return path if path else None
