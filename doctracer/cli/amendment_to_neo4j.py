#!/usr/bin/env python3
import json
import re
import os
import argparse
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def extract_item_number(item_str):
    """Return the first integer found, as string, or None."""
    if not item_str:
        return None
    m = re.search(r"(\d+)", str(item_str))
    return str(m.group(1)) if m else None


def normalize_column(col):
    """Normalize column inputs like 'I', 'II', 'III' or '1','2','3' to '1'|'2'|'3'."""
    if col is None:
        return None
    s = str(col).strip().upper()
    roman_map = {"I": "1", "II": "2", "III": "3"}
    if s in roman_map:
        return roman_map[s]
    m = re.search(r"([1-3])", s)
    if m:
        return m.group(1)
    return None


def get_item_name_from_base_file(base_gazette_path, minister_number, column_no, item_number):
    """Fallback: attempt to read name from base JSON file (if available)."""
    if not base_gazette_path or not os.path.exists(base_gazette_path):
        return None
    with open(base_gazette_path, "r", encoding="utf-8") as f:
        base = json.load(f)
    for minister in base.get("ministers", []):
        if str(minister.get("number")) == str(minister_number):
            if column_no == "1":
                items = minister.get("functions", [])
            elif column_no == "2":
                items = minister.get("departments", [])
            else:
                items = minister.get("laws", [])
            for it in items:
                m = re.match(r"^\s*(\d+)\.\s*(.+)$", str(it).strip())
                if m and m.group(1) == str(item_number):
                    return m.group(2).strip()
    return None


def find_node_and_rel(session, parent_id, minister_number, label, rel, item_number=None, item_name=None):
    """Find node and relationship, return dict with existence info and current name."""
    q = f"""
    MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number}})
    OPTIONAL MATCH (m)-[r:{rel}]->(n:{label})
    WHERE ($item_number IS NOT NULL AND n.item_number = $item_number) OR ($item_number IS NULL AND n.name = $item_name)
    RETURN n IS NOT NULL AS node_exists, id(n) AS node_id, r IS NOT NULL AS rel_exists, n.name AS current_name
    LIMIT 1
    """
    res = session.run(q, parent_id=parent_id, minister_number=str(minister_number),
                      item_number=item_number, item_name=item_name)
    rec = res.single()
    if rec:
        return {"node_exists": rec["node_exists"], "node_id": rec["node_id"],
                "rel_exists": rec["rel_exists"], "current_name": rec["current_name"]}
    return {"node_exists": False, "node_id": None, "rel_exists": False, "current_name": None}


def apply_change(session, parent_id, minister_number, column_no, raw_text, amend_id, published_date, action, base_gazette_file=None):
    """
    Apply a single change (added/removed/updated) to Neo4j.
    Only modifies nodes if content actually changed.
    """
    column = normalize_column(column_no)
    label_map = {"1": "Function", "2": "Department", "3": "Law"}
    rel_map = {"1": "HAS_FUNCTION", "2": "OVERSEES_DEPARTMENT", "3": "RESPONSIBLE_FOR_LAW"}

    label = label_map.get(column)
    rel = rel_map.get(column)
    if not label or not rel:
        print(f"⚠️ Unknown column '{column_no}' for minister {minister_number}. Skipping.")
        return

    item_number = extract_item_number(raw_text)
    item_name = None
    if item_number and base_gazette_file:
        item_name = get_item_name_from_base_file(base_gazette_file, minister_number, column, item_number)
    if not item_name:
        m = re.match(r"^\s*\d+\.\s*(.+)$", str(raw_text).strip())
        if m:
            item_name = m.group(1).strip()
        else:
            item_name = str(raw_text).strip()

    found = find_node_and_rel(session, parent_id, minister_number, label, rel, item_number, item_name)

    # Determine node property names
    node_prop_by = f"{action}_by"
    node_prop_on = f"{action}_on"
    rel_prop_by = f"{action}_by"
    rel_prop_on = f"{action}_on"

    params = {
        "parent_id": parent_id,
        "minister_number": str(minister_number),
        "item_number": item_number,
        "item_name": item_name,
        "amend_id": amend_id,
        "published_date": published_date
    }

    # Skip if node exists and content unchanged (for added/updated)
    if found["node_exists"] and action in ["added", "updated"]:
        if found["current_name"] == item_name:
            # Node unchanged → do not overwrite base added_by/added_date
            return

    if found["node_exists"]:
        # Update node/rel for changed content or removal
        q_update = f"""
        MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number}})
        MATCH (m)-[r:{rel}]->(n:{label})
        WHERE ($item_number IS NOT NULL AND n.item_number = $item_number) OR ($item_number IS NULL AND n.name = $item_name)
        SET n.{node_prop_by} = $amend_id,
            n.{node_prop_on} = $published_date
        MERGE (m)-[rr:{rel}]->(n)
        SET rr.{rel_prop_by} = $amend_id,
            rr.{rel_prop_on} = $published_date
        """
        session.run(q_update, **params)
        print(f"ℹ️ Updated existing {label} node for minister {minister_number}.")
    else:
        # Node not found → create new node and relationship
        q_create = f"""
        MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number}})
        CREATE (n:{label} {{name: $item_name, {node_prop_by}: $amend_id, {node_prop_on}: $published_date}})
        """
        if item_number:
            q_create = f"""
            MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number}})
            CREATE (n:{label} {{item_number: $item_number, name: $item_name, {node_prop_by}: $amend_id, {node_prop_on}: $published_date}})
            """
        q_create += f"""
        CREATE (m)-[rr:{rel}]->(n)
        SET rr.{rel_prop_by} = $amend_id, rr.{rel_prop_on} = $published_date
        """
        session.run(q_create, **params)
        print(f"ℹ️ Created {label} node and relationship for minister {minister_number}.")


def load_amendment_data(json_path, base_gazette_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    amend_gazette_id = meta.get("gazette_id")
    published_date = meta.get("published_date") or meta.get("Gazette Published Date")
    parent_gazette_id = (meta.get("parent_gazette") or {}).get("gazette_id") or data.get("parent_gazette") or data.get("parent")

    if not amend_gazette_id or not parent_gazette_id:
        raise ValueError("Amendment JSON missing gazette_id or parent_gazette.gazette_id")

    # Fallback base file
    if not base_gazette_path and parent_gazette_id:
        safe_id = parent_gazette_id.replace("/", "-")
        amendment_dir = os.path.dirname(os.path.abspath(json_path))
        base_dir = amendment_dir.replace("amendment", "base")
        candidate = os.path.join(base_dir, f"{safe_id}_E.json")
        if os.path.exists(candidate):
            base_gazette_path = candidate

    with driver.session() as session:
        # Create Amendment node
        session.run("""
        MERGE (a:AmendmentGazette {gazette_id: $amend_id})
        SET a.published_date = $published_date, a.published_by = $published_by,
            a.gazette_type = $gazette_type, a.language = $language, a.pdf_url = $pdf_url
        """, amend_id=amend_gazette_id, published_date=published_date,
        published_by=meta.get("published_by"), gazette_type=meta.get("gazette_type"),
        language=meta.get("language"), pdf_url=meta.get("pdf_url"))

        # Link to base gazette
        session.run("""
        MERGE (b:BaseGazette {gazette_id: $parent_id})
        MERGE (a:AmendmentGazette {gazette_id: $amend_id})
        MERGE (b)-[r:AMENDED_BY]->(a)
        SET r.date = $date
        """, parent_id=parent_gazette_id, amend_id=amend_gazette_id, date=published_date)

        # Process changes
        for change in data.get("changes", []):
            op_type = (change.get("operation_type") or "").upper()
            details = change.get("details", {}) or {}
            minister_number = details.get("number") or details.get("minister_number")
            column_no = details.get("column_no") or details.get("column")

            if not minister_number or not column_no:
                print(f"⚠️ Skipping change missing minister_number or column: {change}")
                continue

            # Deletions
            if op_type in ["DELETION", "UPDATE"]:
                for raw in details.get("deleted_sections", []) or []:
                    apply_change(session, parent_gazette_id, minister_number, column_no, raw,
                                 amend_gazette_id, published_date, "removed", base_gazette_path)

            # Insertions / updates
            if op_type in ["INSERTION", "UPDATE"]:
                for raw in details.get("added_content", []) or []:
                    apply_change(session, parent_gazette_id, minister_number, column_no, raw,
                                 amend_gazette_id, published_date, "added", base_gazette_path)
                for raw in details.get("updated_content", []) or []:
                    apply_change(session, parent_gazette_id, minister_number, column_no, raw,
                                 amend_gazette_id, published_date, "updated", base_gazette_path)

    print(f"✅ Applied amendment {amend_gazette_id} to parent {parent_gazette_id}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply amendment gazette JSON to Neo4j")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    parser.add_argument("--base", required=False, help="Optional path to base gazette JSON")
    args = parser.parse_args()
    load_amendment_data(args.input, args.base)


# import json
# import os
# import re
# import argparse
# from neo4j import GraphDatabase
# from dotenv import load_dotenv

# load_dotenv()

# URI = os.getenv("NEO4J_URI")
# USER = os.getenv("NEO4J_USER")
# PASSWORD = os.getenv("NEO4J_PASSWORD")

# driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# def extract_item_number(item_str):
#     match = re.search(r"(\d+)", item_str)
#     return match.group(1) if match else None

# def get_item_name_from_base_gazette(base_gazette_path, minister_number, column_no, item_number):
#     if not os.path.exists(base_gazette_path):
#         return None
#     with open(base_gazette_path, "r", encoding="utf-8") as f:
#         base_data = json.load(f)

#     for minister in base_data.get("ministers", []):
#         if str(minister.get("number")) == str(minister_number):
#             items = []
#             if column_no == "1":
#                 items = minister.get("functions", [])
#             elif column_no == "2":
#                 items = minister.get("departments", [])
#             for item_str in items:
#                 match = re.match(r"^\s*(\d+)\.\s*(.+)$", item_str.strip())
#                 if match and match.group(1) == str(item_number):
#                     return match.group(2)
#     return None

# def process_change(session, column_no, item_number, item_name, minister_number, gazette_id, published_date, change_type):
#     label_map = {"1": "Function", "2": "Department", "3": "Law"}
#     rel_map = {"1": "HAS_FUNCTION", "2": "OVERSEES_DEPARTMENT", "3": "RESPONSIBLE_FOR_LAW"}
#     label = label_map.get(column_no)
#     rel = rel_map.get(column_no)
#     if not label or not rel:
#         return

#     cypher = f"""
#         MERGE (n:{label} {{item_number: coalesce($item_number, 'N/A'), name: $item_name}})
#         SET n.{change_type} = $gazette_id,
#             n.{change_type}_date = $published_date
#         WITH n
#         MATCH (m:Minister {{number: $minister_number}})
#         MERGE (m)-[r:{rel}]->(n)
#         SET r.{change_type} = $gazette_id,
#             r.{change_type}_date = $published_date
#     """

#     session.run(cypher,
#                 item_number=item_number,
#                 item_name=item_name,
#                 minister_number=minister_number,
#                 gazette_id=gazette_id,
#                 published_date=published_date)

# def load_amendment_data(json_path, base_gazette_path=None):
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     meta = data.get("metadata", {})
#     gazette_id = meta.get("gazette_id")
#     published_date = meta.get("Gazette Published Date")
#     parent_gazette_id = meta.get("parent_gazette", {}).get("gazette_id")

#     if not base_gazette_path and parent_gazette_id:
#         safe_id = parent_gazette_id.replace('/', '-')
#         amendment_dir = os.path.dirname(os.path.abspath(json_path))
#         base_dir = amendment_dir.replace('amendment', 'base')
#         base_gazette_path = os.path.join(base_dir, f"{safe_id}_E.json")

#     with driver.session() as session:
#         session.run(
#             """
#             MERGE (a:AmendmentGazette {gazette_id: $gazette_id})
#             SET a.published_date = $published_date,
#                 a.published_by = $published_by,
#                 a.gazette_type = $gazette_type,
#                 a.language = $language,
#                 a.pdf_url = $pdf_url
#             """,
#             gazette_id=gazette_id,
#             published_date=published_date,
#             published_by=meta.get("published_by"),
#             gazette_type=meta.get("gazette_type"),
#             language=meta.get("language"),
#             pdf_url=meta.get("pdf_url")
#         )

#         if parent_gazette_id:
#             session.run(
#                 """
#                 MERGE (b:BaseGazette {gazette_id: $parent_id})
#                 MERGE (a:AmendmentGazette {gazette_id: $amend_id})
#                 MERGE (b)-[r:AMENDED_BY]->(a)
#                 SET r.date = $date
#                 """,
#                 parent_id=parent_gazette_id,
#                 amend_id=gazette_id,
#                 date=published_date
#             )

#         for change in data.get("changes", []):
#             op_type = change.get("operation_type")
#             details = change.get("details", {})
#             minister_number = details.get("number")
#             column_no = details.get("column_no")

#             # Handle deletions
#             if op_type in ["DELETION", "UPDATE"]:
#                 for raw in details.get("deleted_sections", []):
#                     item_number = extract_item_number(raw)
#                     item_name = get_item_name_from_base_gazette(base_gazette_path, minister_number, column_no, item_number)
#                     if item_name:
#                         process_change(session, column_no, item_number, item_name, minister_number, gazette_id, published_date, "removed_in")

#             # Handle insertions
#             if op_type in ["INSERTION", "UPDATE"]:
#                 for raw in details.get("added_content", []):
#                     item_number = extract_item_number(raw)
#                     item_name = raw.strip()
#                     process_change(session, column_no, item_number, item_name, minister_number, gazette_id, published_date, "added_in")
#                 for raw in details.get("updated_content", []):
#                     item_number = extract_item_number(raw)
#                     item_name = raw.strip()
#                     process_change(session, column_no, item_number, item_name, minister_number, gazette_id, published_date, "updated_in")

#     print(f"✅ Amendment Gazette {gazette_id} applied to parent {parent_gazette_id}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--input", required=True, help="Path to amendment JSON file")
#     parser.add_argument("--base", required=False, help="Path to parent/base gazette JSON file")
#     args = parser.parse_args()

#     load_amendment_data(args.input, args.base)


# import json
# import os
# import argparse
# import re
# from neo4j import GraphDatabase
# from dotenv import load_dotenv

# load_dotenv()

# URI = os.getenv("NEO4J_URI")
# USER = os.getenv("NEO4J_USER")
# PASSWORD = os.getenv("NEO4J_PASSWORD")

# driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# def extract_item_number(item_str):
#     match = re.search(r"(\d+)", item_str)
#     return match.group(1) if match else None

# def get_item_name_from_base_gazette(base_gazette_path, minister_number, column_no, item_number):
#     if not os.path.exists(base_gazette_path):
#         print(f"❌ Base gazette not found: {base_gazette_path}")
#         return None
#     with open(base_gazette_path, "r", encoding="utf-8") as f:
#         base_data = json.load(f)
#     for minister in base_data.get("ministers", []):
#         if str(minister.get("number")) == str(minister_number):
#             if column_no == "1":
#                 items = minister.get("functions", [])
#             elif column_no == "2":
#                 items = minister.get("departments", [])
#             else:
#                 return None
#             for item_str in items:
#                 match = re.match(r"^\s*(\d+)\.\s*(.+)$", item_str.strip())
#                 if match and match.group(1) == str(item_number):
#                     return match.group(2)
#     return None

# def process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, flag):
#     item_number = extract_item_number(raw)
#     match = re.match(r"^\s*(\d+)\.\s*(.+)$", raw.strip())
#     item_name = match.group(2) if match else raw.strip()
#     if column_no == "1":
#         session.run(
#             f"""
#             MERGE (f:Function {{item_number: $item_number, name: $item_name}})
#             SET f.{flag} = $gazette_id,
#                 f.{flag}_date = $published_date
#             WITH f
#             MATCH (m:Minister {{name: $minister_name}})
#             MERGE (m)-[:HAS_FUNCTION]->(f)
#             """,
#             item_number=item_number,
#             item_name=item_name,
#             gazette_id=gazette_id,
#             published_date=published_date,
#             minister_name=minister_name,
#         )
#     elif column_no == "2":
#         session.run(
#             f"""
#             MERGE (d:Department {{item_number: $item_number, name: $item_name}})
#             SET d.{flag} = $gazette_id,
#                 d.{flag}_date = $published_date
#             WITH d
#             MATCH (m:Minister {{name: $minister_name}})
#             MERGE (m)-[:OVERSEES_DEPARTMENT]->(d)
#             """,
#             item_number=item_number,
#             item_name=item_name,
#             gazette_id=gazette_id,
#             published_date=published_date,
#             minister_name=minister_name,
#         )
#     elif column_no == "3":
#         session.run(
#             f"""
#             MERGE (l:Law {{name: $item_name}})
#             SET l.{flag} = $gazette_id,
#                 l.{flag}_date = $published_date
#             WITH l
#             MATCH (m:Minister {{name: $minister_name}})
#             MERGE (m)-[:RESPONSIBLE_FOR_LAW]->(l)
#             """,
#             item_name=item_name,
#             gazette_id=gazette_id,
#             published_date=published_date,
#             minister_name=minister_name,
#         )

# def process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date):
#     if column_no == "1":
#         session.run(
#             """
#             MATCH (f:Function {item_number: $item_number, name: $item_name})
#             SET f.removed_in = $gazette_id,
#                 f.removed_in_date = $published_date
#             """,
#             item_number=item_number,
#             item_name=item_name,
#             gazette_id=gazette_id,
#             published_date=published_date,
#         )
#     elif column_no == "2":
#         session.run(
#             """
#             MATCH (d:Department {item_number: $item_number, name: $item_name})
#             SET d.removed_in = $gazette_id,
#                 d.removed_in_date = $published_date
#             """,
#             item_number=item_number,
#             item_name=item_name,
#             gazette_id=gazette_id,
#             published_date=published_date,
#         )

# def load_amendment_data(json_path, base_gazette_path=None):
#     if not os.path.exists(json_path):
#         raise FileNotFoundError(f"❌ File not found: {json_path}")

#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     meta = data.get("metadata", {})
#     gazette_id = meta.get("gazette_id")
#     published_date = meta.get("Gazette Published Date")
#     parent_gazette_id = meta.get("Parent Gazette", {}).get("gazette_id")

#     # Dynamically determine base gazette path if not provided
#     if not base_gazette_path:
#         if parent_gazette_id:
#             safe_id = parent_gazette_id.replace('/', '-')
#             amendment_dir = os.path.dirname(os.path.abspath(json_path))
#             base_dir = amendment_dir.replace('amendment', 'base')
#             base_gazette_filename = f"{safe_id}_E.json"
#             base_gazette_path = os.path.join(base_dir, base_gazette_filename)
#         else:
#             base_gazette_path = None

#     with driver.session() as session:
#         session.run("""
#             MERGE (a:AmendmentGazette {gazette_id: $gazette_id})
#             SET a.published_date = $published_date,
#                 a.published_by = $published_by,
#                 a.gazette_type = $gazette_type,
#                 a.language = $language,
#                 a.pdf_url = $pdf_url
#         """,
#             gazette_id=gazette_id,
#             published_date=published_date,
#             published_by=meta.get("published_by"),
#             gazette_type=meta.get("Gazette Type"),
#             language=meta.get("Language"),
#             pdf_url=meta.get("PDF URL")
#         )

#         if parent_gazette_id:
#             session.run("""
#                 MERGE (b:BaseGazette {gazette_id: $parent_id})
#                 MERGE (a:AmendmentGazette {gazette_id: $amend_id})
#                 MERGE (b)-[r:AMENDED_BY]->(a)
#                 SET r.date = $date
#             """, parent_id=parent_gazette_id, amend_id=gazette_id, date=published_date)

#         for change in data.get("changes", []):
#             op_type = change.get("operation_type")
#             details = change.get("details", {})
#             minister_name = details.get("name")
#             minister_number = details.get("number")
#             column_no = details.get("column_no")

#             # Handle deletions in DELETION and UPDATE operations
#             if op_type in ["DELETION", "UPDATE"]:
#                 for raw in details.get("deleted_sections", []):
#                     item_number = extract_item_number(raw)
#                     item_name = None
#                     if column_no in ["1", "2"] and item_number and parent_gazette_id:
#                         item_name = get_item_name_from_base_gazette(
#                             base_gazette_path, minister_number, column_no, item_number
#                         )
#                         if item_name:
#                             process_deletion(session, column_no, item_number, item_name, minister_name, gazette_id, published_date)
#                         else:
#                             print(f"⚠️ Could not find item name for Minister {minister_name} ({minister_number}), column {column_no}, item {item_number}")
#             # Handle insertions
#             if op_type == "INSERTION":
#                 for raw in details.get("added_content", []):
#                     process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")

#             # Handle updates (added/updated content)
#             if op_type == "UPDATE":
#                 for raw in details.get("added_content", []):
#                     process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "added_in")
#                 for raw in details.get("updated_content", []):
#                     process_add_or_update(session, column_no, raw, minister_name, gazette_id, published_date, "updated_in")

#     print(f"✅ Amendment Gazette {gazette_id} applied to parent {parent_gazette_id}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Load Amendment Gazette JSON into Neo4j")
#     parser.add_argument("--input", required=True, help="Path to amendment JSON file")
#     parser.add_argument("--base", required=True, help="Path to parent/base gazette JSON file")
#     args = parser.parse_args()
#     load_amendment_data(args.input, args.base)