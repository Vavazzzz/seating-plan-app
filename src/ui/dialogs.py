from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt

class RangeInputDialog(QDialog):
    """
    Generic dialog for creating seat or row ranges.
    mode: "seat" or "row"

    Fields:
      - For seat mode:
          row (text), row_prefix, row_suffix, start_seat (text), end_seat (text),
          parity (All/Even/Odd)
      - For row mode:
          start_row (text), end_row (text), row_prefix, row_suffix, start_seat (text),
          end_seat (text), parity (All/Even/Odd), continuous (bool)
    """
    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode  # 'seat' or 'row'
        self.setWindowTitle("Add " + ("Row Range" if mode == "row" else "Seat Range"))
        self.setMinimumWidth(360)

        layout = QFormLayout(self)

        # Fields
        self.row_field = QLineEdit()
        self.start_row_field = QLineEdit()
        self.end_row_field = QLineEdit()

        # Prefix / suffix for row labels (applies to both modes)
        self.row_prefix_field = QLineEdit()
        self.row_prefix_field.setPlaceholderText("Optional prefix (before row label)")
        self.row_suffix_field = QLineEdit()
        self.row_suffix_field.setPlaceholderText("Optional suffix (after row label)")

        # Seat inputs: text fields so letters are supported. Keep a small width hint.
        self.start_seat_field = QLineEdit()
        self.end_seat_field = QLineEdit()
        self.start_seat_field.setPlaceholderText("e.g. 1 or A")
        self.end_seat_field.setPlaceholderText("e.g. 10 or F")

        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["All", "Even", "Odd"])

        # New: continuous numbering option (for row mode)
        self.continuous_checkbox = QCheckBox("Continuous numbering across rows")
        self.continuous_checkbox.setToolTip(
            "When checked, seat numbers will continue across rows.\n"
            "Example: rows 1-3 with seats 1-10 and continuous checked => "
            "row1:1-10, row2:11-20, row3:21-30\n\n"
            "Continuous numbering only supports numeric seat labels."
        )

        # New: no numbered rows option
        self.unnamberedrows_checkbox = QCheckBox("No numbered rows")
        self.unnamberedrows_checkbox.setToolTip(
            "When checked, row numbers will have # prefix.\n"
        )

        if mode == "seat":
            layout.addRow("Row:", self.row_field)
        else:
            layout.addRow("Start row:", self.start_row_field)
            layout.addRow("End row:", self.end_row_field)

        # Prefix/suffix appear for both modes
        layout.addRow("Row prefix:", self.row_prefix_field)
        layout.addRow("Row suffix:", self.row_suffix_field)

        layout.addRow("Start seat:", self.start_seat_field)
        layout.addRow("End seat:", self.end_seat_field)
        layout.addRow("Seat filter:", self.parity_combo)
        if mode == "row":
            layout.addRow(self.continuous_checkbox)
        layout.addRow(self.unnamberedrows_checkbox)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_values(self) -> dict:
        parity = self.parity_combo.currentText().lower()  # "all", "even", "odd"
        base = {
            "start_seat": self.start_seat_field.text().strip(),
            "end_seat": self.end_seat_field.text().strip(),
            "parity": parity
        }
        if self.mode == "seat":
            base.update({
                "row": self.row_field.text().strip(),
                "continuous": False,
                "unnambered_rows" : bool(self.unnamberedrows_checkbox.isChecked()),
                "row_prefix" : self.row_prefix_field.text().strip(),
                "row_suffix" : self.row_suffix_field.text().strip()
            })
            return base
        else:
            base.update({
                "start_row": self.start_row_field.text().strip(),
                "end_row": self.end_row_field.text().strip(),
                "continuous": bool(self.continuous_checkbox.isChecked()),
                "unnambered_rows" : bool(self.unnamberedrows_checkbox.isChecked()),
                "row_prefix" : self.row_prefix_field.text().strip(),
                "row_suffix" : self.row_suffix_field.text().strip()
            })
            return base