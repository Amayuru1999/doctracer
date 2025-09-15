from flask import Flask, jsonify
from neo4j import GraphDatabase
import os

app = Flask(__name__)
# server side
from flask_cors import CORS
CORS(app)  # after app = Flask(__name__)


URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j123")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

@app.route("/gazettes", methods=["GET"])
def get_gazettes():
    with driver.session() as session:
        result = session.run("""
            MATCH (g:BaseGazette)
            RETURN g.gazette_id AS gazette_id,
                   g.published_date AS published_date
            ORDER BY published_date
        """)
        return jsonify([record.data() for record in result])

@app.route("/gazettes/<gazette_id>", methods=["GET"])
def get_gazette_details(gazette_id):
    with driver.session() as session:
        result = session.run("""
            MATCH (g:BaseGazette {gazette_id: $gazette_id})
                  -[:HAS_MINISTER]->(m:BaseMinister)
            OPTIONAL MATCH (m)-[:OVERSEES_DEPARTMENT]->(d:BaseDepartment)
            OPTIONAL MATCH (m)-[:RESPONSIBLE_FOR_LAW]->(l:BaseLaw)
            OPTIONAL MATCH (m)-[:PERFORMS_FUNCTION]->(f:BaseFunction)
            RETURN g.gazette_id AS gazette_id, g.published_date AS published_date,
                   m.name AS minister, collect(DISTINCT d.name) AS departments,
                   collect(DISTINCT l.name) AS laws,
                   collect(DISTINCT f.description) AS functions
        """, gazette_id=gazette_id)
        return jsonify([record.data() for record in result])

if __name__ == "__main__":
    app.run(port=5001, debug=True)
