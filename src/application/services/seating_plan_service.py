"""Service for seating plan-level operations."""

from typing import List, Optional
from pathlib import Path
from .base import BaseService
from .section_service import SectionService
from ..result import Result, ValidationErrors
from ..use_cases import (
    ImportSeatingPlanUseCase,
    ExportSeatingPlanUseCase,
    SaveSeatingPlanUseCase,
    LoadSeatingPlanUseCase,
)
from ...domain.models.seating_plan import SeatingPlan
from ...domain.exceptions import SeatingPlanException


class SeatingPlanService(BaseService):
    """High-level service for seating plan operations.
    
    Coordinates file I/O, validation, and provides section service.
    """
    
    def __init__(self, seating_plan: SeatingPlan, command_handler, use_cases_config=None):
        """Initialize the service.
        
        Args:
            seating_plan: The seating plan to operate on
            command_handler: Handler for undo/redo operations
            use_cases_config: Optional dict with 'importers', 'exporters', 'repository'
        """
        super().__init__(seating_plan, command_handler)
        self.use_cases_config = use_cases_config or {}
        self._section_service: Optional[SectionService] = None
    
    def get_section_service(self) -> SectionService:
        """Get the section service for this plan.
        
        Returns:
            SectionService instance for coordinated section operations
        """
        if self._section_service is None:
            self._section_service = SectionService(self.seating_plan, self.command_handler)
        return self._section_service
    
    def create_new_plan(self, plan_name: str) -> Result[None, ValidationErrors]:
        """Create a clean new seating plan.
        
        Args:
            plan_name: Name for the new plan
            
        Returns:
            Result indicating success or validation errors
        """
        self.clear_validation_errors()
        
        # Validation
        if not plan_name or not plan_name.strip():
            self.validate(False, "Plan name cannot be empty")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            # Clear existing sections (but don't use commands for this operation)
            self.seating_plan.sections.clear()
            self.seating_plan.name = plan_name
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Failed to create new plan: {str(e)}")
            return Result.failure(errors)
    
    def import_seating_plan(
        self,
        file_path: str,
        plan_name: Optional[str] = None,
    ) -> Result[None, ValidationErrors]:
        """Import a seating plan from a file.
        
        Args:
            file_path: Path to file to import
            plan_name: Optional custom name (uses filename stem if not provided)
            
        Returns:
            Result indicating success or validation errors
        """
        self.clear_validation_errors()
        
        # Validation
        if not file_path or not file_path.strip():
            self.validate(False, "File path cannot be empty")
        elif not Path(file_path).exists():
            self.validate(False, f"File not found: {file_path}")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            importers = self.use_cases_config.get("importers")
            if not importers:
                raise ValueError("No importers configured")
            
            use_case = ImportSeatingPlanUseCase(importers)
            imported_plan = use_case.execute(file_path, plan_name)
            
            # Replace current plan with imported one
            self.seating_plan.sections.clear()
            self.seating_plan.sections.update(imported_plan.sections)
            self.seating_plan.name = imported_plan.name
            
            return Result.success(None)
        except SeatingPlanException as e:
            errors = ValidationErrors()
            errors.add(f"Import failed: {str(e)}")
            return Result.failure(errors)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Unexpected error during import: {str(e)}")
            return Result.failure(errors)
    
    def export_seating_plan(
        self,
        file_path: str,
        format_type: Optional[str] = None,
    ) -> Result[None, ValidationErrors]:
        """Export the seating plan to a file.
        
        Args:
            file_path: Path where file should be saved
            format_type: Optional format type (auto-detected from extension if not provided)
            
        Returns:
            Result indicating success or validation errors
        """
        self.clear_validation_errors()
        
        # Validation
        if not file_path or not file_path.strip():
            self.validate(False, "File path cannot be empty")
        
        # Check directory exists
        target_dir = Path(file_path).parent
        if not target_dir.exists():
            self.validate(False, f"Target directory does not exist: {target_dir}")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            exporters = self.use_cases_config.get("exporters")
            if not exporters:
                raise ValueError("No exporters configured")
            
            use_case = ExportSeatingPlanUseCase(exporters)
            use_case.execute(self.seating_plan, file_path)
            
            return Result.success(None)
        except SeatingPlanException as e:
            errors = ValidationErrors()
            errors.add(f"Export failed: {str(e)}")
            return Result.failure(errors)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Unexpected error during export: {str(e)}")
            return Result.failure(errors)
    
    def save_seating_plan(self, file_path: str) -> Result[None, ValidationErrors]:
        """Save the current seating plan to a JSON file.
        
        Args:
            file_path: Path where file should be saved
            
        Returns:
            Result indicating success or validation errors
        """
        self.clear_validation_errors()
        
        # Validation
        if not file_path or not file_path.strip():
            self.validate(False, "File path cannot be empty")
        
        target_dir = Path(file_path).parent
        if not target_dir.exists():
            self.validate(False, f"Target directory does not exist: {target_dir}")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            repository = self.use_cases_config.get("repository")
            if not repository:
                raise ValueError("No repository configured")
            
            use_case = SaveSeatingPlanUseCase(repository)
            use_case.execute(self.seating_plan, file_path)
            
            return Result.success(None)
        except SeatingPlanException as e:
            errors = ValidationErrors()
            errors.add(f"Save failed: {str(e)}")
            return Result.failure(errors)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Unexpected error during save: {str(e)}")
            return Result.failure(errors)
    
    def load_seating_plan(self, file_path: str) -> Result[None, ValidationErrors]:
        """Load a seating plan from a JSON file.
        
        Args:
            file_path: Path to file to load
            
        Returns:
            Result indicating success or validation errors
        """
        self.clear_validation_errors()
        
        # Validation
        if not file_path or not file_path.strip():
            self.validate(False, "File path cannot be empty")
        elif not Path(file_path).exists():
            self.validate(False, f"File not found: {file_path}")
        
        if self.has_validation_errors():
            return Result.failure(self.get_validation_errors())
        
        try:
            repository = self.use_cases_config.get("repository")
            if not repository:
                raise ValueError("No repository configured")
            
            use_case = LoadSeatingPlanUseCase(repository)
            loaded_plan = use_case.execute(file_path)
            
            # Replace current plan with loaded one
            self.seating_plan.sections.clear()
            self.seating_plan.sections.update(loaded_plan.sections)
            self.seating_plan.name = loaded_plan.name
            
            return Result.success(None)
        except SeatingPlanException as e:
            errors = ValidationErrors()
            errors.add(f"Load failed: {str(e)}")
            return Result.failure(errors)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Unexpected error during load: {str(e)}")
            return Result.failure(errors)
    
    def get_plan_info(self) -> dict:
        """Get information about the current seating plan.
        
        Returns:
            Dictionary with plan metadata
        """
        total_seats = sum(
            len(section.seats) for section in self.seating_plan.sections.values()
        )
        
        return {
            "name": self.seating_plan.name,
            "sections": len(self.seating_plan.sections),
            "total_seats": total_seats,
            "can_undo": self.command_handler.can_undo(),
            "can_redo": self.command_handler.can_redo(),
            "history_size": len(self.command_handler.undo_stack),
        }
    
    def undo(self) -> Result[None, ValidationErrors]:
        """Undo the last operation.
        
        Returns:
            Result indicating success or validation errors
        """
        try:
            if not self.command_handler.can_undo():
                errors = ValidationErrors()
                errors.add("No operations to undo")
                return Result.failure(errors)
            
            self.command_handler.undo()
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Undo failed: {str(e)}")
            return Result.failure(errors)
    
    def redo(self) -> Result[None, ValidationErrors]:
        """Redo the last undone operation.
        
        Returns:
            Result indicating success or validation errors
        """
        try:
            if not self.command_handler.can_redo():
                errors = ValidationErrors()
                errors.add("No operations to redo")
                return Result.failure(errors)
            
            self.command_handler.redo()
            return Result.success(None)
        except Exception as e:
            errors = ValidationErrors()
            errors.add(f"Redo failed: {str(e)}")
            return Result.failure(errors)
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.command_handler.can_undo()
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.command_handler.can_redo()
    
    def get_undo_description(self) -> str:
        """Get description of next undo operation."""
        return self.command_handler.get_undo_description()
    
    def get_redo_description(self) -> str:
        """Get description of next redo operation."""
        return self.command_handler.get_redo_description()
