from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.seating_plan import SeatingPlan
from .routes import sections, seats, projects
from .dependencies import init_plan

app = FastAPI(title="Seating Plan API")

# Allow local frontend during development
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Global in-memory seating plan instance for this process
seating_plan = SeatingPlan()

# initialize dependency module with our global instance
init_plan(seating_plan)


app.include_router(sections.router, prefix="/api/sections", tags=["sections"], dependencies=[],)
app.include_router(seats.router, prefix="/api/seats", tags=["seats"], dependencies=[],)
app.include_router(projects.router, prefix="/api/projects", tags=["projects"], dependencies=[],)


@app.get("/", tags=["root"])
def root():
	return {"status": "ok", "message": "Seating Plan API"}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

