# src/ui/section_view.py
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox,
    QGraphicsSimpleTextItem, QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QPainter, QFont
from ..models.section import Section

SEAT_WIDTH = 30
SEAT_HEIGHT = 20
SEAT_GAP_X = 6
SEAT_GAP_Y = 8
ROW_LABEL_MARGIN = 10
ROW_LABEL_OFFSET = 8


# ---------- RANGE INPUT DIALOG ----------
class RangeInputDialog(QDialog):
    """Generic dialog for creating seat or row ranges."""
    _last_values = {
        "row": "", "start_row": "", "end_row": "",
        "start_seat": 1, "end_seat": 10
    }

    def __init__(self, mode: str, parent=None):
        """
        mode = "seat" or "row"
        """
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Add Seat Range" if mode == "seat" else "Add Row Range")
        self.setModal(True)

        form = QFormLayout()

        if mode == "seat":
            self.row_edit = QLineEdit(RangeInputDialog._last_values["row"])
            self.start_seat = QSpinBox()
            self.start_seat.setMaximum(9999)
            self.start_seat.setValue(RangeInputDialog._last_values["start_seat"])
            self.end_seat = QSpinBox()
            self.end_seat.setMaximum(9999)
            self.end_seat.setValue(RangeInputDialog._last_values["end_seat"])
            form.addRow("Row name:", self.row_edit)
            form.addRow("Start seat:", self.start_seat)
            form.addRow("End seat:", self.end_seat)

        else:  # mode == "row"
            self.start_row = QLineEdit(RangeInputDialog._last_values["start_row"])
            self.end_row = QLineEdit(RangeInputDialog._last_values["end_row"])
            self.start_seat = QSpinBox()
            self.start_seat.setMaximum(9999)
            self.start_seat.setValue(RangeInputDialog._last_values["start_seat"])
            self.end_seat = QSpinBox()
            self.end_seat.setMaximum(9999)
            self.end_seat.setValue(RangeInputDialog._last_values["end_seat"])
            form.addRow("Start row:", self.start_row)
            form.addRow("End row:", self.end_row)
            form.addRow("Start seat:", self.start_seat)
            form.addRow("End seat:", self.end_seat)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form.addRow(buttons)
        self.setLayout(form)

    def get_data(self):
        """Return validated user input or None."""
        if self.mode == "seat":
            row = self.row_edit.text().strip()
            if not row:
                QMessageBox.warning(self, "Missing data", "Row name cannot be empty.")
                return None
            start, end = self.start_seat.value(), self.end_seat.value()
            if end < start:
                start, end = end, start
            # remember values
            RangeInputDialog._last_values.update(row=row, start_seat=start, end_seat=end)
            return {"row": row, "start_seat": start, "end_seat": end}

        else:  # row mode
            start_row = self.start_row.text().strip()
            end_row = self.end_row.text().strip()
            if not start_row or not end_row:
                QMessageBox.warning(self, "Missing data", "Start and end row cannot be empty.")
                return None
            start_seat, end_seat = self.start_seat.value(), self.end_seat.value()
            if end_seat < start_seat:
                start_seat, end_seat = end_seat, start_seat
            RangeInputDialog._last_values.update(
                start_row=start_row, end_row=end_row, start_seat=start_seat, end_seat=end_seat
            )
            return {
                "start_row": start_row, "end_row": end_row,
                "start_seat": start_seat, "end_seat": end_seat
            }


# ---------- SEAT ITEM ----------
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
        self.center_text()
        self.update_visual()

    def center_text(self):
        b = self.rect()
        tw = self.text.boundingRect().width()
        th = self.text.boundingRect().height()
        self.text.setPos((b.width() - tw) / 2, (b.height() - th) / 2)

    def update_visual(self):
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.setPen(pen)
        if self.isSelected():
            brush = QBrush(Qt.GlobalColor.green)
        else:
            brush = QBrush(Qt.GlobalColor.lightGray)
        self.setBrush(brush)
        self.text.setText(f"{self.seat_number}")
        self.center_text()

    def hoverEnterEvent(self, event):
        self.setToolTip(f"Row {self.row} Seat {self.seat_number}")
        super().hoverEnterEvent(event)


# ---------- SECTION VIEW ----------
class SectionView(QWidget):
    selectionChanged = pyqtSignal(int)  # emits count of selected seats
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

        self.add_range_btn.clicked.connect(lambda: self.add_range_dialog("seat"))
        self.add_rows_range_btn.clicked.connect(lambda: self.add_range_dialog("row"))
        self.delete_btn.clicked.connect(self.delete_selected)
        self.renumber_btn.clicked.connect(self.renumber_selected_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.scene.selectionChanged.connect(self.on_selection_changed)

    # ---- Load & display section ----
    def load_section(self, section: Section):
        self.section = section
        self.scene.clear()
        if not section:
            return

        rows = {}
        for seat in section.seats.values():
            rows.setdefault(seat.row_number, []).append(seat)

        def row_key(r):
            try:
                return int(r)
            except:
                return r

        sorted_rows = sorted(rows.keys(), key=row_key)

        y = 0
        for row in sorted_rows:
            try:
                seats_sorted = sorted(rows[row], key=lambda s: int(s.seat_number))
            except:
                seats_sorted = sorted(rows[row], key=lambda s: s.seat_number)
            x = 0
            for seat in seats_sorted:
                item = SeatItem(row, seat.seat_number, x, y)
                self.scene.addItem(item)
                x += SEAT_WIDTH + SEAT_GAP_X
            # row label
            label = QGraphicsSimpleTextItem(f"{row}")
            font = QFont()
            font.setPointSize(9)
            label.setFont(font)
            label.setPos(-ROW_LABEL_MARGIN - SEAT_WIDTH, y + (SEAT_HEIGHT - label.boundingRect().height()) / 2 + ROW_LABEL_OFFSET)
            self.scene.addItem(label)
            y += SEAT_HEIGHT + SEAT_GAP_Y

        bounding = self.scene.itemsBoundingRect()
        bounding.setLeft(bounding.left() - 40)
        self.scene.setSceneRect(bounding)
        self.update_all_seat_visuals()

    # ---- Add seat/row range unified ----
    def add_range_dialog(self, mode: str):
        if not self.section:
            QMessageBox.warning(self, "No section", "Please select/create a section first.")
            return

        dlg = RangeInputDialog(mode, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_data()
        if not data:
            return

        if mode == "seat":
            self.section.add_seat_range(data["row"], data["start_seat"], data["end_seat"])
        else:
            rows_to_add = self._generate_rows(data["start_row"], data["end_row"])
            if not rows_to_add:
                QMessageBox.warning(self, "Invalid rows", "Rows must both be numeric or single letters.")
                return
            for r in rows_to_add:
                self.section.add_seat_range(r, data["start_seat"], data["end_seat"])
        self.load_section(self.section)

    def _generate_rows(self, start_row, end_row):
        """Generate inclusive row list for numeric or letter ranges."""
        if start_row.isdigit() and end_row.isdigit():
            s, e = int(start_row), int(end_row)
            if s > e:
                s, e = e, s
            return [str(i) for i in range(s, e + 1)]
        elif len(start_row) == 1 and len(end_row) == 1 and start_row.isalpha() and end_row.isalpha():
            s_ord, e_ord = ord(start_row.upper()), ord(end_row.upper())
            if s_ord > e_ord:
                s_ord, e_ord = e_ord, s_ord
            return [chr(i) for i in range(s_ord, e_ord + 1)]
        elif start_row == end_row:
            return [start_row]
        return None

    # ---- Seat editing actions ----
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

        choice, ok = QInputDialog.getItem(self, "Renumber", "Operation:",
                                          ["Set new row", "Set starting seat numbers (increment)"], 0, False)
        if not ok:
            return

        if choice == "Set new row":
            new_row, ok = QInputDialog.getText(self, "New row", "New row name:")
            if not ok or not new_row:
                return
            old_rows = set(it.row for it in selected)
            if len(old_rows) == 1:
                self.section.change_row_number(next(iter(old_rows)), new_row)
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

    # ---- Visual refresh ----
    def on_selection_changed(self):
        self.update_all_seat_visuals()

    def update_all_seat_visuals(self):
        for it in self.scene.items():
            if isinstance(it, SeatItem):
                it.update_visual()

    def on_selection_changed(self):
            selected = [it for it in self.scene.selectedItems() if isinstance(it, SeatItem)]
            self.selectionChanged.emit(len(selected))  # notify main window
            self.update_all_seat_visuals()