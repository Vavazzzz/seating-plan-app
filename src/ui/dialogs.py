from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox, QDialogButtonBox, QCheckBox
)

class RangeInputDialog(QDialog):
    """
    Generic dialog for creating seat or row ranges.
    mode: "seat" or "row"
    """
    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode  # 'seat' or 'row'
        self.setWindowTitle("Add " + ("Row Range" if mode == "row" else "Seat Range"))
        self.setMinimumWidth(320)

        layout = QFormLayout(self)

        # Fields
        self.row_field = QLineEdit()
        self.start_row_field = QLineEdit()
        self.end_row_field = QLineEdit()
        self.start_seat_spin = QSpinBox()
        self.end_seat_spin = QSpinBox()
        self.start_seat_spin.setRange(0, 10000)
        self.end_seat_spin.setRange(0, 10000)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["All", "Even", "Odd"])

        # New: continuous numbering option (for row mode)
        self.continuous_checkbox = QCheckBox("Continuous numbering across rows")
        self.continuous_checkbox.setToolTip(
            "When checked, seat numbers will continue across rows.\n"
            "Example: rows 1-3 with seats 1-10 and continuous checked => "
            "row1:1-10, row2:11-20, row3:21-30"
        )

        if mode == "seat":
            layout.addRow("Row:", self.row_field)
        else:
            layout.addRow("Start row:", self.start_row_field)
            layout.addRow("End row:", self.end_row_field)

        layout.addRow("Start seat:", self.start_seat_spin)
        layout.addRow("End seat:", self.end_seat_spin)
        layout.addRow("Seat filter:", self.parity_combo)
        if mode == "row":
            layout.addRow(self.continuous_checkbox)

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
            "start_seat": self.start_seat_spin.value(),
            "end_seat": self.end_seat_spin.value(),
            "parity": parity
        }
        if self.mode == "seat":
            base.update({
                "row": self.row_field.text().strip(),
                "continuous": False
            })
            return base
        else:
            base.update({
                "start_row": self.start_row_field.text().strip(),
                "end_row": self.end_row_field.text().strip(),
                "continuous": bool(self.continuous_checkbox.isChecked())
            })
            return base