import json
import os
import argparse
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def extract_item_number(item_str):
    match = re.search(r"(\d+)", item_str)
    return match.group(1) if match else None

def get_item_name_from_base_gazette(base_gazette_path, minister_number, column_no, item_number):
    if not os.path.exists(base_gazette_path):
        print(f"❌ Base gazette not found: {base_gazette_path}")
        return None
    with open(base_gazette_path, "r", encoding="utf-8") as f:
        base_data = json.load(f)
    for minister in base_data.get("ministers", []):
        if str(minister.get("number")) == str(minister_number):
            if column_no == "1":
                items = minister.get("functions", [])
            elif column_no == "2":
                items = minister.get("departments", [])
            else:
                return None
            for item_str in items:
                match = re.match(r"^\s*(\d+)\.\s*(.+)$", item_str.strip())
                if match and match.group(1) == str(item_number):
                    return match.group(2)
    return None

def process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, flag):
    item_number = extract_item_number(raw)
    match = re.match(r"^\s*(\d+)\.\s*(.+)$", raw.strip())
    item_name = match.group(2) if match else raw.strip()
    if column_no == "1":
        session.run(
            f"""
            MERGE (f:Function {{item_number: $item_number, name: $item_name}})
            SET f.{flag} = $gazette_id,
                f.{flag}_date = $published_date
            WITH f
            MATCH (m:Minister {{name: $minister_name}})
            MERGE (m)-[:HAS_FUNCTION]->(f)
            """,
            item_number=item_number,
            item_name=item_name,
            gazette_id=gazette_id,
            published_date=published_date,
            minister_name=minister_name,
        )
    elif column_no == "2":
        session.run(
            f"""
            MERGE (d:Department {{item_number: $item_number, name: $item_name}})
            SET d.{flag} = $gazette_id,
                d.{flag}_date = $published_date
            WITH d
            MATCH (m:Minister {{name: $minister_name}})
            MERGE (m)-[:OVERSEES]->(d)
            """,
            item_number=item_number,
            item_name=item_name,
            gazette_id=gazette_id,
            published_date=published_date,
            minister_name=minister_name,
        )
    elif column_no == "3":
        session.run(
            f"""
            MERGE (l:Law {{name: $item_name}})
            SET l.{flag} = $gazette_id,
                l.{flag}_date = $published_date
            WITH l
            MATCH (m:Minister {{name: $minister_name}})
            MERGE (m)-[:ENFORCES]->(l)
            """,
            item_name=item_name,
            gazette_id=gazette_id,
            published_date=published_date,
            minister_name=minister_name,
        )

def process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date):
    if column_no == "1":
        session.run(
            """
            MATCH (f:Function {item_number: $item_number, name: $item_name})
            SET f.removed_in = $gazette_id,
                f.removed_in_date = $published_date
            """,
            item_number=item_number,
            item_name=item_name,
            gazette_id=gazette_id,
            published_date=published_date,
        )
    elif column_no == "2":
        session.run(
            """
            MATCH (d:Department {item_number: $item_number, name: $item_name})
            SET d.removed_in = $gazette_id,
                d.removed_in_date = $published_date
            """,
            item_number=item_number,
            item_name=item_name,
            gazette_id=gazette_id,
            published_date=published_date,
        )

def load_amendment_data(json_path, base_gazette_path=None):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    gazette_id = meta.get("Gazette ID")
    published_date = meta.get("Gazette Published Date")
    parent_gazette_id = meta.get("Parent Gazette", {}).get("Gazette ID")

    # Dynamically determine base gazette path if not provided
    if not base_gazette_path:
        if parent_gazette_id:
            safe_id = parent_gazette_id.replace('/', '-')
            amendment_dir = os.path.dirname(os.path.abspath(json_path))
            base_dir = amendment_dir.replace('amendment', 'base')
            base_gazette_filename = f"{safe_id}_E_sample.json"
            base_gazette_path = os.path.join(base_dir, base_gazette_filename)
        else:
            base_gazette_path = None

    with driver.session() as session:
        session.run("""
            MERGE (a:AmendmentGazette {gazette_id: $gazette_id})
            SET a.published_date = $published_date,
                a.published_by = $published_by,
                a.gazette_type = $gazette_type,
                a.language = $language,
                a.pdf_url = $pdf_url
        """,
            gazette_id=gazette_id,
            published_date=published_date,
            published_by=meta.get("Gazette Published by"),
            gazette_type=meta.get("Gazette Type"),
            language=meta.get("Language"),
            pdf_url=meta.get("PDF URL")
        )

        if parent_gazette_id:
            session.run("""
                MERGE (b:BaseGazette {gazette_id: $parent_id})
                MERGE (a:AmendmentGazette {gazette_id: $amend_id})
                MERGE (b)-[r:AMENDED_BY]->(a)
                SET r.date = $date
            """, parent_id=parent_gazette_id, amend_id=gazette_id, date=published_date)

        for change in data.get("changes", []):
            op_type = change.get("operation_type")
            details = change.get("details", {})
            minister_name = details.get("name")
            minister_number = details.get("number")
            column_no = details.get("column_no")

            # Handle deletions in DELETION and UPDATE operations
            if op_type in ["DELETION", "UPDATE"]:
                for raw in details.get("deleted_sections", []):
                    item_number = extract_item_number(raw)
                    item_name = None
                    if column_no in ["1", "2"] and item_number and parent_gazette_id:
                        item_name = get_item_name_from_base_gazette(
                            base_gazette_path, minister_number, column_no, item_number
                        )
                        if item_name:
                            process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date)
                        else:
                            print(f"⚠️ Could not find item name for Minister {minister_name} ({minister_number}), column {column_no}, item {item_number}")
            # Handle insertions
            if op_type == "INSERTION":
                for raw in details.get("added_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")

            # Handle updates (added/updated content)
            if op_type == "UPDATE":
                for raw in details.get("added_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")
                for raw in details.get("updated_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "updated_in")

    print(f"✅ Amendment Gazette {gazette_id} applied to parent {parent_gazette_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Amendment Gazette JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    parser.add_argument("--base", required=True, help="Path to parent/base gazette JSON file")
    args = parser.parse_args()
    load_amendment_data(args.input, args.base)