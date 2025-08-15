import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def update_graph_from_amendment(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changes = data.get("changes", [])
    with driver.session() as session:
        for change in changes:
            op_type = change.get("operation_type")
            details = change.get("details", {})
            minister_name = details.get("heading_name")

            if op_type == "DELETION":
                for section in details.get("deleted_sections", []):
                    # Try removing as a Law
                    session.run("""
                        MATCH (m:Minister {name: $name})-[r:RESPONSIBLE_FOR_LAW]->(l:Law {name: $section})
                        DELETE r
                    """, name=minister_name, section=section)
                    
                    # Try removing as a Department
                    session.run("""
                        MATCH (m:Minister {name: $name})-[r:OVERSEES_DEPARTMENT]->(d:Department {name: $section})
                        DELETE r
                    """, name=minister_name, section=section)
                    
                    # Try removing as a Function
                    session.run("""
                        MATCH (m:Minister {name: $name})-[r:PERFORMS_FUNCTION]->(f:Function {description: $section})
                        DELETE r
                    """, name=minister_name, section=section)

            elif op_type == "INSERTION":
                session.run("""
                    MERGE (m:Minister {name: $name})
                """, name=minister_name)

                for item in details.get("subjects_and_functions", []):
                    # Decide if it's a Law or Department or Function
                    if "Act" in item or "Law" in item:
                        session.run("""
                            MERGE (l:Law {name: $item})
                            WITH l
                            MATCH (m:Minister {name: $name})
                            MERGE (m)-[:RESPONSIBLE_FOR_LAW]->(l)
                        """, name=minister_name, item=item)
                    elif "Board" in item or "Commission" in item or "Department" in item:
                        session.run("""
                            MERGE (d:Department {name: $item})
                            WITH d
                            MATCH (m:Minister {name: $name})
                            MERGE (m)-[:OVERSEES_DEPARTMENT]->(d)
                        """, name=minister_name, item=item)
                    else:
                        session.run("""
                            MERGE (f:Function {description: $item})
                            WITH f
                            MATCH (m:Minister {name: $name})
                            MERGE (m)-[:PERFORMS_FUNCTION]->(f)
                        """, name=minister_name, item=item)

            elif op_type == "RENUMBERING":
                session.run("""
                    MATCH (m:Minister {name: $name})
                    SET m.heading_number = $new_number
                """, name=minister_name, new_number=details.get("new_number"))

    print(f"✅ Amendment from {json_path} applied to Neo4j.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update Neo4j with Gazette Amendments")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    args = parser.parse_args()

    update_graph_from_amendment(args.input)
