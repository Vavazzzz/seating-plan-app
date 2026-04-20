"""Application use cases for import/export operations."""

from pathlib import Path
from typing import List, Optional

from infrastructure.import_export import Importer, Exporter
from infrastructure.persistence import SeatingPlanRepository
from domain.models.seating_plan import SeatingPlan
from domain.exceptions import SeatingPlanException


class ImportSeatingPlanUseCase:
    """Use case for importing a seating plan from a file."""
    
    def __init__(self, importers: List[Importer]):
        """Initialize with a list of available importers.
        
        Args:
            importers: List of Importer implementations to try
        """
        if not importers:
            raise ValueError("At least one importer must be provided")
        self.importers = importers
    
    def execute(self, file_path: str, plan_name: Optional[str] = None) -> SeatingPlan:
        """Import a seating plan from a file.
        
        Tries each importer until one claims to support the file type.
        
        Args:
            file_path: Path to the file to import
            plan_name: Optional custom name for the plan (uses filename stem if not provided)
            
        Returns:
            The imported SeatingPlan
            
        Raises:
            SeatingPlanException: If no importer supports the file or import fails
        """
        # Use provided name or derive from filename
        if not plan_name:
            plan_name = Path(file_path).stem
        
        # Find a suitable importer
        for importer in self.importers:
            if importer.supports(file_path):
                return importer.import_seating_plan(file_path, plan_name)
        
        # No supported importer found
        supported = ", ".join([
            importer.SUPPORTED_EXTENSIONS[0] 
            for importer in self.importers
        ])
        raise SeatingPlanException(
            f"No importer available for file: {file_path}\n"
            f"Supported formats: {supported}",
            error_code="UNSUPPORTED_FORMAT"
        )


class ExportSeatingPlanUseCase:
    """Use case for exporting a seating plan to a file."""
    
    def __init__(self, exporters: List[Exporter]):
        """Initialize with a list of available exporters.
        
        Args:
            exporters: List of Exporter implementations to try
        """
        if not exporters:
            raise ValueError("At least one exporter must be provided")
        self.exporters = exporters
    
    def execute(self, seating_plan: SeatingPlan, file_path: str) -> None:
        """Export a seating plan to a file.
        
        Tries each exporter until one claims to support the file type.
        
        Args:
            seating_plan: The SeatingPlan to export
            file_path: Where to save the file
            
        Raises:
            SeatingPlanException: If no exporter supports the file or export fails
        """
        # Find a suitable exporter
        for exporter in self.exporters:
            if exporter.supports(file_path):
                exporter.export_seating_plan(file_path, seating_plan)
                return
        
        # No supported exporter found
        supported = ", ".join([
            exporter.SUPPORTED_EXTENSIONS[0] 
            for exporter in self.exporters
        ])
        raise SeatingPlanException(
            f"No exporter available for file: {file_path}\n"
            f"Supported formats: {supported}",
            error_code="UNSUPPORTED_FORMAT"
        )


class SaveSeatingPlanUseCase:
    """Use case for saving a seating plan using a repository."""
    
    def __init__(self, repository: SeatingPlanRepository):
        """Initialize with a repository.
        
        Args:
            repository: The persistence repository to use
        """
        self.repository = repository
    
    def execute(self, seating_plan: SeatingPlan, file_path: str) -> None:
        """Save a seating plan to a file using the repository.
        
        Args:
            seating_plan: The SeatingPlan to save
            file_path: Where to save the file
            
        Raises:
            SeatingPlanException: If save fails
        """
        self.repository.save(seating_plan, file_path)


class LoadSeatingPlanUseCase:
    """Use case for loading a seating plan using a repository."""
    
    def __init__(self, repository: SeatingPlanRepository):
        """Initialize with a repository.
        
        Args:
            repository: The persistence repository to use
        """
        self.repository = repository
    
    def execute(self, file_path: str) -> SeatingPlan:
        """Load a seating plan from a file using the repository.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            The loaded SeatingPlan
            
        Raises:
            SeatingPlanException: If load fails
        """
        return self.repository.load(file_path)
