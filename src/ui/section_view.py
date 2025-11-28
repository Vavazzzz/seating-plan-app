from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider, QLabel, QFrame,
    QMenu, QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QBrush, QPen, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from ..models.section import Section
from ..utils.alphanum_handler import alphanum_range
from .dialogs import RangeInputDialog
from string import ascii_uppercase

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
    """A QWidget for rendering and manipulating a Section in a seating plan."""
    selectionChanged = pyqtSignal(int)
    aboutToModify = pyqtSignal()   # emitted before mutating ops (for undo)
    sectionModified = pyqtSignal()  # emitted after mutation (for refresh)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)

        # Controls
        self.btn_add_seat_range = QPushButton("\u2795 Add Seat Range")
        self.btn_add_seat_range.setToolTip("Add seat range (opens a single dialog).")
        self.btn_add_row_range = QPushButton("\u2795 Add Row Range")
        self.btn_add_row_range.setToolTip("Add multiple rows with seat ranges.")
        self.btn_delete_seat = QPushButton("\U0001F5D1 Delete Seats")
        self.btn_delete_seat.setToolTip("Delete selected seats (Del).")
        self.btn_delete_row = QPushButton("\U0001F5D1 Delete Rows")
        self.btn_delete_row.setToolTip("Delete selected rows (by selecting seats in those rows).")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_add_seat_range)
        controls_layout.addWidget(self.btn_add_row_range)
        controls_layout.addWidget(self.btn_delete_seat)
        controls_layout.addWidget(self.btn_delete_row)
        controls_layout.addStretch()

        # ---- Buttons shortcuts ----
        self.btn_delete_seat.setShortcut("Del")
        self.btn_delete_row.setShortcut("Shift+Del")

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

        # Connect buttons
        self.btn_add_seat_range.clicked.connect(self.add_seat_range_dialog)
        self.btn_add_row_range.clicked.connect(self.add_row_range_dialog)
        self.btn_delete_seat.clicked.connect(self.delete_selected_seats)
        self.btn_delete_row.clicked.connect(self.delete_selected_rows)

        # Context menu for move seats
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.view.viewport().installEventFilter(self)
        self._updating_slider = False

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
        def seat_key_sort(n: str):
            try:
                return int(n)
            except Exception:
                return n

        all_seat_numbers = sorted({s.seat_number for s in section.seats.values()}, key=seat_key_sort)

        def _row_sort_key(value: str):
            try:
                return int(value)
            except ValueError:
                return value

        sorted_rows = sorted(seats_by_row.keys(), key=_row_sort_key)

        # Layout constants
        x_spacing = SeatItemRect.WIDTH + 5
        y_spacing = SeatItemRect.HEIGHT + 10

        section_label = self.scene.addText(section.name)
        section_label.setPos((len(all_seat_numbers) * x_spacing + 10) / 2, -50)

        # Render seats
        y = 0
        for row in sorted_rows:
            seats = {s.seat_number: s for s in seats_by_row[row]}
            row_label_sx = self.scene.addSimpleText(str(row))
            row_label_sx.setPos(-40, y)
            row_label_dx = self.scene.addSimpleText(str(row))
            row_label_dx.setPos(len(all_seat_numbers) * x_spacing + 10, y)

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

    # ---------- Context menu and move seats ----------
    def show_context_menu(self, pos):
        """Show context menu on right-click if seats are selected."""
        if not self.section:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected:
            return

        menu = QMenu(self)
        move_action = menu.addAction("Move selected seats to section...")
        action = menu.exec(self.mapToGlobal(pos))
        if action == move_action:
            self.move_selected_seats_dialog()

    def move_selected_seats_dialog(self):
        """
        Show dialog to move selected seats to an existing or new section.
        Uses the parent (MainWindow) seating_plan to list/create sections.
        """
        if not self.section or not self.parent() or not hasattr(self.parent(), "seating_plan"):
            return

        mainwindow = self.parent()
        current_section_name = self.section.name
        all_names = [name for name in mainwindow.seating_plan.sections.keys() if name != current_section_name]
        all_names.append("Create new section...")

        target_item, ok = QInputDialog.getItem(self, "Move Seats", "Select target section:", all_names, editable=False)
        if not ok or not target_item:
            return

        if target_item == "Create new section...":
            target_name, ok2 = QInputDialog.getText(self, "New Section", "Enter name for new section:")
            if not ok2 or not target_name:
                return
            target_name = target_name.strip()
            if not target_name:
                return
            if target_name in mainwindow.seating_plan.sections:
                QMessageBox.warning(self, "Exists", "Section by that name already exists.")
                return
            # push snapshot via aboutToModify in caller
            mainwindow.seating_plan.add_section(target_name)
            target = target_name
        else:
            target = target_item

        # perform move
        selected_items = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected_items:
            return

        # notify about to modify so MainWindow can take a snapshot
        self.aboutToModify.emit()

        target_section = mainwindow.seating_plan.sections.get(target)
        if not target_section:
            QMessageBox.warning(self, "Target Missing", "Target section could not be found.")
            return

        for item in selected_items:
            key = f"{item.row}-{item.seat}"
            seat_obj = self.section.seats.get(key)
            if seat_obj:
                # add to target and remove from current
                target_section.add_seat(seat_obj.row_number, seat_obj.seat_number)
                self.section.delete_seat(seat_obj.row_number, seat_obj.seat_number)

        # refresh main UI and this view
        try:
            mainwindow.refresh_section_table()
        except Exception:
            pass
        self.load_section(self.section)
        self.sectionModified.emit()

    # ---------- Seat Manipulation ----------
    def add_seat_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog("seat", self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        row = data.get("row")
        if not row:
            return

        start = data["start_seat"]
        end = data["end_seat"]
        parity = data.get("parity", "all")

        # build seat labels using alphanum helper
        seats = alphanum_range(start, end)
        if not seats:
            # fallback: attempt numeric interpretation
            try:
                a = int(start); b = int(end)
                if a > b:
                    a, b = b, a
                seats = [str(i) for i in range(a, b+1)]
            except Exception:
                QMessageBox.warning(self, "Invalid range", "Could not interpret start/end seat range.")
                return

        # notify about to modify (so undo snapshot can be taken)
        self.aboutToModify.emit()

        if parity == "all":
            for s in seats:
                self.section.add_seat(row, s)
        else:
            for s in seats:
                if s.isdigit():
                    val = int(s)
                    keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                    if keep:
                        self.section.add_seat(row, s)
                else:
                    # skip non-numeric seat labels for even/odd parity
                    continue

        self.load_section(self.section)
        self.sectionModified.emit()

    def add_row_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog("row", self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        start_row = data.get("start_row")
        end_row = data.get("end_row")
        if not start_row or not end_row:
            return

        start_seat = data["start_seat"]
        end_seat = data["end_seat"]
        parity = data.get("parity", "all")
        continuous = bool(data.get("continuous", False))

        # Build rows list (numeric or letter ranges supported)
        rows = []
        try:
            rs = int(start_row); re = int(end_row)
            if rs <= re:
                rows = [str(i) for i in range(rs, re + 1)]
            else:
                rows = [str(i) for i in range(re, rs + 1)]
        except ValueError:
            # letter range
            try:
                si = ascii_uppercase.index(start_row.upper())
                ei = ascii_uppercase.index(end_row.upper())
                if si <= ei:
                    rows = list(ascii_uppercase[si:ei+1])
                else:
                    rows = list(ascii_uppercase[ei:si+1])
            except Exception:
                QMessageBox.warning(self, "Invalid rows", "Could not interpret start/end row range.")
                return

        if not rows:
            return

        # notify before bulk modification
        self.aboutToModify.emit()

        # Continuous numbering logic only supported for numeric seat labels
        if continuous:
            # verify numeric seats
            try:
                s0 = int(start_seat); s1 = int(end_seat)
            except Exception:
                QMessageBox.warning(self, "Continuous numbering",
                                    "Continuous numbering is only supported for numeric seat labels. Falling back to per-row numbering.")
                continuous = False

        if continuous:
            # compute seats per row and sequential numbering across rows
            if s0 <= s1:
                seats_per_row = s1 - s0 + 1
                seq = s0
            else:
                seats_per_row = s0 - s1 + 1
                seq = s1

            for _row in rows:
                for i in range(seats_per_row):
                    seat_label = str(seq)
                    if parity == "all":
                        self.section.add_seat(_row, seat_label)
                    else:
                        val = int(seat_label)
                        keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                        if keep:
                            self.section.add_seat(_row, seat_label)
                    seq += 1
        else:
            # standard behavior: apply same seat range for each row
            seats = alphanum_range(start_seat, end_seat)
            if not seats:
                # fallback to numeric if possible
                try:
                    a = int(start_seat); b = int(end_seat)
                    if a > b:
                        a, b = b, a
                    seats = [str(i) for i in range(a, b+1)]
                except Exception:
                    QMessageBox.warning(self, "Invalid seats", "Could not interpret start/end seat range.")
                    return

            if parity == "all":
                for r in rows:
                    for s in seats:
                        self.section.add_seat(r, s)
            else:
                for r in rows:
                    for s in seats:
                        if s.isdigit():
                            val = int(s)
                            keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                            if keep:
                                self.section.add_seat(r, s)
                        else:
                            # skip non-numeric for even/odd
                            continue

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

        # Panning state
        self._panning = False
        self._pan_start = None

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

    def mousePressEvent(self, event):
        # Start panning when middle button (mouse wheel) is pressed
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            # disable rubberband while panning
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_start is not None:
            # compute delta in viewport coordinates and scroll accordingly
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            # Adjust the view's position directly instead of relying on scrollbars
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            # restore rubberband drag
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            event.accept()
            return
        super().mouseReleaseEvent(event)