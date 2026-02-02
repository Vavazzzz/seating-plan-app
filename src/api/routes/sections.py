from fastapi import APIRouter, Depends, HTTPException
from typing import List
from string import ascii_uppercase

from src.models.seating_plan import SeatingPlan
from src.api.schemas import SectionCreate, SectionOut, CloneResponse, BulkSeats, SeatRange, RenameSection, RowRange
from src.utils.alphanum_handler import alphanum_range

from src.api.dependencies import get_plan

router = APIRouter()


@router.get("/", response_model=List[SectionOut])
def list_sections(plan: SeatingPlan = Depends(get_plan)):
	return [section.to_dict() for section in plan.sections.values()]


@router.post("/", response_model=SectionOut, status_code=201)
def create_section(payload: SectionCreate, plan: SeatingPlan = Depends(get_plan)):
	if payload.name in plan.sections:
		raise HTTPException(status_code=409, detail="Section already exists")
	plan.add_section(payload.name, is_ga=payload.is_ga)
	return plan.sections[payload.name].to_dict()


@router.get("/{name}", response_model=SectionOut)
def get_section(name: str, plan: SeatingPlan = Depends(get_plan)):
	if name not in plan.sections:
		raise HTTPException(status_code=404, detail="Section not found")
	return plan.sections[name].to_dict()


@router.delete("/{name}", status_code=204)
def delete_section(name: str, plan: SeatingPlan = Depends(get_plan)):
	plan.delete_section(name)
	return {}


@router.post("/{name}/clone", response_model=CloneResponse)
def clone_section(name: str, count: int = 1, plan: SeatingPlan = Depends(get_plan)):
	created = plan.clone_section_many(name, count)
	return {"created": created}

@router.patch("/{name}", response_model=SectionOut)
def rename_section(name: str, payload: RenameSection, plan: SeatingPlan = Depends(get_plan)):
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    plan.rename_section(name, payload.new_name)
    return plan.sections[payload.new_name].to_dict()


@router.post("/{name}/rows/{row}/bulk", status_code=201)
def add_bulk_seats(name: str, row: str, payload: BulkSeats, plan: SeatingPlan = Depends(get_plan)):
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    for seat_number in payload.seat_numbers:
        plan.sections[name].add_seat(row, seat_number)
    return {"status": "ok", "count": len(payload.seat_numbers)}


@router.post("/{name}/rows/{row}/range", status_code=201)
def add_seat_range(name: str, row: str, payload: SeatRange, plan: SeatingPlan = Depends(get_plan)):
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    plan.sections[name].add_seat_range(row, payload.start_seat, payload.end_seat)
    return {"status": "ok"}


@router.post("/{name}/rows/range", status_code=201)
def add_row_range(name: str, payload: RowRange, plan: SeatingPlan = Depends(get_plan)):
    """
    Add multiple rows with seat ranges. Supports:
    - start_row, end_row: row range (numeric or letter)
    - start_seat, end_seat: seat range for each row
    - parity: "all", "even", or "odd" (filters seats)
    - continuous: if True, seat numbers continue across rows
    - row_prefix, row_suffix: applied to row labels
    - unnumbered_rows: if True, add '#' prefix to row numbers
    """
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    
    section = plan.sections[name]
    
    # Build rows list (numeric or letter ranges)
    rows_raw = []
    try:
        rs = int(payload.start_row)
        re = int(payload.end_row)
        if rs <= re:
            rows_raw = [str(i) for i in range(rs, re + 1)]
        else:
            rows_raw = [str(i) for i in range(re, rs + 1)]
    except ValueError:
        # letter range
        try:
            si = ascii_uppercase.index(payload.start_row.upper())
            ei = ascii_uppercase.index(payload.end_row.upper())
            if si <= ei:
                rows_raw = list(ascii_uppercase[si:ei+1])
            else:
                rows_raw = list(ascii_uppercase[ei:si+1])
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid row range")
    
    # Apply prefix/suffix
    prefix = payload.row_prefix or ""
    suffix = payload.row_suffix or ""
    if payload.unnumbered_rows:
        rows = [f"#{r}" for r in rows_raw]
    else:
        rows = [f"{prefix}{r}{suffix}" for r in rows_raw]
    
    if not rows:
        raise HTTPException(status_code=400, detail="No rows generated")
    
    # Handle continuous numbering
    parity = (payload.parity or "all").lower()
    continuous = payload.continuous or False
    
    if continuous:
        # Only numeric seat labels support continuous
        try:
            s0 = int(payload.start_seat)
            s1 = int(payload.end_seat)
            seats_per_row = abs(s1 - s0) + 1
            seq = min(s0, s1)
            
            for row in rows:
                for i in range(seats_per_row):
                    seat_label = str(seq)
                    if parity == "all":
                        section.add_seat(row, seat_label)
                    else:
                        val = int(seat_label)
                        keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                        if keep:
                            section.add_seat(row, seat_label)
                    seq += 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Continuous numbering requires numeric seat labels")
    else:
        # Standard: same seat range for each row
        seats = alphanum_range(payload.start_seat, payload.end_seat)
        if not seats:
            try:
                a = int(payload.start_seat)
                b = int(payload.end_seat)
                if a > b:
                    a, b = b, a
                seats = [str(i) for i in range(a, b + 1)]
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid seat range")
        
        if parity == "all":
            for row in rows:
                for seat in seats:
                    section.add_seat(row, seat)
        else:
            for row in rows:
                for seat in seats:
                    if seat.isdigit():
                        val = int(seat)
                        keep = (val % 2 == 0) if parity == "even" else (val % 2 == 1)
                        if keep:
                            section.add_seat(row, seat)
    
    return {"status": "ok", "rows_added": len(rows)}


@router.delete("/{name}/rows/{row}", status_code=204)
def delete_row(name: str, row: str, plan: SeatingPlan = Depends(get_plan)):
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    plan.sections[name].delete_row(row)
    return {}