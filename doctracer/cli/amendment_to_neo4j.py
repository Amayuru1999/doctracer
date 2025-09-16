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

def extract_item_number(item_str: str):
    if not item_str:
        return None
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
            elif column_no == "3":
                items = minister.get("laws", [])
            else:
                return None
            for item_str in items:
                match = re.match(r"^\s*(\d+)\.\s*(.+)$", item_str.strip())
                if match and match.group(1) == str(item_number):
                    return match.group(2)
    return None

def process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, flag):
    if not raw or not minister_name:
        return
    item_number = extract_item_number(raw)
    match = re.match(r"^\s*(\d+)\.\s*(.+)$", raw.strip())
    item_name = match.group(2) if match else raw.strip()

    if column_no == "1":
        session.run("""
            MERGE (f:AmendmentFunction:Function {item_number: $item_number, description: $item_name})
            SET f.source = 'amendment', f[$flag] = $gazette_id, f[$flag+'_date'] = $published_date
            WITH f
            MERGE (m:AmendmentMinister:Minister {name: $minister_name})
            MERGE (m)-[:PERFORMS_FUNCTION {status:$flag, amendment_date:$published_date}]->(f)
        """, item_number=item_number, item_name=item_name, gazette_id=gazette_id,
           published_date=published_date, minister_name=minister_name, flag=flag)

    elif column_no == "2":
        session.run("""
            MERGE (d:AmendmentDepartment:Department {item_number: $item_number, name: $item_name})
            SET d.source = 'amendment', d[$flag] = $gazette_id, d[$flag+'_date'] = $published_date
            WITH d
            MERGE (m:AmendmentMinister:Minister {name: $minister_name})
            MERGE (m)-[:OVERSEES_DEPARTMENT {status:$flag, amendment_date:$published_date}]->(d)
        """, item_number=item_number, item_name=item_name, gazette_id=gazette_id,
           published_date=published_date, minister_name=minister_name, flag=flag)

    elif column_no == "3":
        session.run("""
            MERGE (l:AmendmentLaw:Law {name: $item_name})
            SET l.source = 'amendment', l[$flag] = $gazette_id, l[$flag+'_date'] = $published_date
            WITH l
            MERGE (m:AmendmentMinister:Minister {name: $minister_name})
            MERGE (m)-[:RESPONSIBLE_FOR_LAW {status:$flag, amendment_date:$published_date}]->(l)
        """, item_name=item_name, gazette_id=gazette_id,
           published_date=published_date, minister_name=minister_name, flag=flag)

def process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date):
    if not item_name:
        return
    if column_no == "1":
        session.run("""
            MATCH (f:AmendmentFunction {item_number: $item_number, description: $item_name})
            SET f.removed_in = $gazette_id, f.removed_in_date = $published_date
        """, item_number=item_number, item_name=item_name, gazette_id=gazette_id, published_date=published_date)

    elif column_no == "2":
        session.run("""
            MATCH (d:AmendmentDepartment {item_number: $item_number, name: $item_name})
            SET d.removed_in = $gazette_id, d.removed_in_date = $published_date
        """, item_number=item_number, item_name=item_name, gazette_id=gazette_id, published_date=published_date)

    elif column_no == "3":
        session.run("""
            MATCH (l:AmendmentLaw {name: $item_name})
            SET l.removed_in = $gazette_id, l.removed_in_date = $published_date
        """, item_name=item_name, gazette_id=gazette_id, published_date=published_date)

def load_amendment_data(json_path, base_gazette_path=None):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    gazette_id = meta.get("Gazette ID")
    published_date = meta.get("Gazette Published Date")
    parent_gazette_id = meta.get("Parent Gazette", {}).get("Gazette No")

    # Derive base gazette path if not provided
    if not base_gazette_path and parent_gazette_id:
        safe_id = parent_gazette_id.replace('/', '-')
        amendment_dir = os.path.dirname(os.path.abspath(json_path))
        base_dir = amendment_dir.replace('amendment', 'base')
        base_gazette_filename = f"{safe_id}_E_sample.json"
        base_gazette_path = os.path.join(base_dir, base_gazette_filename)

    with driver.session() as session:
        # Create amendment gazette
        session.run("""
            MERGE (a:AmendmentGazette:Gazette {gazette_id: $gazette_id})
            SET a.published_date = $published_date,
                a.published_by = $published_by,
                a.gazette_type = $gazette_type,
                a.language = $language,
                a.pdf_url = $pdf_url,
                a.source = 'amendment'
        """, gazette_id=gazette_id, published_date=published_date,
           published_by=meta.get("Gazette Published by"),
           gazette_type=meta.get("Gazette Type"),
           language=meta.get("Language"),
           pdf_url=meta.get("PDF URL"))

        # Link to parent base gazette
        if parent_gazette_id:
            session.run("""
                MERGE (b:BaseGazette {gazette_id: $parent_id})
                MERGE (a:AmendmentGazette {gazette_id: $amend_id})
                MERGE (a)-[:AMENDS {date:$date}]->(b)
            """, parent_id=parent_gazette_id, amend_id=gazette_id, date=published_date)

        # Process changes
        for change in data.get("changes", []):
            op_type = change.get("operation_type")
            details = change.get("details", {})
            minister_name = details.get("name")
            minister_number = details.get("number")
            column_no = details.get("column_no")

            if not minister_name:
                print(f"⚠️ Skipping change with missing minister name: {change}")
                continue

            # Deletions + Updates (deleted sections)
            if op_type in ["DELETION", "UPDATE"]:
                for raw in details.get("deleted_sections", []):
                    item_number = extract_item_number(raw)
                    item_name = None
                    if parent_gazette_id and column_no in ["1", "2", "3"]:
                        item_name = get_item_name_from_base_gazette(base_gazette_path, minister_number, column_no, item_number)
                    if not item_name:
                        # fallback: raw string after dot
                        match = re.match(r"^\s*(\d+)\.\s*(.+)$", raw.strip())
                        item_name = match.group(2) if match else raw.strip()
                    process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date)

            # Insertions
            if op_type == "INSERTION":
                for raw in details.get("added_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")

            # Updates (added/updated content)
            if op_type == "UPDATE":
                for raw in details.get("added_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")
                for raw in details.get("updated_content", []):
                    process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "updated_in")

    print(f"✅ Amendment Gazette {gazette_id} applied to parent {parent_gazette_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Amendment Gazette JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    parser.add_argument("--base", help="Path to parent/base gazette JSON file (optional)")
    args = parser.parse_args()
    load_amendment_data(args.input, args.base)