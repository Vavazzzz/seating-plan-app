"""Dialog for renaming a section."""

from PyQt6.QtWidgets import QInputDialog, QMessageBox


def show_rename_section_dialog(parent, old_name, existing_sections):
    """Show dialog for renaming a section.
    
    Args:
        parent: Parent widget
        old_name: Current section name
        existing_sections: Set or list of existing section names (excluding old_name)
        
    Returns:
        Tuple of (new_name,) or (None,) if cancelled
    """
    new_name, ok = QInputDialog.getText(
        parent,
        "Rename Section",
        "New name:",
        text=old_name
    )
    
    if not ok or not new_name or new_name == old_name:
        return None,
    
    new_name = new_name.strip()
    
    if new_name in existing_sections:
        QMessageBox.warning(parent, "Exists", "Section with that name already exists.")
        return show_rename_section_dialog(parent, old_name, existing_sections)
    
    return new_name,
