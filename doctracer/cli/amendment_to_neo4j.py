# load_amendment_data.py
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

def clean_item(item: str) -> str:
    """
    Remove 'item xx.' or 'number.' prefixes from section descriptions.
    Example: '18. Registration of Persons' -> 'Registration of Persons'
    """
    return re.sub(r"^\s*\d+(\.\d+)?\s*[\.\)]?\s*", "", item.strip())

def extract_item_number(item: str) -> int:
    """
    From 'item 3' or '3. Something' extract the integer 3.
    """
    match = re.search(r"(\d+)", item)
    return int(match.group(1)) if match else None

def process_item(session, column_no, item, minister_name, gazette_id, published_date, flag):
    """
    Handle insertion/update/deletion for Function / Department / Law
    based on column number.
    flag = 'added_in' | 'updated_in' | 'removed_in'
    """
    item_no = extract_item_number(item)   # ✅ keep extracted number
    content = clean_item(item)            # ✅ keep cleaned description

    mapping = {
        "1": ("Function", "description", "PERFORMS_FUNCTION"),
        "2": ("Department", "name", "OVERSEES_DEPARTMENT"),
        "3": ("Law", "name", "RESPONSIBLE_FOR_LAW"),
    }
    label, prop, rel = mapping.get(column_no, (None, None, None))
    if not label:
        print(f"⚠️ Unknown column {column_no}")
        return

    if item_no and not content:  
        # ✅ Case 1: only item number → match by item_number
        session.run(f"""
            MATCH (n:{label} {{item_number: $item_no}})
            WITH n
            MATCH (m:Minister {{name: $mname}})
            MERGE (m)-[r:{rel}]->(n)
            SET r.{flag} = $gazette_id, r.{flag}_date = $date
        """, item_no=item_no, mname=minister_name,
           gazette_id=gazette_id, date=published_date)

    elif item_no and content:  
        # ✅ Case 2: item number + description
        session.run(f"""
            MERGE (n:{label} {{{prop}: $content}})
            ON CREATE SET n.item_number = $item_no
            ON MATCH SET n.item_number = coalesce(n.item_number, $item_no)
            WITH n
            MATCH (m:Minister {{name: $mname}})
            MERGE (m)-[r:{rel}]->(n)
            SET r.{flag} = $gazette_id, r.{flag}_date = $date
        """, content=content, item_no=item_no, mname=minister_name,
           gazette_id=gazette_id, date=published_date)

    else:  
        # ✅ Case 3: only description
        session.run(f"""
            MERGE (n:{label} {{{prop}: $content}})
            WITH n
            MATCH (m:Minister {{name: $mname}})
            MERGE (m)-[r:{rel}]->(n)
            SET r.{flag} = $gazette_id, r.{flag}_date = $date
        """, content=content, mname=minister_name,
           gazette_id=gazette_id, date=published_date)


def load_amendment_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    gazette_id = meta.get("Gazette ID", "UNKNOWN")
    published_date = meta.get("Gazette Published Date")
    parent_gazette_id = meta.get("Parent Gazette", {}).get("Gazette No")

    with driver.session() as session:
        # Amendment Gazette node
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

        # Link parent base gazette
        if parent_gazette_id:
            session.run("""
                MATCH (b:BaseGazette {gazette_id: $parent_id})
                MATCH (a:AmendmentGazette {gazette_id: $amend_id})
                MERGE (b)-[r:AMENDED_BY]->(a)
                SET r.date = $date
            """, parent_id=parent_gazette_id, amend_id=gazette_id, date=published_date)

        # Process changes
        for change in data.get("changes", []):
            op_type = change.get("operation_type")
            details = change.get("details", {})
            minister_name = details.get("heading_name")
            column_no = details.get("column_no")

            if op_type == "UPDATE":
                for raw in details.get("deleted_sections", []):
                    process_item(session, column_no, raw, minister_name, gazette_id, published_date, "removed_in")

                for raw in details.get("updated_content", []):
                    process_item(session, column_no, raw, minister_name, gazette_id, published_date, "updated_in")

            elif op_type == "INSERTION":
                for raw in details.get("added_content", []):
                    process_item(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")

            elif op_type == "DELETION":
                for raw in details.get("deleted_sections", []):
                    process_item(session, column_no, raw, minister_name, gazette_id, published_date, "removed_in")

    print(f"✅ Amendment Gazette {gazette_id} applied to parent {parent_gazette_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Amendment Gazette JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    args = parser.parse_args()
    load_amendment_data(args.input)
