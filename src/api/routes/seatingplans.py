import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException

from src.models.seating_plan import SeatingPlan
from src.api.schemas import ProjectName
from src.api.dependencies import get_plan

router = APIRouter()

PROJECTS_DIR = "projects"


def ensure_projects_dir():
    """Ensure projects directory exists."""
    Path(PROJECTS_DIR).mkdir(exist_ok=True)


def get_project_path(name: str) -> str:
    """Get the file path for a project."""
    ensure_projects_dir()
    return os.path.join(PROJECTS_DIR, f"{name}.json")


@router.get("/list")
def list_projects():
    """List all saved projects."""
    ensure_projects_dir()
    projects = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".json"):
            projects.append(filename[:-5])  # Remove .json extension
    return {"projects": projects}


@router.get("/seatingplan/{name}")
def show_seating_plan(name: str):
    """Get the seating plan data for a saved project."""
    path = get_project_path(name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        return {"name": name, "seating_plan": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new/{name}")
def new_project(name: str, plan: SeatingPlan = Depends(get_plan)):
    """Create a new empty seating plan project (clears current plan)."""
    # Reset in-memory plan and set its name
    plan.name = name
    plan.sections = {}
    return {"status": "new", "name": name, "seating_plan": plan.to_dict()}

@router.post("/save")
def save_project(payload: ProjectName, plan: SeatingPlan = Depends(get_plan)):
    """Save the current seating plan to a JSON file."""
    try:
        # Ensure the seating plan's internal name is set before export
        plan.name = payload.name
        plan.export_project(get_project_path(payload.name))
        return {"status": "saved", "name": payload.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load")
def load_project(payload: ProjectName, plan: SeatingPlan = Depends(get_plan)):
    """Load a seating plan from a JSON file (overwrites current plan)."""
    path = get_project_path(payload.name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Project '{payload.name}' not found")
    try:
        plan.import_project(path)
        return {"status": "loaded", "name": payload.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{name}")
def delete_project(name: str):
    """Delete a saved project."""
    path = get_project_path(name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    try:
        os.remove(path)
        return {"status": "deleted", "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
