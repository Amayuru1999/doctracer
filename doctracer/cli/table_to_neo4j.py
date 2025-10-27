import json
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def extract_item_number_and_name(item_str):
    """Return (item_number (str) or None, item_name (str))."""
    if not item_str:
        return None, None
    s = item_str.strip()
    m = re.match(r"^\s*(\d+)\.\s*(.+)$", s)
    if m:
        return str(m.group(1)), m.group(2).strip()
    return None, s


def load_table_data(file_path: str):
    """Load a single base gazette JSON file into Neo4j."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gazette_id = data.get("gazette_id")
    published_date = data.get("published_date")
    published_by = data.get("published_by")
    gazette_type = data.get("gazette_type")
    language = data.get("language")
    pdf_url = data.get("pdf_url")
    president = data.get("president")

    if not gazette_id:
        raise ValueError(f"Missing gazette_id in base JSON: {file_path}")

    with driver.session() as session:
        # Base Gazette
        session.run(
            """
            MERGE (b:BaseGazette {gazette_id: $gazette_id})
            SET b.published_date = $published_date,
                b.published_by = $published_by,
                b.gazette_type = $gazette_type,
                b.language = $language,
                b.pdf_url = $pdf_url,
                b.president = $president
            """,
            gazette_id=gazette_id,
            published_date=published_date,
            published_by=published_by,
            gazette_type=gazette_type,
            language=language,
            pdf_url=pdf_url,
            president=president,
        )

        for minister in data.get("ministers", []):
            minister_name = minister.get("name")
            minister_number = str(minister.get("number")) if minister.get("number") is not None else None

            if not minister_number:
                print(f"⚠️ Skipping minister without number: {minister_name}")
                continue

            # Minister node
            session.run(
                """
                MERGE (m:Minister {number: $minister_number})
                SET m.name = $minister_name
                WITH m
                MATCH (b:BaseGazette {gazette_id: $gazette_id})
                MERGE (b)-[:HAS_MINISTER]->(m)
                """,
                minister_number=minister_number,
                minister_name=minister_name,
                gazette_id=gazette_id,
            )

            # Functions
            for func_str in minister.get("functions", []):
                item_number, item_name = extract_item_number_and_name(func_str)
                if item_number:
                    session.run(
                        """
                        MATCH (m:Minister {number: $minister_number})
                        MERGE (f:Function {item_number: $item_number})
                        ON CREATE SET f.name = $item_name, f.created_in = $gazette_id, f.added_date = $published_date
                        ON MATCH SET f.name = coalesce(f.name, $item_name)
                        MERGE (m)-[:HAS_FUNCTION]->(f)
                        """,
                        minister_number=minister_number,
                        item_number=item_number,
                        item_name=item_name,
                        gazette_id=gazette_id,
                        published_date=published_date,
                    )
                else:
                    session.run(
                        """
                        MATCH (m:Minister {number: $minister_number})
                        MERGE (f:Function {name: $item_name, minister_ref: $minister_number})
                        ON CREATE SET f.created_in = $gazette_id, f.added_date = $published_date
                        MERGE (m)-[:HAS_FUNCTION]->(f)
                        """,
                        minister_number=minister_number,
                        item_name=item_name,
                        gazette_id=gazette_id,
                        published_date=published_date,
                    )

            # Departments
            for dept_str in minister.get("departments", []):
                item_number, item_name = extract_item_number_and_name(dept_str)
                if item_number:
                    session.run(
                        """
                        MATCH (m:Minister {number: $minister_number})
                        MERGE (d:Department {item_number: $item_number})
                        ON CREATE SET d.name = $item_name, d.created_in = $gazette_id, d.added_date = $published_date
                        ON MATCH SET d.name = coalesce(d.name, $item_name)
                        MERGE (m)-[:OVERSEES_DEPARTMENT]->(d)
                        """,
                        minister_number=minister_number,
                        item_number=item_number,
                        item_name=item_name,
                        gazette_id=gazette_id,
                        published_date=published_date,
                    )
                else:
                    session.run(
                        """
                        MATCH (m:Minister {number: $minister_number})
                        MERGE (d:Department {name: $item_name, minister_ref: $minister_number})
                        ON CREATE SET d.created_in = $gazette_id, d.added_date = $published_date
                        MERGE (m)-[:OVERSEES_DEPARTMENT]->(d)
                        """,
                        minister_number=minister_number,
                        item_name=item_name,
                        gazette_id=gazette_id,
                        published_date=published_date,
                    )

            # Laws
            for law_name in minister.get("laws", []):
                name = law_name.strip()
                if not name:
                    continue
                session.run(
                    """
                    MATCH (m:Minister {number: $minister_number})
                    MERGE (l:Law {name: $law_name})
                    ON CREATE SET l.created_in = $gazette_id, l.added_date = $published_date
                    MERGE (m)-[:RESPONSIBLE_FOR_LAW]->(l)
                    """,
                    minister_number=minister_number,
                    law_name=name,
                    gazette_id=gazette_id,
                    published_date=published_date,
                )

    print(f"✅ Base Gazette {gazette_id} loaded/updated.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load a single base gazette JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to base gazette JSON")
    args = parser.parse_args()
    load_table_data(args.input)
