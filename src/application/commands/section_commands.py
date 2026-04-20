"""Commands for section-level operations."""

import copy
from typing import List, Optional

from domain.models.seating_plan import SeatingPlan
from domain.models.section import Section
from domain.exceptions import MergeConflictError, ValidationError
from .base import Command


class AddSectionCommand(Command):
    """Command to add a new section to a seating plan."""
    
    def __init__(self, seating_plan: SeatingPlan, section_name: str, is_ga: bool = False):
        """Initialize add section command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            section_name: Name for the new section
            is_ga: Whether this is general admission
        """
        super().__init__(f"Add section '{section_name}'")
        self.seating_plan = seating_plan
        self.section_name = section_name
        self.is_ga = is_ga
    
    def execute(self) -> None:
        """Add the section."""
        if self.section_name in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.section_name}' already exists")
        
        self.seating_plan.add_section(self.section_name, is_ga=self.is_ga)
        self._executed = True
    
    def undo(self) -> None:
        """Remove the section."""
        self.seating_plan.delete_section(self.section_name)


class DeleteSectionCommand(Command):
    """Command to delete a section from a seating plan."""
    
    def __init__(self, seating_plan: SeatingPlan, section_name: str):
        """Initialize delete section command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            section_name: Name of section to delete
        """
        super().__init__(f"Delete section '{section_name}'")
        self.seating_plan = seating_plan
        self.section_name = section_name
        self._saved_section: Optional[Section] = None
    
    def execute(self) -> None:
        """Delete the section."""
        if self.section_name not in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.section_name}' not found")
        
        # Save section for undo
        self._saved_section = copy.deepcopy(
            self.seating_plan.sections[self.section_name]
        )
        self.seating_plan.delete_section(self.section_name)
        self._executed = True
    
    def undo(self) -> None:
        """Restore the section."""
        if self._saved_section:
            self.seating_plan.sections[self.section_name] = self._saved_section


class RenameSectionCommand(Command):
    """Command to rename a section."""
    
    def __init__(self, seating_plan: SeatingPlan, old_name: str, new_name: str):
        """Initialize rename section command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            old_name: Current section name
            new_name: New section name
        """
        super().__init__(f"Rename section '{old_name}' to '{new_name}'")
        self.seating_plan = seating_plan
        self.old_name = old_name
        self.new_name = new_name
    
    def execute(self) -> None:
        """Rename the section."""
        if self.old_name not in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.old_name}' not found")
        if self.new_name in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.new_name}' already exists")
        
        self.seating_plan.rename_section(self.old_name, self.new_name)
        self._executed = True
    
    def undo(self) -> None:
        """Restore original name."""
        self.seating_plan.rename_section(self.new_name, self.old_name)


class CloneSectionCommand(Command):
    """Command to clone a section."""
    
    def __init__(self, seating_plan: SeatingPlan, source_name: str, clone_name: str):
        """Initialize clone section command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            source_name: Section to clone from
            clone_name: Name for cloned section
        """
        super().__init__(f"Clone section '{source_name}' to '{clone_name}'")
        self.seating_plan = seating_plan
        self.source_name = source_name
        self.clone_name = clone_name
    
    def execute(self) -> None:
        """Clone the section."""
        if self.source_name not in self.seating_plan.sections:
            raise ValidationError(f"Source section '{self.source_name}' not found")
        if self.clone_name in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.clone_name}' already exists")
        
        self.seating_plan.clone_section(self.source_name, self.clone_name)
        self._executed = True
    
    def undo(self) -> None:
        """Delete the cloned section."""
        self.seating_plan.delete_section(self.clone_name)


class CloneSectionManyCommand(Command):
    """Command to clone a section multiple times with auto-generated names."""
    
    def __init__(self, seating_plan: SeatingPlan, source_name: str, count: int):
        """Initialize clone multiple command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            source_name: Section to clone
            count: Number of clones to create
        """
        super().__init__(f"Clone section '{source_name}' {count} times")
        self.seating_plan = seating_plan
        self.source_name = source_name
        self.count = count
        self._created_names: List[str] = []
    
    def execute(self) -> None:
        """Clone the section multiple times with auto-generated names."""
        if self.source_name not in self.seating_plan.sections:
            raise ValidationError(f"Section '{self.source_name}' not found")
        
        # Use the domain model's clone_section_many method
        self._created_names = self.seating_plan.clone_section_many(
            self.source_name,
            self.count
        )
        self._executed = True
    
    def undo(self) -> None:
        """Delete all created clones."""
        for name in self._created_names:
            self.seating_plan.delete_section(name)


class MergeSectionsCommand(Command):
    """Command to merge multiple sections."""
    
    def __init__(
        self, 
        seating_plan: SeatingPlan, 
        source_names: List[str], 
        target_name: str,
        delete_sources: bool = True,
    ):
        """Initialize merge sections command.
        
        Args:
            seating_plan: The SeatingPlan to modify
            source_names: Sections to merge
            target_name: Name for merged section
            delete_sources: Whether to delete source sections after merge
        """
        super().__init__(
            f"Merge sections {source_names} into '{target_name}'"
        )
        self.seating_plan = seating_plan
        self.source_names = source_names
        self.target_name = target_name
        self.delete_sources = delete_sources
        self._saved_sections: dict = {}
        self._target_saved: Optional[Section] = None
    
    def execute(self) -> None:
        """Merge the sections."""
        if len(self.source_names) < 2:
            raise ValidationError("At least 2 sections required for merge")
        
        # Check if target exists and save it if it does
        if self.target_name in self.seating_plan.sections:
            self._target_saved = copy.deepcopy(
                self.seating_plan.sections[self.target_name]
            )
        
        # Save sources for undo
        for name in self.source_names:
            if name not in self.seating_plan.sections:
                raise ValidationError(f"Source section '{name}' not found")
            self._saved_sections[name] = copy.deepcopy(
                self.seating_plan.sections[name]
            )
        
        try:
            self.seating_plan.merge_sections(self.source_names, self.target_name)
            
            # Delete sources if requested
            if self.delete_sources:
                for name in self.source_names:
                    if name in self.seating_plan.sections:
                        self.seating_plan.delete_section(name)
        except MergeConflictError as e:
            raise ValidationError(f"Cannot merge: {str(e)}") from e
        
        self._executed = True
    
    def undo(self) -> None:
        """Restore merged sections and remove merged result."""
        # Delete the target section (or restore it if it existed before)
        if self._target_saved is not None:
            # Target existed before - restore it
            self.seating_plan.sections[self.target_name] = self._target_saved
        else:
            # Target was created by merge - delete it
            if self.target_name in self.seating_plan.sections:
                self.seating_plan.delete_section(self.target_name)
        
        # Restore original source sections
        for name, section in self._saved_sections.items():
            self.seating_plan.sections[name] = section
