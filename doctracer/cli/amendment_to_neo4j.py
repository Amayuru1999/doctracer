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
    """Find node and relationship, return dict with existence info and current name.
    
    FIX: Now includes gazette_id and minister_number constraint to avoid cross-gazette/minister conflicts.
    """
    # Normalize minister number by stripping parentheses but keep leading zeros to match stored data (e.g., "04")
    clean_number = str(minister_number).strip('()')
    normalized_minister_number = clean_number.zfill(2) if clean_number.isdigit() else clean_number
    
    q = f"""
    MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number, gazette_id: $parent_id}})
    OPTIONAL MATCH (m)-[r:{rel}]->(n:{label} {{minister_number: $minister_number, gazette_id: $parent_id}})
    WHERE ($item_number IS NOT NULL AND n.item_number = $item_number) OR ($item_number IS NULL AND n.name = $item_name)
    RETURN n IS NOT NULL AS node_exists, id(n) AS node_id, r IS NOT NULL AS rel_exists, n.name AS current_name
    LIMIT 1
    """
    res = session.run(q, parent_id=parent_id, minister_number=normalized_minister_number,
                      item_number=item_number, item_name=item_name)
    rec = res.single()
    if rec:
        return {"node_exists": rec["node_exists"], "node_id": rec["node_id"],
                "rel_exists": rec["rel_exists"], "current_name": rec["current_name"]}
    return {"node_exists": False, "node_id": None, "rel_exists": False, "current_name": None}


def apply_change(session, parent_id, minister_number, column_no, raw_text, amend_id, published_date, action, base_gazette_file=None):
    """
    Apply a single change (added/removed/updated) to Neo4j.
    
    Properly tracks all changes through node and relationship properties:
    
    Node Properties:
    - added_by, added_on: Amendment that first added this item
    - updated_by, updated_on: Latest amendment that updated this item
    - removed_by, removed_on: Amendment that removed this item
    - is_active: Boolean flag (true if active, false if removed)
    
    Relationship Properties:
    - added_by, added_on: When relationship was created
    - updated_by, updated_on: When relationship was updated
    - removed_by, removed_on: When relationship was removed
    - is_active: Boolean flag (true if active, false if removed)
    
    This allows complete audit trail of changes through amendments.
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

    # Normalize minister number by stripping parentheses but keep leading zeros to match stored data (e.g., "04")
    clean_number = str(minister_number).strip('()')
    normalized_minister_number = clean_number.zfill(2) if clean_number.isdigit() else clean_number
    
    params = {
        "parent_id": parent_id,
        "minister_number": normalized_minister_number,
        "item_number": item_number,
        "item_name": item_name,
        "amend_id": amend_id,
        "published_date": published_date
    }

    # Skip if node exists and content unchanged (for added/updated)
    if found["node_exists"] and action in ["added", "updated"]:
        if found["current_name"] == item_name:
            # Node unchanged → do not update tracking properties
            return

    if found["node_exists"]:
        # Node exists → update tracking based on action type
        if action == "removed":
            # Mark node and relationship as removed, but keep for audit trail
            q_update = f"""
            MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number, gazette_id: $parent_id}})
            MATCH (m)-[r:{rel}]->(n:{label} {{minister_number: $minister_number, gazette_id: $parent_id}})
            WHERE ($item_number IS NOT NULL AND n.item_number = $item_number) OR ($item_number IS NULL AND n.name = $item_name)
            SET n.removed_by = $amend_id,
                n.removed_on = $published_date,
                n.is_active = false
            SET r.removed_by = $amend_id,
                r.removed_on = $published_date,
                r.is_active = false
            """
            action_desc = "Removed"
        else:
            # Track updates and additions
            q_update = f"""
            MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number, gazette_id: $parent_id}})
            MATCH (m)-[r:{rel}]->(n:{label} {{minister_number: $minister_number, gazette_id: $parent_id}})
            WHERE ($item_number IS NOT NULL AND n.item_number = $item_number) OR ($item_number IS NULL AND n.name = $item_name)
            SET n.updated_by = $amend_id,
                n.updated_on = $published_date,
                n.is_active = true
            SET r.updated_by = $amend_id,
                r.updated_on = $published_date,
                r.is_active = true
            """
            action_desc = "Updated" if action == "updated" else "Restored"
        
        session.run(q_update, **params)
        print(f"ℹ️ {action_desc} {label} node for minister {normalized_minister_number} (amendment: {amend_id}).")
    else:
        # Node not found → create new node and relationship with proper tracking
        if item_number:
            q_create = f"""
            MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number, gazette_id: $parent_id}})
            CREATE (n:{label} {{item_number: $item_number, minister_number: $minister_number, name: $item_name, 
                                gazette_id: $parent_id, added_by: $amend_id, added_on: $published_date, is_active: true}})
            CREATE (m)-[rr:{rel}]->(n)
            SET rr.added_by = $amend_id, rr.added_on = $published_date, rr.is_active = true
            """
        else:
            q_create = f"""
            MATCH (b:BaseGazette {{gazette_id: $parent_id}})-[:HAS_MINISTER]->(m:Minister {{number: $minister_number, gazette_id: $parent_id}})
            CREATE (n:{label} {{name: $item_name, minister_number: $minister_number, gazette_id: $parent_id, 
                                added_by: $amend_id, added_on: $published_date, is_active: true}})
            CREATE (m)-[rr:{rel}]->(n)
            SET rr.added_by = $amend_id, rr.added_on = $published_date, rr.is_active = true
            """
        
        session.run(q_create, **params)
        print(f"ℹ️ Created {label} node for minister {normalized_minister_number} (amendment: {amend_id}).")


def load_amendment_data(json_path, base_gazette_path=None):
    """
    Load amendment data with proper change tracking.
    
    Each change is tracked at both node and relationship level.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    amend_gazette_id = meta.get("gazette_id")
    published_date = meta.get("published_date") or meta.get("Gazette Published Date")
    parent_gazette_id = (meta.get("parent_gazette") or {}).get("gazette_id") or data.get("parent_gazette") or data.get("parent")

    if not amend_gazette_id or not parent_gazette_id:
        raise ValueError("Amendment JSON missing gazette_id or parent_gazette.gazette_id")

    # Fallback base file: prefer an explicitly passed file. If base_gazette_path is a directory,
    # try to find matching base file by gazette id inside that directory.
    def _find_base_in_dir_by_id(base_dir, parent_id):
        if not base_dir or not os.path.isdir(base_dir):
            return None
        pid_safe = str(parent_id).replace("/", "-")
        for root, _, files in os.walk(base_dir):
            for fname in files:
                if not fname.lower().endswith(".json"):
                    continue
                # quick filename check
                if pid_safe in fname or str(parent_id) in fname:
                    return os.path.join(root, fname)
                # content check (safe)
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as bf:
                        bdata = json.load(bf)
                    file_gzid = bdata.get("gazette_id") or bdata.get("metadata", {}).get("gazette_id")
                    if file_gzid and str(file_gzid) == str(parent_id):
                        return fpath
                except Exception:
                    continue
        return None

    # If caller passed a directory as base_gazette_path, resolve it to the actual file
    if base_gazette_path and os.path.isdir(base_gazette_path):
        found = _find_base_in_dir_by_id(base_gazette_path, parent_gazette_id)
        if found:
            base_gazette_path = found
        else:
            # if not found, leave it None so other fallback logic may try
            base_gazette_path = None

    # Existing fallback (your original logic) now runs if base_gazette_path still None
    if not base_gazette_path and parent_gazette_id:
        safe_id = parent_gazette_id.replace("/", "-")
        amendment_dir = os.path.dirname(os.path.abspath(json_path))
        base_dir_guess = amendment_dir.replace("amendment", "base")
        candidate = os.path.join(base_dir_guess, f"{safe_id}_E.json")
        if os.path.exists(candidate) and os.path.isfile(candidate):
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

    print(f"✅ Applied amendment {amend_gazette_id} to parent {parent_gazette_id} with proper change tracking.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply amendment gazette JSON to Neo4j")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    parser.add_argument("--base", required=False, help="Optional path to base gazette JSON")
    args = parser.parse_args()
    load_amendment_data(args.input, args.base)
