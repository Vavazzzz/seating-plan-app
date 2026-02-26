from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsRectItem, QGraphicsSimpleTextItem, QSlider, QLabel, QFrame,
    QMenu, QInputDialog, QMessageBox, QDialog, QTextEdit, QGroupBox, QLineEdit,
    QDialogButtonBox, QComboBox, QCheckBox
)
from PyQt6.QtGui import QBrush, QPen, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from ..models.section import Section
from ..utils.alphanum_handler import alphanum_range, alphanum_sort_key
from .dialogs import RangeInputDialog, RenumberRowsDialog
from string import ascii_uppercase

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
    aboutToModify = pyqtSignal()   # emitted before mutating ops (for undo)
    sectionModified = pyqtSignal()  # emitted after mutation (for refresh)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.section: Section | None = None
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.is_collapsed = False  # State for collapse/expand

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

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_add_row_range)
        controls_layout.addWidget(self.btn_add_custom_rows)
        controls_layout.addWidget(self.btn_delete_seat)
        controls_layout.addWidget(self.btn_delete_row)
        controls_layout.addWidget(self.btn_renumber_rows)
        controls_layout.addWidget(self.btn_toggle_collapse)
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

        all_seat_numbers = sorted({s.seat_number for s in section.seats.values()}, key=alphanum_sort_key)

        sorted_rows = sorted(seats_by_row.keys(), key=alphanum_sort_key)

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

    def toggle_collapse_section(self):
        """Toggle between collapsed and normal view of the section."""
        self.is_collapsed = not self.is_collapsed
        self.btn_toggle_collapse.setChecked(self.is_collapsed)
        if self.section:
            self.load_section(self.section)

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
    def add_row_range_dialog(self):
        if not self.section:
            return
        dialog = RangeInputDialog("row", self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_values()
        start_row = data.get("start_row")
        end_row = data.get("end_row")
        prefix = data.get("row_prefix", "") or ""
        suffix = data.get("row_suffix", "") or ""
        if not start_row or not end_row:
            return

        start_seat = data["start_seat"]
        end_seat = data["end_seat"]
        parity = data.get("parity", "all")
        continuous = bool(data.get("continuous", False))
        unnamaberedrows = bool(data.get("unnambered_rows", False))

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

        if unnamaberedrows:
            rows = [f"#{r}" for r in rows_raw]
        else:
            # Compose final row labels with prefix/suffix
            rows = [f"{prefix}{r}{suffix}" for r in rows_raw]

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

    def add_custom_rows_dialog(self):
        """Add seats to custom rows specified as text input (one row per line)."""
        if not self.section:
            return
        
        # Create dialog for custom rows input
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Custom Rows")
        dialog.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Label for rows
        rows_label = QLabel("Enter row numbers (one per line):")
        layout.addWidget(rows_label)
        
        # Text edit for custom rows
        rows_input = QTextEdit()
        rows_input.setPlaceholderText("Enter rows here, one per line:\nA\nB\nC\n...")
        layout.addWidget(rows_input)
        
        # Seat range section
        seat_group = QGroupBox("Seat Range")
        seat_layout = QVBoxLayout()
        
        start_seat_label = QLabel("Start Seat:")
        start_seat_input = QLineEdit()
        seat_layout.addWidget(start_seat_label)
        seat_layout.addWidget(start_seat_input)
        
        end_seat_label = QLabel("End Seat:")
        end_seat_input = QLineEdit()
        seat_layout.addWidget(end_seat_label)
        seat_layout.addWidget(end_seat_input)
        
        seat_group.setLayout(seat_layout)
        layout.addWidget(seat_group)
        
        # Row prefix/suffix section
        prefix_suffix_group = QGroupBox("Row Prefix/Suffix")
        prefix_suffix_layout = QVBoxLayout()
        
        prefix_label = QLabel("Prefix:")
        prefix_input = QLineEdit()
        prefix_suffix_layout.addWidget(prefix_label)
        prefix_suffix_layout.addWidget(prefix_input)
        
        suffix_label = QLabel("Suffix:")
        suffix_input = QLineEdit()
        prefix_suffix_layout.addWidget(suffix_label)
        prefix_suffix_layout.addWidget(suffix_input)
        
        prefix_suffix_group.setLayout(prefix_suffix_layout)
        layout.addWidget(prefix_suffix_group)
        
        # Options section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        parity_label = QLabel("Seat Filter:")
        parity_combo = QComboBox()
        parity_combo.addItems(["All", "Even", "Odd"])
        options_layout.addWidget(parity_label)
        options_layout.addWidget(parity_combo)
        
        continuous_checkbox = QCheckBox("Continuous Numbering")
        continuous_checkbox.setToolTip("Number seats sequentially across all rows.")
        options_layout.addWidget(continuous_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Get input values
        rows_text_value = rows_input.toPlainText().strip()
        start_seat = start_seat_input.text().strip()
        end_seat = end_seat_input.text().strip()
        prefix = prefix_input.text() or ""
        suffix = suffix_input.text() or ""
        parity = parity_combo.currentText().lower()
        continuous = continuous_checkbox.isChecked()
        
        if not rows_text_value or not start_seat or not end_seat:
            QMessageBox.warning(self, "Missing Input", "Please fill in all fields.")
            return
        
        # Parse rows from text (one per line, strip whitespace, apply prefix/suffix)
        rows_raw = [line.strip() for line in rows_text_value.split('\n') if line.strip()]
        rows = [f"{prefix}{r}{suffix}" for r in rows_raw]
        
        if not rows:
            QMessageBox.warning(self, "No Rows", "No valid rows were entered.")
            return
        
        # Get seat range
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
        
        if not seats:
            QMessageBox.warning(self, "No Seats", "Could not generate seat range.")
            return
        
        # notify before bulk modification
        self.aboutToModify.emit()
        
        # Add seats with options
        if continuous:
            # Continuous numbering logic only supported for numeric seat labels
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
            
            for row in rows:
                for i in range(seats_per_row):
                    seat_label = str(seq)
                    if parity == "all":
                        self.section.add_seat(row, seat_label)
                    else:
                        val = int(seat_label)
                        keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                        if keep:
                            self.section.add_seat(row, seat_label)
                    seq += 1
        else:
            # Standard behavior: apply same seat range for each row
            if parity == "all":
                for row in rows:
                    for seat in seats:
                        self.section.add_seat(row, seat)
            else:
                for row in rows:
                    for seat in seats:
                        if seat.isdigit():
                            val = int(seat)
                            keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                            if keep:
                                self.section.add_seat(row, seat)
                        else:
                            # skip non-numeric for even/odd
                            continue
        
        self.load_section(self.section)
        self.sectionModified.emit()
        QMessageBox.information(self, "Success", f"Added seats to {len(rows)} rows.")

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
        
        # Show dialog
        dialog = RenumberRowsDialog(selected_rows, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_start = dialog.get_start_row()
        if not new_start:
            QMessageBox.warning(self, "Invalid Input", "Please enter a starting row number.")
            return
        
        is_unnumbered = dialog.is_unnumbered_enabled()
        
        # Apply renumbering
        try:
            self.aboutToModify. emit()
            self.section. renumber_rows(selected_rows, new_start, add_prefix=is_unnumbered)
            self.load_section(self.section)
            self.sectionModified.emit()
            
            # Show success message with details
            unnumbered_text = " (Unnumbered)" if is_unnumbered else ""
            QMessageBox.information(
                self, 
                "Success", 
                f"Rows renumbered successfully!{unnumbered_text}\nStarting from:  {new_start}"
            )
        except Exception as e:  
            QMessageBox.critical(self, "Error", f"Failed to renumber rows: {str(e)}")

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