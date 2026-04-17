"""Service for section-level operations."""

from typing import List, Optional
from .base import BaseService
from ..result import Result, ValidationErrors
from ..commands.section_commands import (
    AddSectionCommand,
    DeleteSectionCommand, 
    RenameSectionCommand,
    CloneSectionCommand,
    CloneSectionManyCommand,
    MergeSectionsCommand,
)
from ...domain.exceptions import (
    DuplicateNameError,
    SectionNotFoundError,
    MergeConflictError,
    ValidationError as DomainValidationError,
)


class SectionService(BaseService):
    """High-level service for section operations.
    
    Provides validated, undo-enabled operations on sections.
    All operations return Result types for error handling.
    """
    
    def add_section(
        self,
        name: str,
        is_ga: bool = False,
    ) -> Result[str, ValidationErrors]:
        """Add a new section to the seating plan.
        
        Args:
            name: Section name (must be unique)
            is_ga: Whether this is a general admission section
            
        Returns:
            Result with section name on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not name or not name.strip():
            self.validate(False, "Section name cannot be empty")
        elif name in self.seating_plan.sections:
            self.validate(False, f"Section '{name}' already exists")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            # Create and execute command
            cmd = AddSectionCommand(self.seating_plan, name, is_ga)
            self.command_handler.execute(cmd)
            return Result.success(name)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to add section: {str(e)}")
            return Result.failure(errors)
    
    def delete_section(self, name: str) -> Result[None, ValidationErrors]:
        """Delete a section from the seating plan.
        
        Args:
            name: Name of section to delete
            
        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not name or not name.strip():
            self.validate(False, "Section name cannot be empty")
        elif name not in self.seating_plan.sections:
            self.validate(False, f"Section '{name}' not found")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            cmd = DeleteSectionCommand(self.seating_plan, name)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to delete section: {str(e)}")
            return Result.failure(errors)
    
    def rename_section(self, old_name: str, new_name: str) -> Result[None, ValidationErrors]:
        """Rename a section.
        
        Args:
            old_name: Current section name
            new_name: New section name
            
        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not old_name or not old_name.strip():
            self.validate(False, "Old section name cannot be empty")
        elif not new_name or not new_name.strip():
            self.validate(False, "New section name cannot be empty")
        elif old_name not in self.seating_plan.sections:
            self.validate(False, f"Section '{old_name}' not found")
        elif new_name in self.seating_plan.sections:
            self.validate(False, f"Section '{new_name}' already exists")
        elif old_name == new_name:
            self.validate(False, "New name must be different from current name")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            cmd = RenameSectionCommand(self.seating_plan, old_name, new_name)
            self.command_handler.execute(cmd)
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to rename section: {str(e)}")
            return Result.failure(errors)
    
    def clone_section(
        self,
        source_name: str,
        target_name: str,
    ) -> Result[str, ValidationErrors]:
        """Clone an existing section.
        
        Args:
            source_name: Name of section to clone from
            target_name: Name for the new cloned section
            
        Returns:
            Result with new section name on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not source_name or not source_name.strip():
            self.validate(False, "Source section name cannot be empty")
        elif not target_name or not target_name.strip():
            self.validate(False, "Target section name cannot be empty")
        elif source_name not in self.seating_plan.sections:
            self.validate(False, f"Source section '{source_name}' not found")
        elif target_name in self.seating_plan.sections:
            self.validate(False, f"Target section '{target_name}' already exists")
        elif source_name == target_name:
            self.validate(False, "Target name must be different from source")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            cmd = CloneSectionCommand(self.seating_plan, source_name, target_name)
            self.command_handler.execute(cmd)
            return Result.success(target_name)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to clone section: {str(e)}")
            return Result.failure(errors)
    
    def clone_section_many(
        self,
        source_name: str,
        count: int,
    ) -> Result[List[str], ValidationErrors]:
        """Clone a section multiple times.
        
        Args:
            source_name: Name of section to clone from
            count: Number of clones to create
            
        Returns:
            Result with list of new section names on success
        """
        self.clear_validation_errors()
        
        # Validation
        if not source_name or not source_name.strip():
            self.validate(False, "Source section name cannot be empty")
        elif source_name not in self.seating_plan.sections:
            self.validate(False, f"Source section '{source_name}' not found")
        elif count <= 0:
            self.validate(False, "Clone count must be positive")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            cmd = CloneSectionManyCommand(self.seating_plan, source_name, count)
            self.command_handler.execute(cmd)
            # The command stores the created names internally, retrieve them
            return Result.success(cmd._created_names)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to clone sections: {str(e)}")
            return Result.failure(errors)
    
    def merge_sections(
        self,
        source_names: List[str],
        target_name: str,
        delete_sources: bool = True,
    ) -> Result[None, ValidationErrors]:
        """Merge multiple sections into one.
        
        Args:
            source_names: Names of sections to merge from
            target_name: Name of section to merge into
            delete_sources: Whether to delete source sections after merging
            
        Returns:
            Result.success() on success, validation errors on failure
        """
        self.clear_validation_errors()
        
        # Validation
        if not source_names:
            self.validate(False, "At least one source section must be provided")
        elif not target_name or not target_name.strip():
            self.validate(False, "Target section name cannot be empty")
        elif target_name not in self.seating_plan.sections:
            self.validate(False, f"Target section '{target_name}' not found")
        
        # Check all source sections exist
        for name in source_names or []:
            if name not in self.seating_plan.sections:
                self.validate(False, f"Source section '{name}' not found")
            elif name == target_name and delete_sources:
                self.validate(False, f"Cannot merge section into itself and delete source")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            cmd = MergeSectionsCommand(
                self.seating_plan,
                source_names,
                target_name,
                delete_sources,
            )
            self.command_handler.execute(cmd)
            return Result.success(None)
        except MergeConflictError as e:
            errors = ValidationErrors()
            errors.add(f"Merge conflict: {str(e)}")
            return Result.failure(errors)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to merge sections: {str(e)}")
            return Result.failure(errors)
    
    def get_section_names(self) -> List[str]:
        """Get all section names in the seating plan.
        
        Returns:
            List of section names, sorted alphabetically
        """
        return sorted(self.seating_plan.sections.keys())
    
    def section_exists(self, name: str) -> bool:
        """Check if a section exists.
        
        Args:
            name: Section name to check
            
        Returns:
            True if section exists, False otherwise
        """
        return name in self.seating_plan.sections
