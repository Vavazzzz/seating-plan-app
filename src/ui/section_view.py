# src/ui/section_view.py
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPen, QBrush
from ..models.section import Section

SEAT_WIDTH = 30
SEAT_HEIGHT = 20
SEAT_GAP_X = 6
SEAT_GAP_Y = 8

class SeatItem(QGraphicsRectItem):
    def __init__(self, row: str, seat_number: str, x: float, y: float, w=SEAT_WIDTH, h=SEAT_HEIGHT):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.row = row
        self.seat_number = seat_number
        self.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.update_visual()

    def update_visual(self):
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.setPen(pen)
        if self.isSelected():
            brush = QBrush(Qt.GlobalColor.cyan)
        else:
            brush = QBrush(Qt.GlobalColor.lightGray)
        self.setBrush(brush)

    def hoverEnterEvent(self, event):
        # show tooltip
        self.setToolTip(f"Row {self.row} Seat {self.seat_number}")
        super().hoverEnterEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # selection visual update happens in main loop; but ensure visual update
        self.update_visual()

class SectionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | Qt.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # simple controls
        btn_layout = QHBoxLayout()
        self.add_range_btn = QPushButton("Add seat range")
        self.delete_btn = QPushButton("Delete selected")
        self.renumber_btn = QPushButton("Renumber selection")
        btn_layout.addWidget(self.add_range_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.renumber_btn)

        self.add_range_btn.clicked.connect(self.add_seat_range_dialog)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.renumber_btn.clicked.connect(self.renumber_selected_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_section(self, section: Section):
        self.section = section
        self.scene.clear()
        if not section:
            return
        # lay out seats grouped by row (rows are strings; we sort them)
        rows = {}
        for key, seat in section.seats.items():
            rows.setdefault(seat.row_number, []).append(seat)

        # sort rows by natural order if numeric else lexicographic
        def row_key(r):
            try:
                return int(r)
            except:
                return r

        sorted_rows = sorted(rows.keys(), key=row_key)

        y = 0
        for row in sorted_rows:
            seats = rows[row]
            # try numeric sort of seat numbers
            try:
                seats_sorted = sorted(seats, key=lambda s: int(s.seat_number))
            except:
                seats_sorted = sorted(seats, key=lambda s: s.seat_number)
            x = 0
            for seat in seats_sorted:
                item = SeatItem(row, seat.seat_number, x, y)
                self.scene.addItem(item)
                x += SEAT_WIDTH + SEAT_GAP_X
            y += SEAT_HEIGHT + SEAT_GAP_Y

        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def add_seat_range_dialog(self):
        if not self.section:
            QMessageBox.warning(self, "No section", "Please select/create a section first.")
            return

        row, ok = QInputDialog.getText(self, "Row name", "Row name (e.g., A or 1):")
        if not ok or not row:
            return
        start, ok = QInputDialog.getInt(self, "Start seat", "Start seat number:", 1, 0)
        if not ok:
            return
        end, ok = QInputDialog.getInt(self, "End seat", "End seat number:", start, 0)
        if not ok:
            return
        self.section.add_seat_range(str(row), start, end)
        self.load_section(self.section)

    def delete_selected(self):
        if not self.section:
            return
        selected = [it for it in self.scene.selectedItems() if isinstance(it, SeatItem)]
        if not selected:
            QMessageBox.information(self, "No selection", "No seats selected.")
            return
        for it in selected:
            self.section.delete_seat(it.row, it.seat_number)
        self.load_section(self.section)

    def renumber_selected_dialog(self):
        if not self.section:
            return
        selected = [it for it in self.scene.selectedItems() if isinstance(it, SeatItem)]
        if not selected:
            QMessageBox.information(self, "No selection", "No seats selected.")
            return

        # Ask for renumber pattern: either increment starting number or set new row number
        choice, ok = QInputDialog.getItem(self, "Renumber", "Operation:", ["Set new row", "Set starting seat numbers (increment)"], 0, False)
        if not ok:
            return
        if choice == "Set new row":
            new_row, ok = QInputDialog.getText(self, "New row", "New row name:")
            if not ok or not new_row:
                return
            # We change row for each selected seat keeping seat numbers
            # Use change_row_number to rename an entire row if all seats belong to same old_row
            old_rows = set(it.row for it in selected)
            if len(old_rows) == 1:
                old_row = next(iter(old_rows))
                self.section.change_row_number(old_row, new_row)
            else:
                # change seats individually
                for it in selected:
                    # create new seat with same seat number in new_row
                    self.section.add_seat(new_row, it.seat_number)
                    self.section.delete_seat(it.row, it.seat_number)
            self.load_section(self.section)
            return

        # increment starting seat numbers
        start_num, ok = QInputDialog.getInt(self, "Start number", "Starting seat number:", 1, 0)
        if not ok:
            return
        # sort selected items by x position so numbering flows left-to-right
        selected_sorted = sorted(selected, key=lambda it: it.scenePos().x())
        current = start_num
        for it in selected_sorted:
            # rename seat: change seat number within the same row
            self.section.change_seat_number(it.row, it.seat_number, str(current))
            current += 1
        self.load_section(self.section)
