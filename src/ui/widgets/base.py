"""Base widget class with common functionality."""

from PyQt6.QtWidgets import QWidget, QMessageBox
from typing import Optional, Callable


class BasePanel(QWidget):
    """Base class for UI panels with common error handling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._error_callback: Optional[Callable[[str], None]] = None
        self._success_callback: Optional[Callable[[str], None]] = None
    
    def set_error_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for error messages."""
        self._error_callback = callback
    
    def set_success_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for success messages."""
        self._success_callback = callback
    
    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        if self._error_callback:
            self._error_callback(f"{title}: {message}")
        else:
            QMessageBox.critical(self, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog."""
        QMessageBox.warning(self, title, message)
    
    def show_success(self, message: str) -> None:
        """Show success message."""
        if self._success_callback:
            self._success_callback(message)
        else:
            QMessageBox.information(self, "Success", message)
    
    def confirm(self, title: str, message: str) -> bool:
        """Show confirmation dialog."""
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
