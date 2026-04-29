class Seat:
    """Represents a seat in a section with row and seat number."""

    def __init__(self, row_number: str, seat_number: str) -> None:
        self.row_number: str = row_number
        self.seat_number: str = seat_number

    def __repr__(self) -> str:
        return f"Seat(row_number='{self.row_number}', seat_number='{self.seat_number}')"