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

def clear_base_data():
    """Clear existing base gazette data"""
    with driver.session() as session:
        # Clear existing base data
        session.run("MATCH (n:BaseGazette) DETACH DELETE n")
        session.run("MATCH (n:BaseMinister) DETACH DELETE n")
        session.run("MATCH (n:BaseDepartment) DETACH DELETE n")
        session.run("MATCH (n:BaseLaw) DETACH DELETE n")
        session.run("MATCH (n:BaseFunction) DETACH DELETE n")
        print("🧹 Cleared existing base data")

def load_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        # Create Gazette node with BaseGazette label
        session.run("""
            CREATE (g:BaseGazette:Gazette {gazette_id: $gazette_id, published_date: $published_date, source: 'base'})
        """, gazette_id=data["gazette_id"], published_date=data["published_date"])

        # Process Ministers
        for minister in data.get("ministers", []):
            session.run("""
                CREATE (m:BaseMinister:Minister {name: $name, source: 'base'})
            """, name=minister["name"])

            # Link Gazette -> Minister
            session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
                MATCH (m:BaseMinister {name: $name})
                CREATE (g)-[:HAS_MINISTER]->(m)
            """, gazette_id=data["gazette_id"], name=minister["name"])

            # Departments
            for dept in minister.get("departments", []):
                session.run("""
                    CREATE (d:BaseDepartment:Department {name: $dept_name, source: 'base'})
                """, dept_name=dept)

                session.run("""
                    MATCH (m:BaseMinister {name: $name})
                    MATCH (d:BaseDepartment {name: $dept_name})
                    CREATE (m)-[:OVERSEES_DEPARTMENT]->(d)
                """, name=minister["name"], dept_name=dept)

            # Laws
            for law in minister.get("laws", []):
                session.run("""
                    CREATE (l:BaseLaw:Law {name: $law_name, source: 'base'})
                """, law_name=law)

                session.run("""
                    MATCH (m:BaseMinister {name: $name})
                    MATCH (l:BaseLaw {name: $law_name})
                    CREATE (m)-[:RESPONSIBLE_FOR_LAW]->(l)
                """, name=minister["name"], law_name=law)

            # Functions
            for func in minister.get("functions", []):
                session.run("""
                    CREATE (f:BaseFunction:Function {description: $func_desc, source: 'base'})
                """, func_desc=func)

                session.run("""
                    MATCH (m:BaseMinister {name: $name})
                    MATCH (f:BaseFunction {description: $func_desc})
                    CREATE (m)-[:PERFORMS_FUNCTION]->(f)
                """, name=minister["name"], func_desc=func)

    print(f"✅ Base data from {json_path} loaded into Neo4j with Base* labels")
    print("🌐 View at: http://localhost:7474")
    print("📊 Use Base* labels to filter base data")

def visualize_base_graph():
    """Generate Cypher queries to visualize the base graph"""
    queries = [
        "// View all base nodes",
        "MATCH (n:BaseGazette:BaseMinister:BaseDepartment:BaseLaw:BaseFunction) RETURN n LIMIT 100",
        "",
        "// View base government structure",
        "MATCH (m:BaseMinister)-[r]->(n) RETURN m, r, n",
        "",
        "// Count base nodes by type",
        "MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC",
        "",
        "// View base ministers and their responsibilities",
        "MATCH (m:BaseMinister) OPTIONAL MATCH (m)-[r]->(n) RETURN m, r, n"
    ]

    print("\n🔍 Useful Cypher queries for base data:")
    for query in queries:
        print(query)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Doctracer JSON into Neo4j Base Graph")
    parser.add_argument("--input", required=True, help="Path to the JSON file")
    parser.add_argument("--clear", action="store_true", help="Clear existing base data")
    args = parser.parse_args()

    if args.clear:
        clear_base_data()

    load_data(args.input)
    visualize_base_graph()
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
                    MERGE (f:Function {item_number: $item_number, name: $item_name})
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
                    MERGE (d:Department {item_number: $item_number, name: $item_name})
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