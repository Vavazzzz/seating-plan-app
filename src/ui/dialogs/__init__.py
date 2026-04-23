"""UI dialog modules for seating plan application."""

from .base import InputDialog, CheckboxDialog
from .section_dialogs import (
    AddSectionDialog,
    RenameSectionDialog,
    MergeSectionsDialog,
    CloneSectionDialog,
)
from .seat_dialogs import (
    AddSeatDialog,
    AddSeatRangeDialog,
    NewPlanDialog,
    FileDialog,
)

__all__ = [
    "InputDialog",
    "CheckboxDialog",
    "AddSectionDialog",
    "RenameSectionDialog",
    "MergeSectionsDialog",
    "CloneSectionDialog",
    "AddSeatDialog",
    "AddSeatRangeDialog",
    "NewPlanDialog",
    "FileDialog",
]
