from typing import Callable

from src.models.seating_plan import SeatingPlan


# Dependency provider for the global SeatingPlan instance.
# We keep the instance on module-level here and provide an injector
# so routes don't need to import `main`, avoiding circular imports.
_plan: SeatingPlan | None = None


def init_plan(plan: SeatingPlan) -> None:
	global _plan
	_plan = plan


def get_plan() -> SeatingPlan:
	if _plan is None:
		raise RuntimeError("SeatingPlan has not been initialized. Call init_plan() during app startup.")
	return _plan

