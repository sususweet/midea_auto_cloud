#!/usr/bin/env python3
"""
Sort translation and icon files alphabetically by key.
"""

import json
import re
from pathlib import Path


PRESERVE_ORDER_KEYS = {"data", "data_description"}

def natural_sort_key(key: str) -> tuple:
    """Generate a sort key that sorts numbers numerically, not lexicographically.

    Splits the string into numeric and non-numeric parts, converting numeric parts
    to integers for proper numerical ordering.
    """
    def try_convert(part):
        try:
            return (0, int(part), "")
        except ValueError:
            return (1, 0, part.lower())

    return tuple(try_convert(part) for part in re.split(r'(\d+)', str(key)))


def sort_dict_recursive(d: dict, parent_key: str = "") -> dict:
    """Sort dictionary recursively, preserving order for value mappings."""
    if not isinstance(d, dict):
        return d

    if parent_key in PRESERVE_ORDER_KEYS:
        return d

    sorted_keys = sorted(d.keys(), key=natural_sort_key)
    result = {}

    for key in sorted_keys:
        value = d[key]
        if isinstance(value, dict):
            result[key] = sort_dict_recursive(value, key)
        else:
            result[key] = value

    return result


def format_icons_json(data: dict) -> str:
    """Format icons.json with compact entity entries."""
    lines = ["{"]
    lines.append('    "entity": {')
    
    entity_types = sorted(data.get("entity", {}).keys(), key=lambda x: str(x).lower())
    
    for i, entity_type in enumerate(entity_types):
        entities = data["entity"][entity_type]
        lines.append(f'        "{entity_type}": {{')
        
        entity_ids = sorted(entities.keys(), key=lambda x: str(x).lower())
        for j, entity_id in enumerate(entity_ids):
            entity_data = entities[entity_id]
            icon = entity_data.get("default", "")
            comma = "," if j < len(entity_ids) - 1 else ""
            lines.append(f'            "{entity_id}": {{ "default": "{icon}" }}{comma}')
        
        comma = "," if i < len(entity_types) - 1 else ""
        lines.append(f'        }}{comma}')
    
    lines.append("    }")
    lines.append("}")
    
    return "\n".join(lines)


def main():
    base_path = Path(__file__).parent.parent / "custom_components" / "midea_smart_home"
    translations_path = base_path / "translations"
    icons_path = base_path / "icons.json"
    
    en_file = translations_path / "en.json"
    zh_file = translations_path / "zh-Hans.json"
    
    print("Sorting English translation file...")
    with open(en_file, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    sorted_en = sort_dict_recursive(en_data)
    with open(en_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted_en, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  Saved: {en_file}")
    
    print("Sorting Chinese translation file...")
    with open(zh_file, "r", encoding="utf-8") as f:
        zh_data = json.load(f)
    sorted_zh = sort_dict_recursive(zh_data)
    with open(zh_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted_zh, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  Saved: {zh_file}")
    
    print("Sorting icons file...")
    with open(icons_path, "r", encoding="utf-8") as f:
        icons_data = json.load(f)
    sorted_icons = sort_dict_recursive(icons_data)
    formatted = format_icons_json(sorted_icons)
    with open(icons_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(formatted)
        f.write("\n")
    print(f"  Saved: {icons_path}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
