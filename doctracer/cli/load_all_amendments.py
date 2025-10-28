# doctracer/cli/load_all_amendments.py
import os
import json
import argparse
from amendment_to_neo4j import load_amendment_data

def find_base_file_for_amendment(amendment_path: str, base_dir: str):
    """
    Given an amendment JSON path and a base directory, read the amendment's
    parent_gazette.gazette_id and search base_dir for a JSON file that either:
      - contains a matching "gazette_id" field in file content, or
      - has the parent id in its filename.
    Returns the matching base file path or None if not found.
    """
    # safe read amendment JSON to get parent id
    try:
        with open(amendment_path, "r", encoding="utf-8") as f:
            adm = json.load(f)
    except Exception as e:
        print(f"⚠️ Could not read amendment file {amendment_path}: {e}")
        return None

    parent_id = None
    # try multiple locations for parent id (be tolerant)
    parent = adm.get("parent_gazette") or adm.get("parent") or adm.get("metadata", {}).get("parent_gazette")
    if isinstance(parent, dict):
        parent_id = parent.get("gazette_id")
    elif isinstance(parent, str):
        parent_id = parent
    # last fallback in metadata keys
    if not parent_id:
        parent_id = adm.get("metadata", {}).get("parent") or adm.get("parent_gazette", {}).get("gazette_id")

    if not parent_id:
        # no parent id available
        return None

    pid_safe = str(parent_id).replace("/", "-")

    # search base_dir recursively
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.lower().endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            # quick filename match
            if pid_safe in fname or str(parent_id) in fname:
                return fpath
            # otherwise inspect file content (fast fail on unreadable)
            try:
                with open(fpath, "r", encoding="utf-8") as bf:
                    bdata = json.load(bf)
                # try expected keys where gazette_id might live
                file_gzid = bdata.get("gazette_id") or bdata.get("metadata", {}).get("gazette_id")
                if file_gzid and str(file_gzid) == str(parent_id):
                    return fpath
            except Exception:
                # ignore malformed files
                continue

    return None


def load_all_amendments(amendments_dir: str, base_dir: str | None = None):
    """
    Recursively load all amendment JSONs under `amendments_dir`.
    If base_dir is provided and is a directory, attempt to find the matching base file
    for each amendment and pass that file to load_amendment_data.
    """
    if not os.path.exists(amendments_dir):
        raise FileNotFoundError(f"❌ Directory not found: {amendments_dir}")

    # Collect all amendment JSONs recursively
    json_files = []
    for root, dirs, files in os.walk(amendments_dir):
        for file in files:
            if file.lower().endswith(".json"):
                json_files.append(os.path.join(root, file))

    if not json_files:
        print(f"⚠️ No JSON files found in {amendments_dir}")
        return

    print(f"📂 Found {len(json_files)} amendment files in {amendments_dir}")
    print("=========================================")

    for file_path in json_files:
        print(f"➡️ Loading amendment: {file_path}")
        # locate base file if base_dir provided
        base_file = None
        if base_dir:
            if os.path.isdir(base_dir):
                base_file = find_base_file_for_amendment(file_path, base_dir)
                if base_file:
                    print(f"   🔍 Found base: {base_file}")
                else:
                    print(f"   ⚠️ Base file not found in {base_dir} for amendment; loader will try fallback.")
            elif os.path.isfile(base_dir):
                # user gave a single base file path -> use it (not typical)
                base_file = base_dir

        try:
            load_amendment_data(file_path, base_file)
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
        print("-----------------------------------------")

    print("✅ All amendment files processed (completed loop).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load all amendment gazettes into Neo4j.")
    parser.add_argument("--dir", required=True, help="Directory containing amendment JSON files (recursively)")
    parser.add_argument("--base", required=False, help="Optional base gazette directory (for fallback)")
    args = parser.parse_args()

    load_all_amendments(args.dir, args.base)
