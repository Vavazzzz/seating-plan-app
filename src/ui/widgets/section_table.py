"""Section table widget for managing sections."""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor


class DragDropSectionTable(QTableWidget):
    """Custom table widget with drag & drop for section reordering."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.drag_source_row = None
    
    def mousePressEvent(self, event):
        """Track drag source row."""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                col = self.column(item)
                if col != 0:  # Not checkbox column
                    self.drag_source_row = self.row(item)
        super().mousePressEvent(event)
    
    def dropEvent(self, event):
        """Handle drop to reorder sections."""
        if event.source() is not self:
            event.ignore()
            return
        
        drop_pos = event.position().toPoint()
        drop_index = self.indexAt(drop_pos).row()
        
        if drop_index < 0:
            event.ignore()
            return
        
        if self.drag_source_row is None or self.drag_source_row == drop_index:
            event.ignore()
            return
        
        # Reorder rows by swapping
        for col in range(self.columnCount()):
            source_item = self.takeItem(self.drag_source_row, col)
            target_item = self.takeItem(drop_index, col)
            self.setItem(self.drag_source_row, col, target_item)
            self.setItem(drop_index, col, source_item)
        
        event.accept()
        self.drag_source_row = None


class SectionTableWidget(QWidget):
    """Widget encapsulating section table management."""
    
    section_selected = pyqtSignal(str)  # Emitted when a section is selected
    sections_checked = pyqtSignal(list)  # Emitted when checks change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = DragDropSectionTable()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup table UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
    
    def load_sections(self, sections):
        """Load sections into the table.
        
        Args:
            sections: Dict of {name: Section} objects
        """
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", "Section", "Seats"])
        
        for idx, (name, section) in enumerate(sections.items()):
            self.table.insertRow(idx)
            
            # Checkbox cell
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(idx, 0, checkbox_item)
            
            # Name cell
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 1, name_item)
            
            # Seat count cell
            seat_count = len(section.seats)
            count_item = QTableWidgetItem(str(seat_count))
            count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 2, count_item)
        
        # Resize columns
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
    
    def get_checked_sections(self):
        """Get list of checked section names.
        
        Returns:
            List of section names
        """
        checked = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                name = self.table.item(row, 1).text()
                checked.append(name)
        return checked
    
    def get_sections_order(self):
        """Get sections in current table order.
        
        Returns:
            List of section names in current order
        """
        sections = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 1).text()
            sections.append(name)
        return sections
    
    def get_selected_section(self):
        """Get currently selected section.
        
        Returns:
            Section name or None
        """
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 1).text()
    
    def clear(self):
        """Clear the table."""
        self.table.setRowCount(0)
