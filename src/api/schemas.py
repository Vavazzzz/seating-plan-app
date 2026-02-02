from typing import List, Optional
from pydantic import BaseModel

# Add schemas here

class SeatIn(BaseModel):
	seat_number: str

class SeatOut(BaseModel):
	seat_number: str

class RowOut(BaseModel):
	row_number: str
	seats: List[SeatOut]

class SectionCreate(BaseModel):
	name: str
	is_ga: bool = False

class SectionOut(BaseModel):
	name: str
	is_ga: bool
	rows: List[RowOut]

class CloneResponse(BaseModel):
	created: List[str]

class SeatRange(BaseModel):
	start_seat: str
	end_seat: str


class RowRange(BaseModel):
	start_row: str
	end_row: str
	start_seat: str
	end_seat: str
	parity: Optional[str] = "all"  # "all", "even", "odd"
	continuous: Optional[bool] = False
	row_prefix: Optional[str] = ""
	row_suffix: Optional[str] = ""
	unnumbered_rows: Optional[bool] = False


class BulkSeats(BaseModel):
	seat_numbers: List[str]


class RenameSection(BaseModel):
	new_name: str


class ProjectName(BaseModel):
	name: str


class ProjectInfo(BaseModel):
	filename: str