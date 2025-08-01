import json
import os
import argparse
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env file
load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def load_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        # Create Gazette node
        session.run("""
            MERGE (g:Gazette {gazette_id: $gazette_id})
            SET g.published_date = $published_date
        """, gazette_id=data["gazette_id"], published_date=data["published_date"])

        # Process Ministers
        for minister in data.get("ministers", []):
            session.run("""
                MERGE (m:Minister {name: $name})
            """, name=minister["name"])

            # Link Gazette -> Minister
            session.run("""
                MATCH (g:Gazette {gazette_id: $gazette_id})
                MATCH (m:Minister {name: $name})
                MERGE (g)-[:HAS_MINISTER]->(m)
            """, gazette_id=data["gazette_id"], name=minister["name"])

            # Departments
            for dept in minister.get("departments", []):
                session.run("""
                    MERGE (d:Department {name: $dept_name})
                """, dept_name=dept)

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (d:Department {name: $dept_name})
                    MERGE (m)-[:OVERSEES_DEPARTMENT]->(d)
                """, name=minister["name"], dept_name=dept)

            # Laws
            for law in minister.get("laws", []):
                session.run("""
                    MERGE (l:Law {name: $law_name})
                """, law_name=law)

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (l:Law {name: $law_name})
                    MERGE (m)-[:RESPONSIBLE_FOR_LAW]->(l)
                """, name=minister["name"], law_name=law)

            # Functions
            for func in minister.get("functions", []):
                session.run("""
                    MERGE (f:Function {description: $func_desc})
                """, func_desc=func)

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (f:Function {description: $func_desc})
                    MERGE (m)-[:PERFORMS_FUNCTION]->(f)
                """, name=minister["name"], func_desc=func)

    print(f"✅ Data from {json_path} loaded into Neo4j.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Doctracer JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to the JSON file")
    args = parser.parse_args()

    load_data(args.input)
