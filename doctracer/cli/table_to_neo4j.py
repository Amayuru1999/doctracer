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

def extract_item_number_and_name(item_str):
    match = re.match(r"^\s*(\d+)\.\s*(.+)$", item_str.strip())
    if match:
        return match.group(1), match.group(2)
    return None, item_str.strip()

def process_table(file_path: str, gazette_id: str, published_date: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        # Create BaseGazette node
        session.run("""
            MERGE (b:BaseGazette {gazette_id: $gazette_id})
            SET b.published_date = $published_date,
                b.published_by = $published_by,
                b.gazette_type = $gazette_type,
                b.language = $language,
                b.pdf_url = $pdf_url
        """,
            gazette_id=data.get("gazette_id"),
            published_date=data.get("published_date"),
            published_by=data.get("published_by"),
            gazette_type=data.get("gazette_type"),
            language=data.get("language"),
            pdf_url=data.get("pdf_url")
        )
        
        for minister in data.get("ministers", []):
            minister_name = minister.get("name")
            minister_number = minister.get("number")

            # Minister node
            session.run(
                """
                MERGE (m:Minister {name: $minister_name, number: $minister_number})
                """,
                minister_name=minister_name,
                minister_number=minister_number,
            )

            # Functions (Column I)
            for func_str in minister.get("functions", []):
                item_number, item_name = extract_item_number_and_name(func_str)
                session.run(
                    """
                    MERGE (f:Function {item_number: coalesce($item_number, 'N/A'), name: $item_name})
                    SET f.created_in = $gazette_id,
                        f.tenure_start = $published_date
                    WITH f
                    MATCH (m:Minister {name: $minister_name, number: $minister_number})
                    MERGE (m)-[:HAS_FUNCTION]->(f)
                    """,
                    item_number=item_number,
                    item_name=item_name,
                    gazette_id=gazette_id,
                    published_date=published_date,
                    minister_name=minister_name,
                    minister_number=minister_number,
                )

            # Departments (Column II)
            for dept_str in minister.get("departments", []):
                item_number, item_name = extract_item_number_and_name(dept_str)
                session.run(
                    """
                    MERGE (d:Department {item_number: coalesce($item_number, 'N/A'), name: $item_name})
                    SET d.created_in = $gazette_id,
                        d.tenure_start = $published_date
                    WITH d
                    MATCH (m:Minister {name: $minister_name, number: $minister_number})
                    MERGE (m)-[:OVERSEES]->(d)
                    """,
                    item_number=item_number,
                    item_name=item_name,
                    gazette_id=gazette_id,
                    published_date=published_date,
                    minister_name=minister_name,
                    minister_number=minister_number,
                )

            # Laws (Column III)
            for law_name in minister.get("laws", []):
                session.run(
                    """
                    MERGE (l:Law {name: $law_name})
                    SET l.created_in = $gazette_id,
                        l.tenure_start = $published_date
                    WITH l
                    MATCH (m:Minister {name: $minister_name, number: $minister_number})
                    MERGE (m)-[:ENFORCES]->(l)
                    """,
                    law_name=law_name,
                    gazette_id=gazette_id,
                    published_date=published_date,
                    minister_name=minister_name,
                    minister_number=minister_number,
                )

    print(f"✅ Base Gazette {gazette_id} loaded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to table gazette JSON")
    parser.add_argument("--gazette_id", required=True)
    parser.add_argument("--published_date", required=True)
    args = parser.parse_args()

    process_table(args.input, args.gazette_id, args.published_date)