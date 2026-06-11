"""Dialogs for seat management and file operations."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QGroupBox, QDialogButtonBox, QFileDialog,
)
from .base import InputDialog


class NewPlanDialog(InputDialog):
    """Dialog to create a new seating plan with custom name."""

    def __init__(self, parent=None):
        super().__init__(
            "New Seating Plan",
            "Plan name:",
            parent,
            "New Plan"
        )


class RangeInputDialog(QDialog):
    """Dialog for adding a range of rows, each filled with a seat range.

    Collects: start/end row, row prefix/suffix, start/end seat,
    seat prefix/suffix, parity filter, continuous numbering, and the
    unnumbered-rows option ('#' prefix).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Row Range")
        self.setMinimumWidth(360)

        layout = QFormLayout(self)

        self.start_row_field = QLineEdit()
        self.end_row_field = QLineEdit()

        self.row_prefix_field = QLineEdit()
        self.row_prefix_field.setPlaceholderText("Optional prefix (before row label)")
        self.row_suffix_field = QLineEdit()
        self.row_suffix_field.setPlaceholderText("Optional suffix (after row label)")

        # Seat inputs: text fields so letters are supported
        self.start_seat_field = QLineEdit()
        self.end_seat_field = QLineEdit()
        self.start_seat_field.setPlaceholderText("e.g. 1 or A")
        self.end_seat_field.setPlaceholderText("e.g. 10 or F")

        self.seat_prefix_field = QLineEdit()
        self.seat_prefix_field.setPlaceholderText("Optional prefix (before seat label)")
        self.seat_suffix_field = QLineEdit()
        self.seat_suffix_field.setPlaceholderText("Optional suffix (after seat label)")

        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["All", "Even", "Odd"])

        self.continuous_checkbox = QCheckBox("Continuous numbering across rows")
        self.continuous_checkbox.setToolTip(
            "When checked, seat numbers will continue across rows.\n"
            "Example: rows 1-3 with seats 1-10 and continuous checked => "
            "row1:1-10, row2:11-20, row3:21-30\n\n"
            "Continuous numbering only supports numeric seat labels."
        )

        self.unnumbered_rows_checkbox = QCheckBox("No numbered rows")
        self.unnumbered_rows_checkbox.setToolTip(
            "When checked, row numbers will have # prefix.\n"
        )

        layout.addRow("Start row:", self.start_row_field)
        layout.addRow("End row:", self.end_row_field)
        layout.addRow("Row prefix:", self.row_prefix_field)
        layout.addRow("Row suffix:", self.row_suffix_field)
        layout.addRow("Start seat:", self.start_seat_field)
        layout.addRow("End seat:", self.end_seat_field)
        layout.addRow("Seat prefix:", self.seat_prefix_field)
        layout.addRow("Seat suffix:", self.seat_suffix_field)
        layout.addRow("Seat filter:", self.parity_combo)
        layout.addRow(self.continuous_checkbox)
        layout.addRow(self.unnumbered_rows_checkbox)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_values(self) -> dict:
        return {
            "start_row": self.start_row_field.text().strip(),
            "end_row": self.end_row_field.text().strip(),
            "row_prefix": self.row_prefix_field.text().strip(),
            "row_suffix": self.row_suffix_field.text().strip(),
            "start_seat": self.start_seat_field.text().strip(),
            "end_seat": self.end_seat_field.text().strip(),
            "seat_prefix": self.seat_prefix_field.text().strip(),
            "seat_suffix": self.seat_suffix_field.text().strip(),
            "parity": self.parity_combo.currentText().lower(),
            "continuous": self.continuous_checkbox.isChecked(),
            "unnumbered_rows": self.unnumbered_rows_checkbox.isChecked(),
        }


class AddCustomRowsDialog(QDialog):
    """Dialog for adding seats to a custom list of rows (one row per line)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Rows")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter row numbers (one per line):"))
        self.rows_input = QTextEdit()
        self.rows_input.setPlaceholderText("Enter rows here, one per line:\nA\nB\nC\n...")
        layout.addWidget(self.rows_input)

        seat_group = QGroupBox("Seat Range")
        seat_layout = QVBoxLayout()
        self.start_seat_input = QLineEdit()
        self.end_seat_input = QLineEdit()
        seat_layout.addWidget(QLabel("Start Seat:"))
        seat_layout.addWidget(self.start_seat_input)
        seat_layout.addWidget(QLabel("End Seat:"))
        seat_layout.addWidget(self.end_seat_input)
        seat_group.setLayout(seat_layout)
        layout.addWidget(seat_group)

        prefix_suffix_group = QGroupBox("Row Prefix/Suffix")
        prefix_suffix_layout = QVBoxLayout()
        self.prefix_input = QLineEdit()
        self.suffix_input = QLineEdit()
        prefix_suffix_layout.addWidget(QLabel("Prefix:"))
        prefix_suffix_layout.addWidget(self.prefix_input)
        prefix_suffix_layout.addWidget(QLabel("Suffix:"))
        prefix_suffix_layout.addWidget(self.suffix_input)
        prefix_suffix_group.setLayout(prefix_suffix_layout)
        layout.addWidget(prefix_suffix_group)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["All", "Even", "Odd"])
        options_layout.addWidget(QLabel("Seat Filter:"))
        options_layout.addWidget(self.parity_combo)
        self.continuous_checkbox = QCheckBox("Continuous Numbering")
        self.continuous_checkbox.setToolTip("Number seats sequentially across all rows.")
        options_layout.addWidget(self.continuous_checkbox)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> dict:
        rows_text = self.rows_input.toPlainText().strip()
        rows = [line.strip() for line in rows_text.split('\n') if line.strip()]
        return {
            "rows": rows,
            "start_seat": self.start_seat_input.text().strip(),
            "end_seat": self.end_seat_input.text().strip(),
            "row_prefix": self.prefix_input.text() or "",
            "row_suffix": self.suffix_input.text() or "",
            "parity": self.parity_combo.currentText().lower(),
            "continuous": self.continuous_checkbox.isChecked(),
        }


class RenumberRowsDialog(QDialog):
    """Dialog to ask for starting row number for renumbering."""

    def __init__(self, selected_rows: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Renumber Rows")
        self.setModal(True)
        self.selected_rows = selected_rows

        layout = QFormLayout()

        # Display selected rows
        layout.addRow("Selected rows:", QLabel(", ".join(selected_rows)))

        # Input for new starting row
        self.start_row_input = QLineEdit()
        self.start_row_input.setPlaceholderText("e.g., 1 or A")
        self.start_row_input.setText("1")
        layout.addRow("Start numbering from:", self.start_row_input)

        # Unnumbered rows checkbox
        self.is_unnumbered_checkbox = QCheckBox("Unnumbered Rows")
        self.is_unnumbered_checkbox.setToolTip("Add '#' prefix to row numbers for unnumbered rows")
        layout.addRow("", self.is_unnumbered_checkbox)

        # Info label
        info = QLabel("Rows will be numbered sequentially from the starting number.")
        info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("", info)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_start_row(self) -> str:
        """Get the starting row number (without prefix - prefix is added separately)."""
        return self.start_row_input.text().strip()

    def is_unnumbered_enabled(self) -> bool:
        """Return whether unnumbered mode is enabled."""
        return self.is_unnumbered_checkbox.isChecked()


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
