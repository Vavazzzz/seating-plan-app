"""Dialog for merging sections."""

from PyQt6.QtWidgets import QInputDialog, QMessageBox


def show_merge_sections_dialog(parent, existing_sections):
    """Show dialog for merging sections.
    
    Args:
        parent: Parent widget
        existing_sections: Set or list of existing section names
        
    Returns:
        Tuple of (new_name,) or (None,) if cancelled
    """
    new_name, ok = QInputDialog.getText(
        parent,
        "Merge Sections",
        "New section name:"
    )
    
    if not ok or not new_name:
        return None,
    
    new_name = new_name.strip()
    
    if new_name in existing_sections:
        QMessageBox.warning(parent, "Exists", "Section with that name already exists.")
        return show_merge_sections_dialog(parent, existing_sections)
    
    return new_name,
