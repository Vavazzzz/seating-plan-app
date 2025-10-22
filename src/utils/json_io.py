from typing import Any, Dict
import json

def export_to_json(data: Dict[str, Any], filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def import_from_json(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        return json.load(f)