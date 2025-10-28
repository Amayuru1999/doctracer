import os
from doctracer.cli.table_to_neo4j import load_table_data

def load_all_gazettes(json_dir: str):
    """Recursively load all JSON files in a folder and subfolders using os.walk."""
    if not os.path.exists(json_dir):
        print(f"❌ Path does not exist: {json_dir}")
        return

    # Collect all JSON files recursively
    json_files = []
    for root, dirs, files in os.walk(json_dir):
        for file in files:
            if file.lower().endswith(".json"):  # case-insensitive
                json_files.append(os.path.join(root, file))

    if not json_files:
        print(f"❌ No JSON files found in {json_dir}")
        return

    print(f"Found {len(json_files)} JSON files in {json_dir}\n")

    for file_path in json_files:
        try:
            print(f"Processing: {file_path}")
            load_table_data(file_path)
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load all base gazette JSONs into Neo4j")
    parser.add_argument("--input_dir", required=True, help="Path to folder containing JSON files")
    args = parser.parse_args()

    load_all_gazettes(args.input_dir)
