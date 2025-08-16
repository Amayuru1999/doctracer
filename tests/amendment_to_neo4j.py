import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def clear_amendment_data():
    """Clear existing amendment data"""
    with driver.session() as session:
        # Clear existing amendment data
        session.run("MATCH (n:AmendmentMinister) DETACH DELETE n")
        session.run("MATCH (n:AmendmentDepartment) DETACH DELETE n")
        session.run("MATCH (n:AmendmentLaw) DETACH DELETE n")
        session.run("MATCH (n:AmendmentFunction) DETACH DELETE n")
        print("🧹 Cleared existing amendment data")

def copy_base_data_to_amendment():
    """Copy base data to amendment labels for comparison"""
    with driver.session() as session:
        # Copy base gazette data
        session.run("""
            MATCH (g:BaseGazette)
            CREATE (g2:AmendmentGazette:Gazette)
            SET g2 = g, g2.source = 'amendment'
        """)
        
        # Copy base minister data
        session.run("""
            MATCH (m:BaseMinister)
            CREATE (m2:AmendmentMinister:Minister)
            SET m2 = m, m2.source = 'amendment'
        """)
        
        # Copy base department data
        session.run("""
            MATCH (d:BaseDepartment)
            CREATE (d2:AmendmentDepartment:Department)
            SET d2 = d, d2.source = 'amendment'
        """)
        
        # Copy base law data
        session.run("""
            MATCH (l:BaseLaw)
            CREATE (l2:AmendmentLaw:Law)
            SET l2 = l, l2.source = 'amendment'
        """)
        
        # Copy base function data
        session.run("""
            MATCH (f:BaseFunction)
            CREATE (f2:AmendmentFunction:Function)
            SET f2 = f, f2.source = 'amendment'
        """)
        
        # Copy relationships
        session.run("""
            MATCH (g:BaseGazette)-[r:HAS_MINISTER]->(m:BaseMinister)
            MATCH (g2:AmendmentGazette {gazette_id: g.gazette_id})
            MATCH (m2:AmendmentMinister {name: m.name})
            CREATE (g2)-[:HAS_MINISTER]->(m2)
        """)
        
        session.run("""
            MATCH (m:BaseMinister)-[r:OVERSEES_DEPARTMENT]->(d:BaseDepartment)
            MATCH (m2:AmendmentMinister {name: m.name})
            MATCH (d2:AmendmentDepartment {name: d.name})
            CREATE (m2)-[:OVERSEES_DEPARTMENT]->(d2)
        """)
        
        session.run("""
            MATCH (m:BaseMinister)-[r:RESPONSIBLE_FOR_LAW]->(l:BaseLaw)
            MATCH (m2:AmendmentMinister {name: m.name})
            MATCH (l2:AmendmentLaw {name: l.name})
            CREATE (m2)-[:RESPONSIBLE_FOR_LAW]->(l2)
        """)
        
        session.run("""
            MATCH (m:BaseMinister)-[r:PERFORMS_FUNCTION]->(f:BaseFunction)
            MATCH (m2:AmendmentMinister {name: m.name})
            MATCH (f2:AmendmentFunction {description: f.description})
            CREATE (m2)-[:PERFORMS_FUNCTION]->(f2)
        """)
        
        print("📋 Copied base data to amendment labels")

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
                    # Mark as deleted instead of removing
                    session.run("""
                        MATCH (m:AmendmentMinister {name: $name})-[r:RESPONSIBLE_FOR_LAW]->(l:AmendmentLaw {name: $section})
                        SET r.status = 'DELETED', r.amendment_date = datetime()
                    """, name=minister_name, section=section)
                    
                    session.run("""
                        MATCH (m:AmendmentMinister {name: $name})-[r:OVERSEES_DEPARTMENT]->(d:AmendmentDepartment {name: $section})
                        SET r.status = 'DELETED', r.amendment_date = datetime()
                    """, name=minister_name, section=section)
                    
                    session.run("""
                        MATCH (m:AmendmentMinister {name: $name})-[r:PERFORMS_FUNCTION]->(f:AmendmentFunction {description: $section})
                        SET r.status = 'DELETED', r.amendment_date = datetime()
                    """, name=minister_name, section=section)

            elif op_type == "INSERTION":
                session.run("""
                    MERGE (m:AmendmentMinister:Minister {name: $name})
                    SET m.source = 'amendment', m.amendment_date = datetime()
                """, name=minister_name)

                for item in details.get("subjects_and_functions", []):
                    # Decide if it's a Law or Department or Function
                    if "Act" in item or "Law" in item:
                        session.run("""
                            MERGE (l:AmendmentLaw:Law {name: $item})
                            SET l.source = 'amendment', l.amendment_date = datetime()
                            WITH l
                            MATCH (m:AmendmentMinister {name: $name})
                            MERGE (m)-[:RESPONSIBLE_FOR_LAW {status: 'ADDED', amendment_date: datetime()}]->(l)
                        """, name=minister_name, item=item)
                    elif "Board" in item or "Commission" in item or "Department" in item:
                        session.run("""
                            MERGE (d:AmendmentDepartment:Department {name: $item})
                            SET d.source = 'amendment', d.amendment_date = datetime()
                            WITH d
                            MATCH (m:AmendmentMinister {name: $name})
                            MERGE (m)-[:OVERSEES_DEPARTMENT {status: 'ADDED', amendment_date: datetime()}]->(d)
                        """, name=minister_name, item=item)
                    else:
                        session.run("""
                            MERGE (f:AmendmentFunction:Function {description: $item})
                            SET f.source = 'amendment', f.amendment_date = datetime()
                            WITH f
                            MATCH (m:AmendmentMinister {name: $name})
                            MERGE (m)-[:PERFORMS_FUNCTION {status: 'ADDED', amendment_date: datetime()}]->(f)
                        """, name=minister_name, item=item)

            elif op_type == "RENUMBERING":
                session.run("""
                    MATCH (m:AmendmentMinister {name: $name})
                    SET m.heading_number = $new_number, m.amendment_date = datetime()
                """, name=minister_name, new_number=details.get("new_number"))

    print(f"✅ Amendment from {json_path} applied to amendment labels")
    print("🌐 View at: http://localhost:7474")
    print("📊 Use Amendment* labels to filter amendment data")

def visualize_amendment_graph():
    """Generate Cypher queries to visualize the amendment graph"""
    queries = [
        "// View all amendment nodes",
        "MATCH (n:AmendmentGazette:AmendmentMinister:AmendmentDepartment:AmendmentLaw:AmendmentFunction) RETURN n LIMIT 100",
        "",
        "// View changes by status",
        "MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IS NOT NULL RETURN a, r, b",
        "",
        "// View added vs deleted relationships",
        "MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IN ['ADDED', 'DELETED'] RETURN a, r, b",
        "",
        "// Count nodes by source",
        "MATCH (n) WHERE n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction RETURN labels(n)[0] as NodeType, n.source as Source, count(n) as Count ORDER BY NodeType, Source",
        "",
        "// View amendment timeline",
        "MATCH (n) WHERE n.amendment_date IS NOT NULL RETURN n ORDER BY n.amendment_date DESC",
        "",
        "// Compare base vs amendment data",
        "MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction OR n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction RETURN labels(n)[0] as NodeType, n.source as Source, count(n) as Count ORDER BY NodeType, Source"
    ]
    
    print("\n🔍 Useful Cypher queries for amendment data:")
    for query in queries:
        print(query)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update Neo4j Amendment Graph with Gazette Amendments")
    parser.add_argument("--input", required=True, help="Path to amendment JSON file")
    parser.add_argument("--clear", action="store_true", help="Clear existing amendment data")
    parser.add_argument("--copy-base", action="store_true", help="Copy base data to amendment labels")
    args = parser.parse_args()

    if args.clear:
        clear_amendment_data()
    
    if args.copy_base:
        copy_base_data_to_amendment()
    
    update_graph_from_amendment(args.input)
    visualize_amendment_graph()
