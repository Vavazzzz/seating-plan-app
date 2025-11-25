from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox, QDialogButtonBox
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

        if mode == "seat":
            layout.addRow("Row:", self.row_field)
        else:
            layout.addRow("Start row:", self.start_row_field)
            layout.addRow("End row:", self.end_row_field)

        layout.addRow("Start seat:", self.start_seat_spin)
        layout.addRow("End seat:", self.end_seat_spin)
        layout.addRow("Seat filter:", self.parity_combo)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_values(self) -> dict:
        parity = self.parity_combo.currentText().lower()  # "all", "even", "odd"
        if self.mode == "seat":
            return {
                "row": self.row_field.text().strip(),
                "start_seat": self.start_seat_spin.value(),
                "end_seat": self.end_seat_spin.value(),
                "parity": parity
            }
        else:
            return {
                "start_row": self.start_row_field.text().strip(),
                "end_row": self.end_row_field.text().strip(),
                "start_seat": self.start_seat_spin.value(),
                "end_seat": self.end_seat_spin.value(),
                "parity": parity
            }