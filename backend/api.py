from flask import Flask, jsonify, request
from neo4j import GraphDatabase
import os
import logging
from flask_cors import CORS
from urllib.parse import unquote

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"])

# Database configuration
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j123")

# Initialize Neo4j driver
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


@app.route("/gazettes", methods=["GET"])
def get_gazettes():
    logger.debug("Received request to get all gazettes")  # Log the request
    with driver.session() as session:
        result = session.run("""
            MATCH (g:BaseGazette)
            RETURN g.gazette_id AS gazette_id,
                   g.published_date AS published_date
            ORDER BY published_date
        """)

        gazettes = [record.data() for record in result]
        logger.debug(f"Fetched {len(gazettes)} gazettes from the database")  # Log number of gazettes fetched

        return jsonify(gazettes)


@app.route("/gazettes/<path:gazette_id>", methods=["GET"])
def get_gazette_details(gazette_id):
    decoded_gazette_id = unquote(gazette_id)  # Decode URL-encoded ID
    logger.debug(f"Decoded gazette_id: {decoded_gazette_id}")  # Log the decoded gazette_id

    with driver.session() as session:
        result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            RETURN g.gazette_id AS gazette_id, 
                   g.published_date AS published_date,
                   g.parent_gazette_id AS parent_gazette_id,
                   labels(g) AS labels
            LIMIT 1
        """, gazette_id=decoded_gazette_id)

        gazette_details = [record.data() for record in result]
        if not gazette_details:
            logger.warning(f"No data found for gazette_id: {decoded_gazette_id}")
        else:
            logger.debug(f"Fetched gazette details: {gazette_details}")
        return jsonify(gazette_details)


@app.route("/amendments", methods=["GET"])
def get_amendments():
    """Get all amendment gazettes"""
    logger.debug("Received request to get all amendments")
    with driver.session() as session:
        result = session.run("""
            MATCH (a:AmendmentGazette)
            RETURN a.gazette_id AS gazette_id,
                   a.published_date AS published_date,
                   a.parent_gazette_id AS parent_gazette_id
            ORDER BY a.published_date
        """)
        
        amendments = [record.data() for record in result]
        logger.debug(f"Fetched {len(amendments)} amendments from the database")
        return jsonify(amendments)


@app.route("/amendments/<path:amendment_id>/graph", methods=["GET"])
def get_amendment_graph(amendment_id):
    """Get graph data for a specific amendment showing relationships"""
    decoded_amendment_id = unquote(amendment_id)
    logger.debug(f"Getting graph for amendment: {decoded_amendment_id}")
    
    with driver.session() as session:
        # Get nodes and relationships for the amendment
        result = session.run("""
            MATCH (a:AmendmentGazette {gazette_id: $amendment_id})
            OPTIONAL MATCH (a)-[r]-(related)
            RETURN a, r, related
        """, amendment_id=decoded_amendment_id)
        
        nodes = []
        links = []
        node_ids = set()
        
        for record in result:
            # Add amendment node
            amendment_node = record['a']
            if amendment_node and amendment_node['gazette_id'] not in node_ids:
                nodes.append({
                    'id': amendment_node['gazette_id'],
                    'label': f"Amendment {amendment_node['gazette_id']}",
                    'kind': 'amendment',
                    'published_date': amendment_node.get('published_date'),
                    'parent_gazette_id': amendment_node.get('parent_gazette_id')
                })
                node_ids.add(amendment_node['gazette_id'])
            
            # Add related node
            related_node = record['related']
            if related_node and related_node['gazette_id'] not in node_ids:
                node_type = 'base' if 'BaseGazette' in related_node.labels else 'amendment'
                nodes.append({
                    'id': related_node['gazette_id'],
                    'label': f"{node_type.title()} {related_node['gazette_id']}",
                    'kind': node_type,
                    'published_date': related_node.get('published_date')
                })
                node_ids.add(related_node['gazette_id'])
            
            # Add relationship
            relationship = record['r']
            if relationship:
                links.append({
                    'source': amendment_node['gazette_id'],
                    'target': related_node['gazette_id'],
                    'kind': relationship.type
                })
        
        return jsonify({'nodes': nodes, 'links': links})


@app.route("/graph/complete", methods=["GET"])
def get_complete_graph():
    """Get complete graph showing all gazettes and their relationships"""
    logger.debug("Getting complete graph")
    
    with driver.session() as session:
        result = session.run("""
            MATCH (g:Gazette)
            OPTIONAL MATCH (g)-[r]-(related:Gazette)
            RETURN g, r, related
        """)
        
        nodes = []
        links = []
        node_ids = set()
        
        for record in result:
            # Add main node
            main_node = record['g']
            if main_node and main_node['gazette_id'] not in node_ids:
                node_type = 'base' if 'BaseGazette' in main_node.labels else 'amendment'
                nodes.append({
                    'id': main_node['gazette_id'],
                    'label': f"{node_type.title()} {main_node['gazette_id']}",
                    'kind': node_type,
                    'published_date': main_node.get('published_date'),
                    'parent_gazette_id': main_node.get('parent_gazette_id')
                })
                node_ids.add(main_node['gazette_id'])
            
            # Add related node
            related_node = record['related']
            if related_node and related_node['gazette_id'] not in node_ids:
                node_type = 'base' if 'BaseGazette' in related_node.labels else 'amendment'
                nodes.append({
                    'id': related_node['gazette_id'],
                    'label': f"{node_type.title()} {related_node['gazette_id']}",
                    'kind': node_type,
                    'published_date': related_node.get('published_date'),
                    'parent_gazette_id': related_node.get('parent_gazette_id')
                })
                node_ids.add(related_node['gazette_id'])
            
            # Add relationship
            relationship = record['r']
            if relationship:
                links.append({
                    'source': main_node['gazette_id'],
                    'target': related_node['gazette_id'],
                    'kind': relationship.type
                })
        
        return jsonify({'nodes': nodes, 'links': links})


@app.route("/gazettes/<path:gazette_id>/details", methods=["GET"])
def get_gazette_full_details(gazette_id):
    """Get detailed information about a gazette including all related entities"""
    decoded_gazette_id = unquote(gazette_id)
    logger.debug(f"Getting full details for gazette: {decoded_gazette_id}")
    
    with driver.session() as session:
        # Get gazette with all related entities
        result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            OPTIONAL MATCH (g)-[r]-(entity)
            WHERE entity:Gazette OR entity:Minister OR entity:Department OR entity:Law
            RETURN g, r, entity
        """, gazette_id=decoded_gazette_id)
        
        gazette_data = None
        entities = []
        relationships = []
        
        for record in result:
            if not gazette_data and record['g']:
                gazette_data = {
                    'gazette_id': record['g']['gazette_id'],
                    'published_date': record['g'].get('published_date'),
                    'parent_gazette_id': record['g'].get('parent_gazette_id'),
                    'type': 'base' if 'BaseGazette' in record['g'].labels else 'amendment'
                }
            
            if record['entity']:
                entity_type = 'gazette' if 'Gazette' in record['entity'].labels else \
                             'minister' if 'Minister' in record['entity'].labels else \
                             'department' if 'Department' in record['entity'].labels else \
                             'law' if 'Law' in record['entity'].labels else 'unknown'
                
                entities.append({
                    'id': record['entity'].get('gazette_id') or record['entity'].get('name'),
                    'type': entity_type,
                    'name': record['entity'].get('name') or record['entity'].get('gazette_id'),
                    'published_date': record['entity'].get('published_date')
                })
            
            if record['r']:
                relationships.append({
                    'type': record['r'].type,
                    'properties': dict(record['r'])
                })
        
        return jsonify({
            'gazette': gazette_data,
            'entities': entities,
            'relationships': relationships
        })


@app.route("/search", methods=["GET"])
def search_gazettes():
    """Search gazettes by various criteria"""
    query = request.args.get('q', '')
    gazette_type = request.args.get('type', 'all')  # all, base, amendment
    
    logger.debug(f"Searching for: {query}, type: {gazette_type}")
    
    with driver.session() as session:
        if gazette_type == 'base':
            match_clause = "MATCH (g:BaseGazette)"
        elif gazette_type == 'amendment':
            match_clause = "MATCH (g:AmendmentGazette)"
        else:
            match_clause = "MATCH (g:Gazette)"
        
        if query:
            cypher = f"""
                {match_clause}
                WHERE g.gazette_id CONTAINS $query OR g.published_date CONTAINS $query
                RETURN g.gazette_id AS gazette_id,
                       g.published_date AS published_date,
                       g.parent_gazette_id AS parent_gazette_id
                ORDER BY g.published_date DESC
                LIMIT 50
            """
            result = session.run(cypher, query=query)
        else:
            cypher = f"""
                {match_clause}
                RETURN g.gazette_id AS gazette_id,
                       g.published_date AS published_date,
                       g.parent_gazette_id AS parent_gazette_id
                ORDER BY g.published_date DESC
                LIMIT 50
            """
            result = session.run(cypher)
        
        gazettes = [record.data() for record in result]
        return jsonify(gazettes)


@app.route("/debug/nodes", methods=["GET"])
def debug_nodes():
    """Debug endpoint to see all nodes in the database"""
    logger.debug("Debug: Getting all nodes")
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            RETURN labels(n) AS labels, 
                   keys(n) AS properties,
                   n.gazette_id AS gazette_id,
                   n.published_date AS published_date,
                   n.parent_gazette_id AS parent_gazette_id
            LIMIT 20
        """)
        
        nodes = [record.data() for record in result]
        logger.debug(f"Debug: Found {len(nodes)} nodes")
        return jsonify(nodes)


@app.route("/debug/gazettes", methods=["GET"])
def debug_gazettes():
    """Debug endpoint to see all gazette nodes"""
    logger.debug("Debug: Getting all gazette nodes")
    with driver.session() as session:
        result = session.run("""
            MATCH (g:Gazette)
            RETURN g.gazette_id AS gazette_id,
                   g.published_date AS published_date,
                   g.parent_gazette_id AS parent_gazette_id,
                   labels(g) AS labels
        """)
        
        gazettes = [record.data() for record in result]
        logger.debug(f"Debug: Found {len(gazettes)} gazette nodes")
        return jsonify(gazettes)

if __name__ == "__main__":
    logger.info("Starting Flask app on port 5001")  # Log when the app starts
    app.run(port=5001, debug=True)