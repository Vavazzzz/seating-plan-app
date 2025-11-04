# src/ui/section_view.py
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider, QLabel, QFrame, QInputDialog,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QSpinBox
)
from PyQt6.QtGui import QBrush, QPen, QPainter, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from ..models.section import Section
from string import ascii_uppercase


class RangeInputDialog(QDialog):
    """Reusable input dialog for seat and row range creation."""
    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode  # 'seat' or 'row'
        self.setWindowTitle("Add " + ("Row Range" if mode == "row" else "Seat Range"))
        self.setMinimumWidth(300)

        layout = QFormLayout(self)

        # Fields common to both modes
        self.row_field = QLineEdit()
        self.start_row_field = QLineEdit()
        self.end_row_field = QLineEdit()
        self.start_seat_spin = QSpinBox()
        self.end_seat_spin = QSpinBox()
        self.start_seat_spin.setRange(1, 10000)
        self.end_seat_spin.setRange(1, 10000)

        if mode == "seat":
            layout.addRow("Row name:", self.row_field)
        else:
            layout.addRow("Start row:", self.start_row_field)
            layout.addRow("End row:", self.end_row_field)

        layout.addRow("Start seat:", self.start_seat_spin)
        layout.addRow("End seat:", self.end_seat_spin)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_values(self):
        if self.mode == "seat":
            return {
                "row": self.row_field.text().strip(),
                "start_seat": self.start_seat_spin.value(),
                "end_seat": self.end_seat_spin.value(),
            }
        else:
            return {
                "start_row": self.start_row_field.text().strip(),
                "end_row": self.end_row_field.text().strip(),
                "start_seat": self.start_seat_spin.value(),
                "end_seat": self.end_seat_spin.value(),
            }


class SeatItemRect:
    WIDTH = 20
    HEIGHT = 20


class SeatItem(QGraphicsRectItem):
    def __init__(self, row, seat):
        super().__init__(0, 0, SeatItemRect.WIDTH, SeatItemRect.HEIGHT)
        self.row = row
        self.seat = seat
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setBrush(QBrush(Qt.GlobalColor.lightGray))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.text_item = QGraphicsSimpleTextItem(str(seat), self)
        self.text_item.setPos(SeatItemRect.WIDTH / 4, SeatItemRect.HEIGHT / 6)

    def update_visual(self):
        self.setBrush(QBrush(Qt.GlobalColor.green if self.isSelected() else Qt.GlobalColor.lightGray))


class SectionView(QWidget):
    selectionChanged = pyqtSignal(int)
    aboutToModify = pyqtSignal()   # emitted before mutating operations to allow snapshots
    sectionModified = pyqtSignal()  # emitted after mutation to refresh UI

    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)

        # ---- Top control buttons ----
        self.btn_add_seat_range = QPushButton("➕ Add Seat Range")
        self.btn_add_seat_range.setToolTip("Add seat range (opens a single dialog).")
        self.btn_add_row_range = QPushButton("➕ Add Row Range")
        self.btn_add_row_range.setToolTip("Add multiple rows with seat ranges.")
        self.btn_delete_seat = QPushButton("🗑 Delete Seats")
        self.btn_delete_seat.setToolTip("Delete selected seats (Del).")
        self.btn_delete_row = QPushButton("🗑 Delete Rows")
        self.btn_delete_row.setToolTip("Delete selected rows (by selecting seats in those rows).")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_add_seat_range)
        controls_layout.addWidget(self.btn_add_row_range)
        controls_layout.addWidget(self.btn_delete_seat)
        controls_layout.addWidget(self.btn_delete_row)
        controls_layout.addStretch()

        # ---- Main layout ----
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls_layout)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # ---- Floating Zoom Overlay ----
        self.zoom_overlay = QFrame(self.view)
        self.zoom_overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 8px;
            }
            QLabel { color: white; font-size: 12px; }
            QSlider::groove:horizontal { height: 4px; background: #555; }
            QSlider::handle:horizontal { background: #ddd; border-radius: 4px; width: 10px; }
        """)
        self.zoom_overlay.setFixedHeight(36)
        self.zoom_overlay.setFixedWidth(180)

        self.zoom_label = QLabel("100%", self.zoom_overlay)
        self.zoom_label.move(10, 10)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal, self.zoom_overlay)
        self.zoom_slider.setGeometry(60, 10, 100, 16)
        self.zoom_slider.setRange(25, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setSingleStep(5)
        self.zoom_overlay.show()

        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        self.scene.selectionChanged.connect(self.on_selection_changed)

        # connect buttons
        self.btn_add_seat_range.clicked.connect(self.add_seat_range_dialog)
        self.btn_add_row_range.clicked.connect(self.add_row_range_dialog)
        self.btn_delete_seat.clicked.connect(self.delete_selected_seats)
        self.btn_delete_row.clicked.connect(self.delete_selected_rows)

        # keyboard shortcuts local to section view
        self._install_shortcuts()

        self.view.viewport().installEventFilter(self)
        self._updating_slider = False

    # ---------- Shortcuts ----------
    def _install_shortcuts(self):
        # Select All
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self.select_all_seats).setContext(Qt.ShortcutContext.WidgetShortcut)
        # Delete selected
        QShortcut(QKeySequence("Delete"), self, activated=self.delete_selected_seats).setContext(Qt.ShortcutContext.WidgetShortcut)
        # Reset zoom
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.reset_zoom).setContext(Qt.ShortcutContext.WidgetShortcut)
        # Zoom in/out (Ctrl + '=' / Ctrl + '-')
        QShortcut(QKeySequence("Ctrl+="), self, activated=self.zoom_in).setContext(Qt.ShortcutContext.WidgetShortcut)
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out).setContext(Qt.ShortcutContext.WidgetShortcut)

    # ---------- Overlay positioning ----------
    def eventFilter(self, obj, event):
        if obj == self.view.viewport() and event.type() == QEvent.Type.Resize:
            self.position_zoom_overlay()
        return super().eventFilter(obj, event)

    def position_zoom_overlay(self):
        margin = 10
        vw, vh = self.view.viewport().width(), self.view.viewport().height()
        self.zoom_overlay.move(vw - self.zoom_overlay.width() - margin,
                               vh - self.zoom_overlay.height() - margin)

    # ---------- Section Rendering ----------
    def load_section(self, section: Section | None):
        self.section = section
        self.scene.clear()
        if not section:
            return

        # Group seats by row
        seats_by_row = {}
        for seat in section.seats.values():
            seats_by_row.setdefault(seat.row_number, []).append(seat)

        # Determine all seat numbers used across the section
        all_seat_numbers = sorted(
            {s.seat_number for s in section.seats.values()},
            key=lambda n: int(n) if str(n).isdigit() else str(n)
        )

        def _row_sort_key(value: str):
            try:
                return int(value)
            except ValueError:
                return value

        sorted_rows = sorted(seats_by_row.keys(), key=_row_sort_key)

        # Layout constants
        x_spacing = SeatItemRect.WIDTH + 5
        y_spacing = SeatItemRect.HEIGHT + 10

        y = 0
        for row in sorted_rows:
            seats = {s.seat_number: s for s in seats_by_row[row]}
            row_label = self.scene.addSimpleText(str(row))
            row_label.setPos(-40, y)
            for idx, seat_num in enumerate(all_seat_numbers):
                if seat_num in seats:
                    seat = seats[seat_num]
                    x = idx * x_spacing
                    item = SeatItem(row, seat.seat_number)
                    item.setPos(x, y)
                    self.scene.addItem(item)
            y += y_spacing

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.position_zoom_overlay()


    # ---------- Seat Manipulation ----------
    def add_seat_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog("seat", self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        if not data["row"]:
            return
        # notify about to modify (so undo snapshot can be taken)
        self.aboutToModify.emit()
        self.section.add_seat_range(data["row"], data["start_seat"], data["end_seat"])
        self.load_section(self.section)
        self.sectionModified.emit()

    def add_row_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog("row", self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        if not data["start_row"] or not data["end_row"]:
            return

        try:
            # numeric range
            rows = [str(i) for i in range(int(data["start_row"]), int(data["end_row"]) + 1)]
        except ValueError:
            # letter range
            rows = ascii_uppercase[
                ascii_uppercase.index(data["start_row"].upper()):
                ascii_uppercase.index(data["end_row"].upper()) + 1
            ]

        # notify before bulk modification
        self.aboutToModify.emit()
        for r in rows:
            self.section.add_seat_range(r, data["start_seat"], data["end_seat"])

        self.load_section(self.section)
        self.sectionModified.emit()

    def delete_selected_seats(self):
        if not self.section:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected:
            return
        # push snapshot
        self.aboutToModify.emit()
        for item in selected:
            self.section.delete_seat(item.row, str(item.seat))
        self.load_section(self.section)
        self.sectionModified.emit()

    def delete_selected_rows(self):
        if not self.section:
            return
        rows = {item.row for item in self.scene.selectedItems() if isinstance(item, SeatItem)}
        if not rows:
            return
        # push snapshot
        self.aboutToModify.emit()
        for r in rows:
            self.section.delete_row(r)
        self.load_section(self.section)
        self.sectionModified.emit()

    # ---------- Selection ----------
    def on_selection_changed(self):
        selected = [it for it in self.scene.selectedItems() if isinstance(it, SeatItem)]
        for it in self.scene.items():
            if isinstance(it, SeatItem):
                it.update_visual()
        self.selectionChanged.emit(len(selected))

    def select_all_seats(self):
        for it in self.scene.items():
            if isinstance(it, SeatItem):
                it.setSelected(True)
        self.on_selection_changed()

    # ---------- Zoom helpers ----------
    def reset_zoom(self):
        self.view.set_zoom(1.0)
        self.zoom_slider.setValue(100)
        self.zoom_label.setText("100%")

    def zoom_in(self):
        v = min(400, self.zoom_slider.value() + 10)
        self.zoom_slider.setValue(v)

    def zoom_out(self):
        v = max(25, self.zoom_slider.value() - 10)
        self.zoom_slider.setValue(v)

    # ---------- Zoom ----------
    def on_zoom_slider_changed(self, value):
        if self._updating_slider:
            return
        scale_factor = value / 100.0
        self.view.set_zoom(scale_factor)
        self.zoom_label.setText(f"{value}%")

    def set_zoom_from_view(self, value):
        self._updating_slider = True
        self.zoom_slider.setValue(int(value * 100))
        self.zoom_label.setText(f"{int(value * 100)}%")
        self._updating_slider = False


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, section_view):
        super().__init__(scene)
        self.setRenderHints(self.renderHints() | QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self._zoom = 1.0
        self.section_view = section_view

    def set_zoom(self, factor: float):
        self.resetTransform()
        self.scale(factor, factor)
        self._zoom = factor
        self.section_view.set_zoom_from_view(factor)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 1 / 1.15
            new_zoom = max(0.25, min(4.0, self._zoom * factor))
            self.set_zoom(new_zoom)
        else:
            super().wheelEvent(event)
