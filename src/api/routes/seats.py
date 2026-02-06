from fastapi import APIRouter, Depends, HTTPException

from src.models.seating_plan import SeatingPlan
from src.api.schemas import SeatIn
from src.api.dependencies import get_plan

router = APIRouter()


@router.get("/{section}")
def list_seats(section: str, plan: SeatingPlan = Depends(get_plan)):
	if section not in plan.sections:
		raise HTTPException(status_code=404, detail="Section not found")
	return plan.sections[section].to_dict()


@router.post("/{section}/{row}", status_code=201)
def add_seat(section: str, row: str, payload: SeatIn, plan: SeatingPlan = Depends(get_plan)):
	if section not in plan.sections:
		raise HTTPException(status_code=404, detail="Section not found")
	plan.sections[section].add_seat(row, payload.seat_number)
	return {"status": "ok"}


@router.delete("/{section}/{row}/{seat}", status_code=204)
def delete_seat(section: str, row: str, seat: str, plan: SeatingPlan = Depends(get_plan)):
	if section not in plan.sections:
		raise HTTPException(status_code=404, detail="Section not found")
	plan.sections[section].delete_seat(row, seat)
	return {}

