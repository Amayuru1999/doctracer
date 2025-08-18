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

def load_base_data(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        # Create Gazette node
        session.run("""
            MERGE (g:Gazette {gazette_id: $gazette_id})
            SET g.published_date = $published_date,
                g.published_by = $published_by,
                g.president = $president,
                g.gazette_type = $gazette_type,
                g.language = $language,
                g.pdf_url = $pdf_url
                    
        """, 
            gazette_id=data["gazette_id"], 
            published_date=data.get("published_date"),
            published_by=data.get("published_by"),
            president=data.get("president"),
            gazette_type=data.get("gazette_type"),
            language=data.get("language"),
            pdf_url=data.get("pdf_url")
            )

        # Process Ministers
        for minister in data.get("ministers", []):
            session.run("""
                MERGE (m:Minister {name: $name})
                SET m.heading_number = $heading_number,
                    m.gazette_id = $gazette_id,
                    m.appointed_by = $appointed_by,
                    m.tenure_start = $tenure_start
            """, 
                name=minister["name"],
                heading_number=minister.get("heading_number"),
                gazette_id=data["gazette_id"],
                appointed_by=data.get("president", None),
                tenure_start=data.get("published_date", None)
            )

            # Link Gazette -> Minister
            session.run("""
                MATCH (g:Gazette {gazette_id: $gazette_id})
                MATCH (m:Minister {name: $name})
                MERGE (g)-[r:HAS_MINISTER]->(m)
                SET r.published_date = $published_date,
                    r.gazette_type = $gazette_type,
                    r.published_by = $published_by,
                    r.president = $president
            """, 
            gazette_id=data["gazette_id"],
            name=minister["name"],
            published_date=data.get("published_date"),
            gazette_type=data.get("gazette_type"),
            published_by=data.get("published_by"),
            president=data.get("president")
            )
            
            # Departments
            for dept in minister.get("departments", []):
                session.run("""
                    MERGE (d:Department {name: $dept_name})
                    SET d.gazette_id = $gazette_id,
                        d.appointed_by = $appointed_by,
                        d.tenure_start = $tenure_start
                """, 
                dept_name=dept,
                gazette_id=data["gazette_id"],
                appointed_by=data.get("president", None),
                tenure_start=data.get("published_date", None)
                )

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (d:Department {name: $dept_name})
                    MERGE (m)-[r:OVERSEES_DEPARTMENT]->(d)
                    SET r.gazette_id = $gazette_id,
                        r.published_date = $published_date,
                        r.gazette_type = $gazette_type,
                        r.published_by = $published_by,
                        r.president = $president
                """, 
                name=minister["name"],
                dept_name=dept,
                gazette_id=data["gazette_id"],
                published_date=data.get("published_date"),
                gazette_type=data.get("gazette_type"),
                published_by=data.get("published_by"),
                president=data.get("president")
                )

            # Laws
            for law in minister.get("laws", []):
                session.run("""
                    MERGE (l:Law {name: $law_name})
                    SET l.gazette_id = $gazette_id,
                        l.appointed_by = $appointed_by,
                        l.tenure_start = $tenure_start
                """, 
                law_name=law,
                gazette_id=data["gazette_id"],
                appointed_by=data.get("president", None),
                tenure_start=data.get("published_date", None)
                )

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (l:Law {name: $law_name})
                    MERGE (m)-[r:RESPONSIBLE_FOR_LAW]->(l)
                    SET r.gazette_id = $gazette_id,
                        r.published_date = $published_date,
                        r.gazette_type = $gazette_type,
                        r.published_by = $published_by,
                        r.president = $president
                """, 
                name=minister["name"], 
                law_name=law,
                gazette_id=data["gazette_id"],
                published_date=data.get("published_date"),
                gazette_type=data.get("gazette_type"),
                published_by=data.get("published_by"),
                president=data.get("president")
                )

            # Functions
            for func in minister.get("functions", []):
                session.run("""
                    MERGE (f:Function {description: $func_desc})
                    SET f.gazette_id = $gazette_id,
                        f.appointed_by = $appointed_by,
                        f.tenure_start = $tenure_start
                """, 
                func_desc=func,
                gazette_id=data["gazette_id"],
                appointed_by=data.get("president", None),
                tenure_start=data.get("published_date", None)
                )

                session.run("""
                    MATCH (m:Minister {name: $name})
                    MATCH (f:Function {description: $func_desc})
                    MERGE (m)-[r:PERFORMS_FUNCTION]->(f)
                    SET r.gazette_id = $gazette_id,
                        r.published_date = $published_date,
                        r.gazette_type = $gazette_type,
                        r.published_by = $published_by,
                        r.president = $president                    
                            
                """, 
                name=minister["name"], 
                func_desc=func,
                gazette_id=data["gazette_id"],
                published_date=data.get("published_date"),
                gazette_type=data.get("gazette_type"),
                published_by=data.get("published_by"),
                president=data.get("president")
                )

    print(f"✅ Data from {json_path} loaded into Neo4j.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Doctracer JSON into Neo4j")
    parser.add_argument("--input", required=True, help="Path to the JSON file")
    args = parser.parse_args()

    load_base_data(args.input)
