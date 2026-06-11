"""Application layer - commands, handlers, use cases, and services."""

from .result import Result, ValidationErrors
from .commands import (
    Command,
    AddSectionCommand,
    DeleteSectionCommand,
    RenameSectionCommand,
    CloneSectionCommand,
    CloneSectionManyCommand,
    MergeSectionsCommand,
    DeleteRowCommand,
    DeleteSeatsCommand,
    AddRowsCommand,
    MoveSeatsCommand,
    RenumberRowsCommand,
)
from .handlers import CommandHandler
from .use_cases import (
    ImportSeatingPlanUseCase,
    ExportSeatingPlanUseCase,
    SaveSeatingPlanUseCase,
    LoadSeatingPlanUseCase,
)
from .services import (
    BaseService,
    SeatingPlanService,
    SectionService,
    SeatService,
)

__all__ = [
    "Result",
    "ValidationErrors",
    "Command",
    "AddSectionCommand",
    "DeleteSectionCommand",
    "RenameSectionCommand",
    "CloneSectionCommand",
    "CloneSectionManyCommand",
    "MergeSectionsCommand",
    "DeleteRowCommand",
    "DeleteSeatsCommand",
    "AddRowsCommand",
    "MoveSeatsCommand",
    "RenumberRowsCommand",
    "CommandHandler",
    "ImportSeatingPlanUseCase",
    "ExportSeatingPlanUseCase",
    "SaveSeatingPlanUseCase",
    "LoadSeatingPlanUseCase",
    "BaseService",
    "SeatingPlanService",
    "SectionService",
    "SeatService",
]
