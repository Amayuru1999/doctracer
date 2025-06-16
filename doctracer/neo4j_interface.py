import os
from neo4j import GraphDatabase


class Neo4jInterface:
    def __init__(self, uri=None, user=None, password=None):
        uri = uri or os.getenv('NEO4J_URI')
        user = user or os.getenv('NEO4J_USER')
        password = password or os.getenv('NEO4J_PASSWORD')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query: str, parameters: dict = None):
        """
        Run an arbitrary Cypher query and return the raw records.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def create_change_event(self, change: dict):
        """
        Persist a single change event into the graph:
          - MERGE the Gazette node
          - MERGE the Minister node
          - MERGE the Entity (department/law/etc) node
          - CREATE a Change node with a UUID, type, and field
          - LINK the Change to Gazette, Minister, and Entity

        Requires the APOC plugin for apoc.create.uuid().
        """
        cypher = """
        MERGE (g:Gazette {id: $gazette_id})
          ON CREATE SET g.published_date = date($date)
        MERGE (m:Minister {name: $minister})
        MERGE (e:Entity  {name: $value})
        CREATE (c:Change {
          id: apoc.create.uuid(),
          type: $type,
          field: $field
        })
        CREATE (c)-[:IN_GAZETTE]->(g)
        CREATE (c)-[:AFFECTS_MINISTER]->(m)
        CREATE (c)-[:AFFECTS_ENTITY]->(e)
        """
        with self.driver.session() as session:
            session.run(cypher, change)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
