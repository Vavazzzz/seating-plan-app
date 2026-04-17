"""Dialog for cloning a section."""

from PyQt6.QtWidgets import QInputDialog, QMessageBox


def show_clone_section_dialog(parent, existing_sections):
    """Show dialog for cloning a section.
    
    Args:
        parent: Parent widget
        existing_sections: Set or list of existing section names
        
    Returns:
        Tuple of (target_name,) or (None,) if cancelled
    """
    target_name, ok = QInputDialog.getText(
        parent,
        "Clone Section",
        "New section name:"
    )
    
    if not ok or not target_name:
        return None,
    
    target_name = target_name.strip()
    
    if target_name in existing_sections:
        QMessageBox.warning(parent, "Exists", "Section with that name already exists.")
        return show_clone_section_dialog(parent, existing_sections)
    
    return target_name,
