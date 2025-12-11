from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
pwd = os.getenv("NEO4J_PASSWORD")

drv = GraphDatabase.driver(uri, auth=(user, pwd))
q = (
    "MATCH (m:Minister {number:'04', gazette_id:'1897/15'})-"
    "[r:OVERSEES_DEPARTMENT]->(d:Department) "
    "RETURN d.item_number as num, d.name as name, coalesce(d.is_active,true) as active, "
    "coalesce(d.added_by,d.updated_by) as amend ORDER BY toInteger(num)"
)
with drv.session() as s:
    rows = s.run(q).data()
for row in rows:
    print(row)
print("count", len(rows))
drv.close()
