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


@router.post("/save")
def save_project(payload: ProjectName, plan: SeatingPlan = Depends(get_plan)):
    """Save the current seating plan to a JSON file."""
    try:
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


@router.get("/list")
def list_projects():
    """List all saved projects."""
    ensure_projects_dir()
    projects = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".json"):
            projects.append(filename[:-5])  # Remove .json extension
    return {"projects": projects}


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
