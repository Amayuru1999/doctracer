import json
from collections import defaultdict

def load_gazette(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

def index_by_ministry_name(ministries):
    return {m["name"]: m for m in ministries}

def compare_gazettes(old_data, new_data):
    old_min = index_by_ministry_name(old_data)
    new_min = index_by_ministry_name(new_data)

    changes = defaultdict(list)
    all_ministries = set(old_min.keys()).union(new_min.keys())

    for name in all_ministries:
        old = old_min.get(name)
        new = new_min.get(name)

        if not old:
            changes["ADDED_MINISTRIES"].append(name)
            continue
        if not new:
            changes["REMOVED_MINISTRIES"].append(name)
            continue

        # Compare departments
        old_deps = set(old.get("departments", []))
        new_deps = set(new.get("departments", []))

        for dep in old_deps - new_deps:
            changes["REMOVED_DEPARTMENTS"].append({"ministry": name, "department": dep})
        for dep in new_deps - old_deps:
            changes["ADDED_DEPARTMENTS"].append({"ministry": name, "department": dep})

        # Compare laws
        old_laws = set(old.get("laws", []))
        new_laws = set(new.get("laws", []))

        for law in old_laws - new_laws:
            changes["REMOVED_LAWS"].append({"ministry": name, "law": law})
        for law in new_laws - old_laws:
            changes["ADDED_LAWS"].append({"ministry": name, "law": law})

    return dict(changes)

def save_diff(changes, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(changes, f, indent=2)
