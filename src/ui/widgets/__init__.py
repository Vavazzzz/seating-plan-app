"""UI widget modules for seating plan application."""

from .base import BasePanel
from .sections_panel import SectionsPanel

# Keep legacy widget for backward compatibility
try:
    from .section_table import SectionTableWidget
except ImportError:
    SectionTableWidget = None

__all__ = [
    "BasePanel",
    "SectionsPanel",
    "SectionTableWidget",
]
