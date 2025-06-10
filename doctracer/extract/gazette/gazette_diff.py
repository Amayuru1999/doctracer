import json
from collections import defaultdict

def load_gazette(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

def index_by_name(ministries):
    return {m["name"]: m for m in ministries}

def compare_gazettes(old_data, new_data):
    old_min = index_by_name(old_data)
    new_min = index_by_name(new_data)

    changes = defaultdict(list)

    all_min_names = set(old_min.keys()).union(new_min.keys())

    for name in all_min_names:
        old = old_min.get(name)
        new = new_min.get(name)

        if not old:
            changes["ADD_MINISTRY"].append(name)
            continue
        if not new:
            changes["REMOVE_MINISTRY"].append(name)
            continue

        # Compare departments
        old_deps = set(old["departments"])
        new_deps = set(new["departments"])

        for dep in old_deps - new_deps:
            changes["REMOVED_DEPARTMENTS"].append({"ministry": name, "department": dep})
        for dep in new_deps - old_deps:
            changes["ADDED_DEPARTMENTS"].append({"ministry": name, "department": dep})

        # Compare laws
        old_laws = set(old["laws"])
        new_laws = set(new["laws"])

        for law in old_laws - new_laws:
            changes["REMOVED_LAWS"].append({"ministry": name, "law": law})
        for law in new_laws - old_laws:
            changes["ADDED_LAWS"].append({"ministry": name, "law": law})

    return changes

def save_diff(changes, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(changes, f, indent=2)
