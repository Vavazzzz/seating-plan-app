import re

from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider, QLabel, QFrame,
    QMenu, QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QBrush, QPen, QPainter, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QPoint
from domain.models.section import Section
from domain.utils.alphanum_handler import alphanum_range, alphanum_sort_key
from .dialogs import RangeInputDialog, AddCustomRowsDialog, RenumberRowsDialog

class SeatItemRect:
    WIDTH = 25
    HEIGHT = 25

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
        # CENTER THE TEXT
        self.center_text()

    def center_text(self):
        text_rect = self.text_item.boundingRect()
        x = (SeatItemRect.WIDTH - text_rect.width()) / 2
        y = (SeatItemRect.HEIGHT - text_rect.height()) / 2
        self.text_item.setPos(x, y)

    def update_visual(self):
        self.setBrush(QBrush(Qt.GlobalColor.green if self.isSelected() else Qt.GlobalColor.lightGray))

class SectionView(QWidget):
    """A QWidget for rendering and manipulating a Section in a seating plan."""
    selectionChanged = pyqtSignal(int)
    sectionModified = pyqtSignal()  # emitted after mutation (for refresh)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.is_collapsed = False  # State for collapse/expand
        self.is_split = False  # State for even/odd split view

        # Controls
        self.btn_add_row_range = QPushButton("\u2795 Add Row Range")
        self.btn_add_row_range.setToolTip("Add multiple rows with seat ranges.")
        self.btn_add_custom_rows = QPushButton("\u2795 Add Custom Rows")
        self.btn_add_custom_rows.setToolTip("Add seats to custom rows (input rows as text lines).")
        self.btn_delete_seat = QPushButton("\U0001F5D1 Delete Seats")
        self.btn_delete_seat.setToolTip("Delete selected seats (Del).")
        self.btn_delete_row = QPushButton("\U0001F5D1 Delete Rows")
        self.btn_delete_row.setToolTip("Delete selected rows (by selecting seats in those rows).")
        self.btn_renumber_rows = QPushButton("\U0001F503 Renumber Rows")
        self.btn_renumber_rows.setToolTip("Renumber rows sequentially (not implemented).")
        self.btn_toggle_collapse = QPushButton("\U0001F4C9 Collapse Section")
        self.btn_toggle_collapse.setToolTip("Collapse section (stack all seats on top of each other).")
        self.btn_toggle_collapse.setCheckable(True)
        self.btn_toggle_split = QPushButton("⇄ Split Even/Odd")
        self.btn_toggle_split.setToolTip("Split section into odd and even seat banks with an aisle between.")
        self.btn_toggle_split.setCheckable(True)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_add_row_range)
        controls_layout.addWidget(self.btn_add_custom_rows)
        controls_layout.addWidget(self.btn_delete_seat)
        controls_layout.addWidget(self.btn_delete_row)
        controls_layout.addWidget(self.btn_renumber_rows)
        controls_layout.addWidget(self.btn_toggle_collapse)
        controls_layout.addWidget(self.btn_toggle_split)
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
        self.btn_add_row_range.clicked.connect(self.add_row_range_dialog)
        self.btn_add_custom_rows.clicked.connect(self.add_custom_rows_dialog)
        self.btn_delete_seat.clicked.connect(self.delete_selected_seats)
        self.btn_delete_row.clicked.connect(self.delete_selected_rows)
        self.btn_renumber_rows.clicked.connect(self.renumber_selected_rows)
        self.btn_toggle_collapse.clicked.connect(self.toggle_collapse_section)
        self.btn_toggle_split.clicked.connect(self.toggle_split_section)

        self.view.viewport().installEventFilter(self)
        self._updating_slider = False

        # Service reference for undo/redo support
        self.seat_service = None

        # Keyboard shortcuts
        QShortcut(QKeySequence.StandardKey.SelectAll, self).activated.connect(self.select_all_seats)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.deselect_all_seats)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.zoom_slider.setValue(100))

    def set_seat_service(self, seat_service):
        """Set the seat service for operations to go through command handler."""
        self.seat_service = seat_service

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

        all_seat_numbers = sorted({s.seat_number for s in section.seats.values()}, key=alphanum_sort_key)

        sorted_rows = sorted(seats_by_row.keys(), key=alphanum_sort_key)

        # Layout constants
        x_spacing = SeatItemRect.WIDTH + 5
        y_spacing = SeatItemRect.HEIGHT + 10

        split_columns = None
        aisle_center = None
        total_width = len(all_seat_numbers) * x_spacing
        if self.is_split and not self.is_collapsed:
            split_columns, total_width, banks = self._build_split_columns(all_seat_numbers, x_spacing)
            for label, start_x, count in banks:
                header = self.scene.addSimpleText(label)
                header_rect = header.boundingRect()
                header.setPos(start_x + (count * x_spacing - header_rect.width()) / 2, -25)
            if len(banks) >= 2:
                # Center of the aisle between the first two banks
                first_bank_end = banks[0][1] + banks[0][2] * x_spacing - 5
                aisle_center = (first_bank_end + banks[1][1]) / 2

        section_label = self.scene.addText(section.name)
        section_label.setPos((total_width + 10) / 2, -50)

        # Render seats
        y = 0
        for row in sorted_rows:
            seats = {s.seat_number: s for s in seats_by_row[row]}
            row_label_sx = self.scene.addSimpleText(str(row))
            row_label_sx.setPos(-40, y)
            
            if self.is_collapsed:
                # Collapsed mode: each row starts at x=0, seats arranged by their order
                row_label_dx = self.scene.addSimpleText(str(row))
                sorted_seat_nums = sorted(seats.keys(), key=alphanum_sort_key)
                row_label_dx.setPos(len(sorted_seat_nums) * x_spacing + 10, y)
                
                for idx, seat_num in enumerate(sorted_seat_nums):
                    seat = seats[seat_num]
                    x = idx * x_spacing
                    item = SeatItem(row, seat.seat_number)
                    item.setPos(x, y)
                    self.scene.addItem(item)
            elif split_columns is not None:
                # Split mode: odd bank mirrored on the left, aisle, even bank on the right
                row_label_dx = self.scene.addSimpleText(str(row))
                row_label_dx.setPos(total_width + 10, y)

                if aisle_center is not None:
                    row_label_mid = self.scene.addSimpleText(str(row))
                    mid_rect = row_label_mid.boundingRect()
                    row_label_mid.setPos(aisle_center - mid_rect.width() / 2,
                                         y + (SeatItemRect.HEIGHT - mid_rect.height()) / 2)

                for seat_num, x in split_columns.items():
                    if seat_num in seats:
                        seat = seats[seat_num]
                        item = SeatItem(row, seat.seat_number)
                        item.setPos(x, y)
                        self.scene.addItem(item)
            else:
                # Normal mode: align all rows to the same grid
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

    def _build_split_columns(
        self, all_seat_numbers: list[str], x_spacing: int
    ) -> tuple[dict[str, int], int, list[tuple[str, int, int]]]:
        """Assign an x position to each seat number: odd bank descending toward
        the aisle (so seat 1 faces seat 2), then even bank ascending, then any
        seats without digits. Returns (seat_number -> x, total width, banks),
        where each bank is (header label, start x, column count)."""
        odds, evens, others = [], [], []
        for seat_num in all_seat_numbers:
            digits = re.search(r"\d+", seat_num)
            if digits is None:
                others.append(seat_num)
            elif int(digits.group()) % 2 == 0:
                evens.append(seat_num)
            else:
                odds.append(seat_num)

        aisle = 2 * x_spacing
        columns = {}
        banks = []
        x = 0
        for label, bank in (("ODD", list(reversed(odds))), ("EVEN", evens), ("OTHER", others)):
            if not bank:
                continue
            banks.append((label, x, len(bank)))
            for seat_num in bank:
                columns[seat_num] = x
                x += x_spacing
            x += aisle
        total_width = x - aisle if banks else 0
        return columns, total_width, banks

    def toggle_collapse_section(self):
        """Toggle between collapsed and normal view of the section."""
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed and self.is_split:
            self.is_split = False
            self.btn_toggle_split.setChecked(False)
        self.btn_toggle_collapse.setChecked(self.is_collapsed)
        if self.section:
            self.load_section(self.section)

    def toggle_split_section(self):
        """Toggle between even/odd split and normal view of the section."""
        self.is_split = not self.is_split
        if self.is_split and self.is_collapsed:
            self.is_collapsed = False
            self.btn_toggle_collapse.setChecked(False)
        self.btn_toggle_split.setChecked(self.is_split)
        if self.section:
            self.load_section(self.section)

    # ---------- Context menu and move seats ----------
    def move_selected_seats_dialog(self):
        """Move selected seats to an existing or new section."""
        if not self.section or not self.seat_service:
            return

        mainwindow = self.window()
        if not mainwindow or not hasattr(mainwindow, "seating_plan") or not hasattr(mainwindow, "section_service"):
            return

        current_section_name = self.section.name
        all_names = [
            name for name in mainwindow.seating_plan.sections.keys()
            if name != current_section_name
        ]
        all_names.append("Create new section...")

        target_item, ok = QInputDialog.getItem(
            self, "Move Seats", "Select target section:", all_names, editable=False
        )
        if not ok or not target_item:
            return

        if target_item == "Create new section...":
            target_name, ok2 = QInputDialog.getText(
                self, "New Section", "Enter name for new section:"
            )
            if not ok2:
                return
            target_name = target_name.strip()
            if not target_name:
                return
            result_create = mainwindow.section_service.add_section(target_name)
            if not result_create.is_success():
                QMessageBox.warning(self, "Error", str(result_create.error))
                return
            target = target_name
        else:
            target = target_item

        selected_items = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected_items:
            return

        seats_to_move = [(item.row, str(item.seat)) for item in selected_items]
        result = self.seat_service.move_seats(current_section_name, target, seats_to_move)

        if not result.is_success():
            QMessageBox.warning(self, "Error", str(result.error))
            return

        moved = result.value
        skipped = len(seats_to_move) - moved
        self.load_section(self.section)
        self.sectionModified.emit()

        if skipped > 0:
            QMessageBox.warning(
                self,
                "Partial Move",
                f"Moved {moved} seat(s) to '{target}'. {skipped} skipped (already exist in target)."
            )

    # ---------- Seat Manipulation ----------
    def add_row_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        start_row = data.get("start_row")
        end_row = data.get("end_row")
        row_prefix = data.get("row_prefix", "") or ""
        row_suffix = data.get("row_suffix", "") or ""
        seat_prefix = data.get("seat_prefix", "") or ""
        seat_suffix = data.get("seat_suffix", "") or ""
        if not start_row or not end_row:
            return

        start_seat = data["start_seat"]
        end_seat = data["end_seat"]
        parity = data.get("parity", "all")
        continuous = bool(data.get("continuous", False))
        unnumbered_rows = bool(data.get("unnumbered_rows", False))

        # Build rows list (numeric or letter ranges supported)
        rows_raw = []
        try:
            rs = int(start_row); re = int(end_row)
            if rs <= re:
                rows_raw = [str(i) for i in range(rs, re + 1)]
            else:
                rows_raw = [str(i) for i in range(re, rs + 1)]
        except ValueError:
            # letter range
            try:
                rows_raw = alphanum_range(start_row, end_row)
            except Exception:
                QMessageBox.warning(self, "Invalid rows", "Could not interpret start/end row range.")
                return

        if unnumbered_rows:
            rows = [f"#{r}" for r in rows_raw]
        else:
            # Compose final row labels with prefix/suffix
            rows = [f"{row_prefix}{r}{row_suffix}" for r in rows_raw]

        if not rows:
            return

        # Use SeatService for undo/redo support
        if not self.seat_service:
            return
        
        result = self.seat_service.add_rows_bulk(
            self.section.name,
            rows=rows,
            start_seat=start_seat,
            end_seat=end_seat,
            seat_prefix=seat_prefix,
            seat_suffix=seat_suffix,
            parity=parity,
            continuous=continuous
        )
        
        if result.is_success():
            self.load_section(self.section)
            self.sectionModified.emit()
        else:
            QMessageBox.warning(self, "Error", f"Failed to add rows: {result.error}")

    def add_custom_rows_dialog(self):
        """Add seats to custom rows specified as text input (one row per line)."""
        if not self.section:
            return

        dialog = AddCustomRowsDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_values()
        rows_raw = data["rows"]
        start_seat = data["start_seat"]
        end_seat = data["end_seat"]

        if not rows_raw or not start_seat or not end_seat:
            QMessageBox.warning(self, "Missing Input", "Please fill in all fields.")
            return

        rows = [f"{data['row_prefix']}{r}{data['row_suffix']}" for r in rows_raw]

        # Use SeatService for undo/redo support
        if not self.seat_service:
            return

        result = self.seat_service.add_rows_bulk(
            self.section.name,
            rows=rows,
            start_seat=start_seat,
            end_seat=end_seat,
            parity=data["parity"],
            continuous=data["continuous"]
        )

        if result.is_success():
            self.load_section(self.section)
            self.sectionModified.emit()
            QMessageBox.information(self, "Success", f"Added seats to {len(rows)} rows.")
        else:
            QMessageBox.warning(self, "Error", f"Failed to add rows: {result.error}")

    def delete_selected_seats(self):
        if not self.section or not self.seat_service:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected:
            return
        
        # Collect (row, seat) tuples and delete via SeatService
        seats_to_delete = [(item.row, str(item.seat)) for item in selected]
        result = self.seat_service.delete_seats(self.section.name, seats_to_delete)
        
        if result.is_success():
            self.load_section(self.section)
            self.sectionModified.emit()
        else:
            QMessageBox.warning(self, "Error", f"Failed to delete seats: {result.error}")

    def delete_selected_rows(self):
        if not self.section or not self.seat_service:
            return
        rows = {item.row for item in self.scene.selectedItems() if isinstance(item, SeatItem)}
        if not rows:
            return
        
        # Delete each row via SeatService (each gets its own command for undo/redo)
        failed = []
        for row in rows:
            result = self.seat_service.delete_row(self.section.name, row)
            if not result.is_success():
                failed.append((row, str(result.error)))
        
        if not failed:
            self.load_section(self.section)
            self.sectionModified.emit()
        else:
            error_msg = "\n".join([f"Row {r}: {e}" for r, e in failed])
            QMessageBox.warning(self, "Error", f"Failed to delete some rows:\n{error_msg}")

    def renumber_selected_rows(self):
        """Renumber selected rows with user-specified starting row."""
        if not self.section: 
            return
        
        # Get selected seats
        selected = [item for item in self.scene.selectedItems() if isinstance(item, SeatItem)]
        if not selected:  
            QMessageBox.warning(self, "No Selection", "Please select seats to renumber their rows.")
            return
        
        # Extract unique rows from selected seats, maintaining order of appearance
        selected_rows = []
        seen = set()
        for item in selected:
            if item.row not in seen:
                selected_rows.append(item.row)
                seen.add(item.row)
        
        if not selected_rows:
            return
        
        sorted_rows = sorted(selected_rows, key=alphanum_sort_key)

        # Show dialog
        dialog = RenumberRowsDialog(sorted_rows, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_start = dialog.get_start_row()
        if not new_start:
            QMessageBox.warning(self, "Invalid Input", "Please enter a starting row number.")
            return
        
        is_unnumbered = dialog.is_unnumbered_enabled()
        
        # Use SeatService for undo/redo support
        if not self.seat_service:
            return
        
        result = self.seat_service.renumber_rows(
            self.section.name,
            sorted_rows,
            new_start,
            add_prefix=is_unnumbered
        )
        
        if result.is_success():
            self.load_section(self.section)
            self.sectionModified.emit()
            
            # Show success message with details
            unnumbered_text = " (Unnumbered)" if is_unnumbered else ""
            QMessageBox.information(
                self, 
                "Success", 
                f"Rows renumbered successfully!{unnumbered_text}\nStarting from: {new_start}"
            )
        else:
            QMessageBox.critical(self, "Error", f"Failed to renumber rows: {result.error}")

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

    def select_all_in_row(self, row_number):
        """Select all seats in a specific row."""
        for it in self.scene.items():
            if isinstance(it, SeatItem) and it.row == row_number:
                it.setSelected(True)
        self.on_selection_changed()

    def deselect_all_seats(self):
        """Deselect all seats."""
        self.scene.clearSelection()
        self.on_selection_changed()

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
        # Handle right-click (context menu)
        if event.button() == Qt.MouseButton.RightButton:
            clicked_item = self.itemAt(event.pos())
            # If clicked on a seat, select it (if not already selected)
            if isinstance(clicked_item, SeatItem):
                if not clicked_item.isSelected():
                    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        # Clear selection if Ctrl is not held
                        self.scene().clearSelection()
                    clicked_item.setSelected(True)
                    self.section_view.on_selection_changed()
            # Show context menu at mouse position (always, regardless of selection)
            global_pos = self.mapToGlobal(event.pos())
            self.show_seat_context_menu(global_pos)
            event.accept()
            return
        
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

    def show_seat_context_menu(self, global_pos: QPoint):
        """Show context menu for seat operations. Disabled items when no selection."""
        menu = QMenu(self)
        
        selected_items = [item for item in self.scene().selectedItems() if isinstance(item, SeatItem)]
        has_selection = len(selected_items) > 0
        
        # Delete selected seats - enabled only if there are selections
        delete_seats_action = menu.addAction("🗑️ Delete Selected Seats")
        delete_seats_action.setEnabled(has_selection)
        delete_seats_action.triggered.connect(self.section_view.delete_selected_seats)
        
        # Delete rows - enabled only if there are selections
        delete_rows_action = menu.addAction("🗑️ Delete Selected Rows")
        delete_rows_action.setEnabled(has_selection)
        delete_rows_action.triggered.connect(self.section_view.delete_selected_rows)
        
        menu.addSeparator()
        
        # Move to section - enabled only if there are selections
        move_action = menu.addAction("➡️ Move to Section...")
        move_action.setEnabled(has_selection)
        move_action.triggered.connect(self.section_view.move_selected_seats_dialog)
        
        menu.addSeparator()
        
        # Select all in row - enabled only if single row is selected
        if selected_items:
            rows = set(item.row for item in selected_items)
            if len(rows) == 1:
                select_row_action = menu.addAction(f"✓ Select All in Row {list(rows)[0]}")
                select_row_action.triggered.connect(lambda: self.section_view.select_all_in_row(list(rows)[0]))
        
        # Select all in section - always enabled
        select_all_action = menu.addAction("✓ Select All in Section")
        select_all_action.triggered.connect(self.section_view.select_all_seats)
        
        menu.addSeparator()
        
        # Deselect all - enabled only if there are selections
        deselect_all_action = menu.addAction("✕ Deselect All")
        deselect_all_action.setEnabled(has_selection)
        deselect_all_action.triggered.connect(self.section_view.deselect_all_seats)
        
        menu.exec(global_pos)