"""UI dialog modules for seating plan application."""

from .base import InputDialog, CheckboxDialog
from .section_dialogs import (
    AddSectionDialog,
    RenameSectionDialog,
    MergeSectionsDialog,
    CloneSectionDialog,
    CloneSectionManyDialog,
)
from .seat_dialogs import (
    NewPlanDialog,
    RangeInputDialog,
    AddCustomRowsDialog,
    RenumberRowsDialog,
    FileDialog,
)

__all__ = [
    "InputDialog",
    "CheckboxDialog",
    "AddSectionDialog",
    "RenameSectionDialog",
    "MergeSectionsDialog",
    "CloneSectionDialog",
    "CloneSectionManyDialog",
    "NewPlanDialog",
    "RangeInputDialog",
    "AddCustomRowsDialog",
    "RenumberRowsDialog",
    "FileDialog",
]
