import json
import os
import argparse
import re
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def extract_item_number(text):
    """
    Extract leading item number (e.g. '1. Department...' -> ('1', 'Department...'))
    If no item number, returns (None, original_text)
    """
    match = re.match(r"^\s*(\d+)\.\s*(.*)", text)
    if match:
        return match.group(1), match.group(2).strip()
    return None, text.strip()

def load_base_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gazette_id = data["gazette_id"]

    with driver.session() as session:
        # Create Base Gazette
        session.run("""
            MERGE (g:BaseGazette {gazette_id: $gazette_id})
            SET g.published_date = $published_date,
                g.published_by   = $published_by,
                g.president      = $president,
                g.gazette_type   = $gazette_type,
                g.language       = $language,
                g.pdf_url        = $pdf_url
        """, 
        gazette_id=gazette_id,
        published_date=data.get("published_date"),
        published_by=data.get("published_by"),
        president=data.get("president"),
        gazette_type=data.get("gazette_type"),
        language=data.get("language"),
        pdf_url=data.get("pdf_url"))

        # Process Ministers
        for minister in data.get("ministers", []):
            session.run("""
                MERGE (m:Minister {name: $name, heading_number: $heading_number})
                SET m.gazette_id   = $gazette_id,
                    m.appointed_by = $appointed_by,
                    m.tenure_start = $tenure_start
            """,
            name=minister["heading_name"],
            heading_number=minister.get("heading_number"),
            gazette_id=gazette_id,
            appointed_by=data.get("president"),
            tenure_start=data.get("published_date"))

            # Gazette → Minister
            session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
                MATCH (m:Minister {name: $name})
                MERGE (g)-[r:HAS_MINISTER]->(m)
                SET r.gazette_id     = $gazette_id,
                    r.published_date = $published_date
            """,
            gazette_id=gazette_id,
            name=minister["heading_name"],
            published_date=data.get("published_date"))

            # Departments
            for dept in minister.get("departments", []):
                item_number, dept = extract_item_number(dept)

                session.run("""
                    MERGE (d:Department {name: $dept})
                    SET d.gazette_id   = $gazette_id,
                        d.tenure_start = $tenure_start,
                        d.item_number = $item_number
                """,
                dept=dept, gazette_id=gazette_id,
                tenure_start=data.get("published_date"),
                item_number=item_number
                )

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (d:Department {name: $dept})
                    MERGE (m)-[r:OVERSEES_DEPARTMENT]->(d)
                    SET r.gazette_id     = $gazette_id,
                        r.published_date = $published_date
                """,
                name=minister["heading_name"], 
                dept=dept,
                gazette_id=gazette_id,
                published_date=data.get("published_date"))

            # Laws
            for law in minister.get("laws", []):
                session.run("""
                    MERGE (l:Law {name: $law})
                    SET l.gazette_id   = $gazette_id,
                        l.tenure_start = $tenure_start
                """,
                law=law, gazette_id=gazette_id,
                tenure_start=data.get("published_date"))

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (l:Law {name: $law})
                    MERGE (m)-[r:RESPONSIBLE_FOR_LAW]->(l)
                    SET r.gazette_id     = $gazette_id,
                        r.published_date = $published_date
                """,
                name=minister["heading_name"], law=law,
                gazette_id=gazette_id,
                published_date=data.get("published_date"))

            # Functions
            for func in minister.get("functions", []):
                item_number, func = extract_item_number(func)

                session.run("""
                    MERGE (f:Function {description: $func})
                    SET f.gazette_id   = $gazette_id,
                        f.tenure_start = $tenure_start,
                        f.item_number = $item_number
                """,
                func=func, 
                gazette_id=gazette_id,
                tenure_start=data.get("published_date"),
                item_number=item_number
                )

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (f:Function {description: $func})
                    MERGE (m)-[r:PERFORMS_FUNCTION]->(f)
                    SET r.gazette_id     = $gazette_id,
                        r.published_date = $published_date
                """,
                name=minister["heading_name"], func=func,
                gazette_id=gazette_id,
                published_date=data.get("published_date"))

    print(f"✅ Base Gazette {gazette_id} loaded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    load_base_data(args.input)
