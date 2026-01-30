from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.models.seating_plan import SeatingPlan
from src.models.section import Section
from src.api.schemas import SectionCreate, SectionOut, CloneResponse, BulkSeats, SeatRange, RenameSection

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


@router.delete("/{name}/rows/{row}", status_code=204)
def delete_row(name: str, row: str, plan: SeatingPlan = Depends(get_plan)):
    if name not in plan.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    plan.sections[name].delete_row(row)
    return {}