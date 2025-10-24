# src/ui/section_view.py
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox,
    QGraphicsSimpleTextItem
)
from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QPainter, QFont
from ..models.section import Section

SEAT_WIDTH = 30
SEAT_HEIGHT = 20
SEAT_GAP_X = 6
SEAT_GAP_Y = 8
ROW_LABEL_MARGIN = 10
ROW_LABEL_OFFSET = 8

class SeatItem(QGraphicsRectItem):
    def __init__(self, row: str, seat_number: str, x: float, y: float, w=SEAT_WIDTH, h=SEAT_HEIGHT):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.row = row
        self.seat_number = seat_number
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)

        # text label inside the seat
        self.text = QGraphicsSimpleTextItem(f"{self.seat_number}", parent=self)
        font = QFont()
        font.setPointSize(8)
        self.text.setFont(font)
        # center text
        b = self.rect()
        tw = self.text.boundingRect().width()
        th = self.text.boundingRect().height()
        self.text.setPos((b.width() - tw) / 2, (b.height() - th) / 2)

        self.update_visual()

    def update_visual(self):
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.setPen(pen)
        if self.isSelected():
            brush = QBrush(Qt.GlobalColor.green)
        else:
            brush = QBrush(Qt.GlobalColor.lightGray)
        self.setBrush(brush)
        # update text if seat_number changed externally
        self.text.setText(f"{self.seat_number}")
        # re-center text
        b = self.rect()
        tw = self.text.boundingRect().width()
        th = self.text.boundingRect().height()
        self.text.setPos((b.width() - tw) / 2, (b.height() - th) / 2)

    def hoverEnterEvent(self, event):
        self.setToolTip(f"Row {self.row} Seat {self.seat_number}")
        super().hoverEnterEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # visual update occurs later via selectionChanged handler, but ensure immediate update for single click
        self.update_visual()

class SectionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # controls
        btn_layout = QHBoxLayout()
        self.add_range_btn = QPushButton("Add seat range")
        self.add_rows_range_btn = QPushButton("Add row range")
        self.delete_btn = QPushButton("Delete selected")
        self.renumber_btn = QPushButton("Renumber selection")
        btn_layout.addWidget(self.add_range_btn)
        btn_layout.addWidget(self.add_rows_range_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.renumber_btn)

        self.add_range_btn.clicked.connect(self.add_seat_range_dialog)
        self.add_rows_range_btn.clicked.connect(self.add_rows_range_dialog)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.renumber_btn.clicked.connect(self.renumber_selected_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # ensure visual updates when selection changes
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def load_section(self, section: Section):
        self.section = section
        self.scene.clear()
        if not section:
            return

        # build rows dict
        rows = {}
        for key, seat in section.seats.items():
            rows.setdefault(seat.row_number, []).append(seat)

        # sort rows by numeric when possible else lexicographic
        def row_key(r):
            try:
                return int(r)
            except:
                return r

        sorted_rows = sorted(rows.keys(), key=row_key)

        y = 0
        max_row_width = 0
        row_label_items = []
        for row in sorted_rows:
            seats = rows[row]
            # try numeric sort for seats
            try:
                seats_sorted = sorted(seats, key=lambda s: int(s.seat_number))
            except:
                seats_sorted = sorted(seats, key=lambda s: s.seat_number)
            x = 0
            for seat in seats_sorted:
                item = SeatItem(row, seat.seat_number, x, y)
                self.scene.addItem(item)
                x += SEAT_WIDTH + SEAT_GAP_X
            max_row_width = max(max_row_width, x)
            y += SEAT_HEIGHT + SEAT_GAP_Y

        # add row labels on the left
        # compute label X position (negative offset)
        label_x = - (ROW_LABEL_MARGIN + SEAT_WIDTH)
        y = 0
        for row in sorted_rows:
            label = QGraphicsSimpleTextItem(f"{row}")
            font = QFont()
            font.setPointSize(9)
            label.setFont(font)
            # vertically center label relative to row seats
            label_rect = label.boundingRect()
            label.setPos(label_x, y + (SEAT_HEIGHT - label_rect.height()) / 2 + ROW_LABEL_OFFSET)
            self.scene.addItem(label)
            y += SEAT_HEIGHT + SEAT_GAP_Y

        # adjust scene bounds so labels are visible
        bounding = self.scene.itemsBoundingRect()
        # expand left to accommodate labels
        bounding.setLeft(label_x - 10)
        self.scene.setSceneRect(bounding)

        # ensure visuals reflect selection state
        self.update_all_seat_visuals()

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

    def add_rows_range_dialog(self):
        """Add multiple rows (numeric or single-letter ranges) each with a seat range."""
        if not self.section:
            QMessageBox.warning(self, "No section", "Please select/create a section first.")
            return

        start_row, ok = QInputDialog.getText(self, "Start row", "Start row (e.g., 1 or A):")
        if not ok or not start_row:
            return
        end_row, ok = QInputDialog.getText(self, "End row", "End row (e.g., 10 or J):")
        if not ok or not end_row:
            return

        # seat range inputs
        start_seat, ok = QInputDialog.getInt(self, "Start seat", "Start seat number:", 1, 0)
        if not ok:
            return
        end_seat, ok = QInputDialog.getInt(self, "End seat", "End seat number:", start_seat, 0)
        if not ok:
            return

        # generate row list: support numeric ranges or single-letter ranges
        rows_to_add = []
        # check numeric
        if start_row.isdigit() and end_row.isdigit():
            s = int(start_row)
            e = int(end_row)
            if s > e:
                s, e = e, s
            rows_to_add = [str(i) for i in range(s, e + 1)]
        # check single-letter alpha range (A..Z or a..z)
        elif len(start_row) == 1 and len(end_row) == 1 and start_row.isalpha() and end_row.isalpha():
            s_ord = ord(start_row.upper())
            e_ord = ord(end_row.upper())
            if s_ord > e_ord:
                s_ord, e_ord = e_ord, s_ord
            rows_to_add = [chr(i) for i in range(s_ord, e_ord + 1)]
        else:
            # fallback: if start==end treat as single row, else error
            if start_row == end_row:
                rows_to_add = [start_row]
            else:
                QMessageBox.warning(self, "Unsupported range", "Rows must both be numeric (e.g., 1→10) or single letters (e.g., A→J).")
                return

        # add seats for each row
        for r in rows_to_add:
            self.section.add_seat_range(r, start_seat, end_seat)

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

        choice, ok = QInputDialog.getItem(self, "Renumber", "Operation:", ["Set new row", "Set starting seat numbers (increment)"], 0, False)
        if not ok:
            return
        if choice == "Set new row":
            new_row, ok = QInputDialog.getText(self, "New row", "New row name:")
            if not ok or not new_row:
                return
            old_rows = set(it.row for it in selected)
            if len(old_rows) == 1:
                old_row = next(iter(old_rows))
                self.section.change_row_number(old_row, new_row)
            else:
                for it in selected:
                    self.section.add_seat(new_row, it.seat_number)
                    self.section.delete_seat(it.row, it.seat_number)
            self.load_section(self.section)
            return

        start_num, ok = QInputDialog.getInt(self, "Start number", "Starting seat number:", 1, 0)
        if not ok:
            return
        selected_sorted = sorted(selected, key=lambda it: it.scenePos().x())
        current = start_num
        for it in selected_sorted:
            self.section.change_seat_number(it.row, it.seat_number, str(current))
            current += 1
        self.load_section(self.section)

    def on_selection_changed(self):
        """Update visuals of all seats whenever selection changes (rubber-band included)."""
        self.update_all_seat_visuals()

    def update_all_seat_visuals(self):
        for it in self.scene.items():
            # items() returns items in descending Z-order; filter SeatItem instances
            if isinstance(it, SeatItem):
                it.update_visual()
