class Seat:
    def __init__(self, row_number, seat_number):
        self.row_number = row_number
        self.seat_number = seat_number

    def __repr__(self):
        return f"Seat(row_number='{self.row_number}', seat_number='{self.seat_number}')"

    def to_dict(self):
        return {
            "row_number": self.row_number,
            "seat_number": self.seat_number
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['row_number'], data['seat_number'])