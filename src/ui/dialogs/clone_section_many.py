"""Dialog for cloning a section multiple times."""

from PyQt6.QtWidgets import QInputDialog


def show_clone_section_many_dialog(parent):
    """Show dialog for cloning a section multiple times.
    
    Args:
        parent: Parent widget
        
    Returns:
        Tuple of (count,) or (None,) if cancelled
    """
    count, ok = QInputDialog.getInt(
        parent,
        "Clone Section Multiple",
        "Number of clones to create:",
        1,
        1,
        500
    )
    
    if not ok or count <= 0:
        return None,
    
    return count,
