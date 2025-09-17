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


@app.route("/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    """Get summary statistics for dashboard"""
    logger.debug("Getting dashboard summary")
    with driver.session() as session:
        # Get counts
        result = session.run("""
            MATCH (g:Gazette)
            WITH labels(g) as nodeLabels, count(g) as count
            UNWIND nodeLabels as label
            WITH label, sum(count) as total
            WHERE label IN ['BaseGazette', 'AmendmentGazette']
            RETURN label, total
        """)
        
        counts = {record['label']: record['total'] for record in result}
        
        # Get recent gazettes (distinct to avoid duplicates)
        recent_result = session.run("""
            MATCH (g:Gazette)
            RETURN DISTINCT g.gazette_id AS gazette_id,
                   g.published_date AS published_date,
                   g.parent_gazette_id AS parent_gazette_id,
                   labels(g) AS labels
            ORDER BY g.published_date DESC
            LIMIT 10
        """)
        
        recent_gazettes = [record.data() for record in recent_result]
        
        return jsonify({
            'counts': counts,
            'recent_gazettes': recent_gazettes
        })


@app.route("/gazettes/<path:gazette_id>/structure", methods=["GET"])
def get_gazette_structure(gazette_id):
    """Get government structure for a specific gazette"""
    try:
        decoded_gazette_id = unquote(gazette_id)
        logger.debug(f"Getting structure for gazette: {decoded_gazette_id}")
        
        with driver.session() as session:
            # First check if the gazette exists
            check_result = session.run("""
                MATCH (g:Gazette {gazette_id: $gazette_id})
                RETURN g
            """, gazette_id=decoded_gazette_id)
            
            gazette_exists = check_result.single()
            if not gazette_exists:
                logger.warning(f"Gazette {decoded_gazette_id} not found")
                return jsonify({
                    'gazette_id': decoded_gazette_id,
                    'ministers': [],
                    'departments': [],
                    'laws': [],
                    'raw_entities': [],
                    'error': 'Gazette not found'
                })
            
            # Get all related entities
            result = session.run("""
                MATCH (g:Gazette {gazette_id: $gazette_id})
                OPTIONAL MATCH (g)-[r]-(entity)
                WHERE entity:BaseMinister OR entity:BaseDepartment OR entity:BaseLaw OR
                      entity:AmendmentMinister OR entity:AmendmentDepartment OR entity:AmendmentLaw
                RETURN g, r, entity, labels(entity) as entity_labels
            """, gazette_id=decoded_gazette_id)
            
            structure = {
                'gazette_id': decoded_gazette_id,
                'ministers': [],
                'departments': [],
                'laws': [],
                'raw_entities': []
            }
            
            ministers_map = {}
            departments_set = set()
            laws_set = set()
            
            for record in result:
                entity = record['entity']
                if entity:
                    entity_labels = record['entity_labels']
                    entity_data = {
                        'name': entity.get('name', entity.get('gazette_id', 'Unknown')),
                        'labels': entity_labels,
                        'properties': dict(entity)
                    }
                    structure['raw_entities'].append(entity_data)
                    
                    # Categorize entities
                    if 'BaseMinister' in entity_labels or 'AmendmentMinister' in entity_labels:
                        minister_name = entity.get('name', 'Unknown')
                        if minister_name not in ministers_map:
                            ministers_map[minister_name] = {
                                'name': minister_name,
                                'departments': [],
                                'laws': [],
                                'functions': []
                            }
                    elif 'BaseDepartment' in entity_labels or 'AmendmentDepartment' in entity_labels:
                        dept_name = entity.get('name', 'Unknown')
                        departments_set.add(dept_name)
                    elif 'BaseLaw' in entity_labels or 'AmendmentLaw' in entity_labels:
                        law_name = entity.get('name', 'Unknown')
                        laws_set.add(law_name)
            
            # Get detailed relationships for ministers
            for minister_name in ministers_map.keys():
                minister_result = session.run("""
                    MATCH (g:Gazette {gazette_id: $gazette_id})
                    MATCH (m {name: $minister_name})
                    WHERE m:BaseMinister OR m:AmendmentMinister
                    OPTIONAL MATCH (m)-[r1:OVERSEES_DEPARTMENT]-(d)
                    WHERE d:BaseDepartment OR d:AmendmentDepartment
                    OPTIONAL MATCH (m)-[r2:RESPONSIBLE_FOR_LAW]-(l)
                    WHERE l:BaseLaw OR l:AmendmentLaw
                    RETURN m, d, l, r1, r2
                """, gazette_id=decoded_gazette_id, minister_name=minister_name)
                
                for record in minister_result:
                    if record['d']:
                        dept_name = record['d'].get('name', 'Unknown')
                        if dept_name not in ministers_map[minister_name]['departments']:
                            ministers_map[minister_name]['departments'].append(dept_name)
                    
                    if record['l']:
                        law_name = record['l'].get('name', 'Unknown')
                        if law_name not in ministers_map[minister_name]['laws']:
                            ministers_map[minister_name]['laws'].append(law_name)
            
            structure['ministers'] = list(ministers_map.values())
            structure['departments'] = list(departments_set)
            structure['laws'] = list(laws_set)
            
            logger.debug(f"Structure for {decoded_gazette_id}: {len(structure['ministers'])} ministers, {len(structure['departments'])} departments, {len(structure['laws'])} laws")
            return jsonify(structure)
            
    except Exception as e:
        logger.error(f"Error getting structure for gazette {gazette_id}: {str(e)}")
        return jsonify({
            'gazette_id': gazette_id,
            'ministers': [],
            'departments': [],
            'laws': [],
            'raw_entities': [],
            'error': str(e)
        }), 500




@app.route("/network/government-evolution", methods=["GET"])
def get_government_structure_evolution():
    """Get government structure evolution showing changes over time"""
    logger.debug("Getting government structure evolution")
    
    with driver.session() as session:
        # Get all gazettes ordered by date with their structure
        result = session.run("""
            MATCH (g:Gazette)
            OPTIONAL MATCH (g)-[r1]-(m)
            WHERE m:BaseMinister OR m:AmendmentMinister
            OPTIONAL MATCH (m)-[r2:OVERSEES_DEPARTMENT]-(d)
            WHERE d:BaseDepartment OR d:AmendmentDepartment
            OPTIONAL MATCH (m)-[r3:RESPONSIBLE_FOR_LAW]-(l)
            WHERE l:BaseLaw OR l:AmendmentLaw
            RETURN g, m, d, l, r1, r2, r3
            ORDER BY g.published_date
        """)
        
        # Group by gazette to build timeline
        gazette_structures = {}
        
        for record in result:
            gazette = record['g']
            if not gazette:
                continue
                
            gazette_id = gazette['gazette_id']
            if gazette_id not in gazette_structures:
                gazette_structures[gazette_id] = {
                    'gazette': {
                        'id': gazette_id,
                        'published_date': gazette.get('published_date'),
                        'type': 'base' if 'BaseGazette' in gazette.labels else 'amendment',
                        'parent_gazette_id': gazette.get('parent_gazette_id')
                    },
                    'ministers': {},
                    'departments': set(),
                    'laws': set()
                }
            
            # Add minister
            minister = record['m']
            if minister:
                minister_name = minister['name']
                if minister_name not in gazette_structures[gazette_id]['ministers']:
                    gazette_structures[gazette_id]['ministers'][minister_name] = {
                        'name': minister_name,
                        'departments': set(),
                        'laws': set()
                    }
                
                # Add department
                department = record['d']
                if department:
                    dept_name = department['name']
                    gazette_structures[gazette_id]['ministers'][minister_name]['departments'].add(dept_name)
                    gazette_structures[gazette_id]['departments'].add(dept_name)
                
                # Add law
                law = record['l']
                if law:
                    law_name = law['name']
                    gazette_structures[gazette_id]['ministers'][minister_name]['laws'].add(law_name)
                    gazette_structures[gazette_id]['laws'].add(law_name)
        
        # Convert sets to lists and build evolution data
        evolution_data = []
        for gazette_id, structure in gazette_structures.items():
            # Convert sets to lists
            structure['departments'] = list(structure['departments'])
            structure['laws'] = list(structure['laws'])
            for minister in structure['ministers'].values():
                minister['departments'] = list(minister['departments'])
                minister['laws'] = list(minister['laws'])
            
            evolution_data.append({
                'gazette': structure['gazette'],
                'structure': {
                    'ministers': list(structure['ministers'].values()),
                    'departments': structure['departments'],
                    'laws': structure['laws']
                }
            })
        
        # Sort by published date
        evolution_data.sort(key=lambda x: x['gazette']['published_date'] or '')
        
        return jsonify({
            'evolution': evolution_data,
            'total_gazettes': len(evolution_data)
        })


@app.route("/network/government-evolution/<path:base_gazette_id>", methods=["GET"])
def get_government_evolution_from_base(base_gazette_id):
    """Get government structure evolution starting from a specific base gazette"""
    decoded_base_id = unquote(base_gazette_id)
    logger.debug(f"Getting government evolution from base gazette: {decoded_base_id}")
    
    with driver.session() as session:
        # Simplified query - get base gazette and its immediate amendments only
        result = session.run("""
            MATCH (base:Gazette {gazette_id: $base_id})
            OPTIONAL MATCH (base)<-[:AMENDS]-(amendment:Gazette)
            WITH base, collect(amendment) as amendments
            UNWIND [base] + amendments as g
            RETURN DISTINCT g.gazette_id as gazette_id, 
                   g.published_date as published_date,
                   labels(g) as labels
            ORDER BY g.published_date
        """, base_id=decoded_base_id)
        
        # Build simple evolution data
        evolution_data = []
        for record in result:
            gazette_id = record['gazette_id']
            published_date = record['published_date']
            labels = record['labels']
            
            evolution_data.append({
                'gazette': {
                    'id': gazette_id,
                    'published_date': published_date,
                    'type': 'base' if 'BaseGazette' in labels else 'amendment'
                },
                'structure': {
                    'ministers': [],
                    'departments': [],
                    'laws': []
                }
            })
        
        # Sort by published date
        evolution_data.sort(key=lambda x: x['gazette']['published_date'] or '')
        
        # Calculate simple changes between consecutive gazettes
        changes = []
        for i in range(1, len(evolution_data)):
            prev = evolution_data[i-1]
            curr = evolution_data[i]
            
            change = {
                'from_gazette': prev['gazette']['id'],
                'to_gazette': curr['gazette']['id'],
                'added_ministers': [],
                'removed_ministers': [],
                'modified_ministers': [],
                'added_departments': [],
                'removed_departments': [],
                'added_laws': [],
                'removed_laws': []
            }
            changes.append(change)
        
        return jsonify({
            'base_gazette': decoded_base_id,
            'evolution': evolution_data,
            'changes': changes,
            'total_gazettes': len(evolution_data)
        })


@app.route("/gazettes/<path:base_gazette_id>/compare/<path:amendment_gazette_id>", methods=["GET"])
def compare_gazette_structures(base_gazette_id, amendment_gazette_id):
    """Compare government structure between base and amendment gazettes"""
    decoded_base_id = unquote(base_gazette_id)
    decoded_amendment_id = unquote(amendment_gazette_id)
    logger.debug(f"Comparing structures: {decoded_base_id} vs {decoded_amendment_id}")
    
    with driver.session() as session:
        # Get base gazette structure
        base_result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            OPTIONAL MATCH (g)-[r]-(entity)
            RETURN g, r, entity, labels(entity) as entity_labels
        """, gazette_id=decoded_base_id)
        
        # Get amendment gazette structure
        amendment_result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            OPTIONAL MATCH (g)-[r]-(entity)
            RETURN g, r, entity, labels(entity) as entity_labels
        """, gazette_id=decoded_amendment_id)
        
        def process_gazette_data(result):
            ministers_map = {}
            departments_set = set()
            laws_set = set()
            raw_entities = []
            
            for record in result:
                entity = record['entity']
                if entity:
                    entity_labels = record['entity_labels']
                    entity_data = {
                        'name': entity.get('name', entity.get('gazette_id', 'Unknown')),
                        'labels': entity_labels,
                        'properties': dict(entity)
                    }
                    raw_entities.append(entity_data)
                    
                    if 'Minister' in entity_labels:
                        minister_name = entity.get('name', 'Unknown')
                        if minister_name not in ministers_map:
                            ministers_map[minister_name] = {
                                'name': minister_name,
                                'departments': [],
                                'laws': [],
                                'functions': []
                            }
                    elif 'Department' in entity_labels:
                        dept_name = entity.get('name', 'Unknown')
                        departments_set.add(dept_name)
                    elif 'Law' in entity_labels:
                        law_name = entity.get('name', 'Unknown')
                        laws_set.add(law_name)
            
            return {
                'ministers': list(ministers_map.values()),
                'departments': list(departments_set),
                'laws': list(laws_set),
                'raw_entities': raw_entities
            }
        
        base_structure = process_gazette_data(base_result)
        amendment_structure = process_gazette_data(amendment_result)
        
        # Calculate differences
        base_ministers = {m['name']: m for m in base_structure['ministers']}
        amendment_ministers = {m['name']: m for m in amendment_structure['ministers']}
        
        added_ministers = [m for name, m in amendment_ministers.items() if name not in base_ministers]
        removed_ministers = [m for name, m in base_ministers.items() if name not in amendment_ministers]
        modified_ministers = []
        
        for name in base_ministers:
            if name in amendment_ministers:
                base_m = base_ministers[name]
                amendment_m = amendment_ministers[name]
                
                changes = {
                    'name': name,
                    'base': base_m,
                    'amendment': amendment_m,
                    'changes': []
                }
                
                # Check for changes in departments
                base_depts = set(base_m['departments'])
                amendment_depts = set(amendment_m['departments'])
                if base_depts != amendment_depts:
                    changes['changes'].append({
                        'type': 'departments',
                        'added': list(amendment_depts - base_depts),
                        'removed': list(base_depts - amendment_depts)
                    })
                
                # Check for changes in laws
                base_laws = set(base_m['laws'])
                amendment_laws = set(amendment_m['laws'])
                if base_laws != amendment_laws:
                    changes['changes'].append({
                        'type': 'laws',
                        'added': list(amendment_laws - base_laws),
                        'removed': list(base_laws - amendment_laws)
                    })
                
                if changes['changes']:
                    modified_ministers.append(changes)
        
        # Get government titles (president names) for both gazettes
        base_title_result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            RETURN g.president AS president, g.published_date AS published_date
        """, gazette_id=decoded_base_id)
        
        amendment_title_result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            RETURN g.president AS president, g.published_date AS published_date
        """, gazette_id=decoded_amendment_id)
        
        base_title = base_title_result.single()
        amendment_title = amendment_title_result.single()
        
        return jsonify({
            'base_gazette': {
                'id': decoded_base_id,
                'structure': base_structure,
                'president': base_title['president'] if base_title else 'Unknown',
                'published_date': base_title['published_date'] if base_title else 'Unknown'
            },
            'amendment_gazette': {
                'id': decoded_amendment_id,
                'structure': amendment_structure,
                'president': amendment_title['president'] if amendment_title else 'Unknown',
                'published_date': amendment_title['published_date'] if amendment_title else 'Unknown'
            },
            'changes': {
                'added_ministers': added_ministers,
                'removed_ministers': removed_ministers,
                'modified_ministers': modified_ministers,
                'added_departments': list(set(amendment_structure['departments']) - set(base_structure['departments'])),
                'removed_departments': list(set(base_structure['departments']) - set(amendment_structure['departments'])),
                'added_laws': list(set(amendment_structure['laws']) - set(base_structure['laws'])),
                'removed_laws': list(set(base_structure['laws']) - set(amendment_structure['laws']))
            }
        })


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


@app.route("/debug/gazettes/<path:gazette_id>/entities", methods=["GET"])
def debug_gazette_entities(gazette_id):
    """Debug endpoint to see all entities connected to a specific gazette"""
    decoded_gazette_id = unquote(gazette_id)
    logger.debug(f"Debug: Getting entities for gazette {decoded_gazette_id}")
    
    with driver.session() as session:
        # Get all nodes connected to this gazette
        result = session.run("""
            MATCH (g:Gazette {gazette_id: $gazette_id})
            OPTIONAL MATCH (g)-[r]-(entity)
            RETURN g, r, entity, labels(entity) as entity_labels
        """, gazette_id=decoded_gazette_id)
        
        entities = []
        for record in result:
            entity_data = {
                'gazette': dict(record['g']) if record['g'] else None,
                'relationship': {
                    'type': record['r'].type if record['r'] else None,
                    'properties': dict(record['r']) if record['r'] else None
                } if record['r'] else None,
                'entity': {
                    'labels': record['entity_labels'],
                    'properties': dict(record['entity']) if record['entity'] else None
                } if record['entity'] else None
            }
            entities.append(entity_data)
        
        return jsonify({
            'gazette_id': decoded_gazette_id,
            'entities': entities,
            'count': len(entities)
        })


@app.route("/debug/database-structure", methods=["GET"])
def debug_database_structure():
    """Debug endpoint to understand the database structure"""
    logger.debug("Debug: Getting database structure")
    
    with driver.session() as session:
        # Get all node types and their counts
        node_types_result = session.run("""
            MATCH (n)
            RETURN labels(n) as labels, count(n) as count
            ORDER BY count DESC
        """)
        
        node_types = []
        for record in node_types_result:
            node_types.append({
                'labels': record['labels'],
                'count': record['count']
            })
        
        # Get all relationship types and their counts
        rel_types_result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(r) as count
            ORDER BY count DESC
        """)
        
        rel_types = []
        for record in rel_types_result:
            rel_types.append({
                'type': record['rel_type'],
                'count': record['count']
            })
        
        # Get sample gazette with all its relationships
        sample_gazette_result = session.run("""
            MATCH (g:Gazette)
            OPTIONAL MATCH (g)-[r]-(entity)
            RETURN g, r, entity, labels(entity) as entity_labels
            LIMIT 20
        """)
        
        sample_relationships = []
        for record in sample_gazette_result:
            sample_relationships.append({
                'gazette': dict(record['g']) if record['g'] else None,
                'relationship': {
                    'type': record['r'].type if record['r'] else None,
                    'properties': dict(record['r']) if record['r'] else None
                } if record['r'] else None,
                'entity': {
                    'labels': record['entity_labels'],
                    'properties': dict(record['entity']) if record['entity'] else None
                } if record['entity'] else None
            })
        
        return jsonify({
            'node_types': node_types,
            'relationship_types': rel_types,
            'sample_relationships': sample_relationships
        })

if __name__ == "__main__":
    logger.info("Starting Flask app on port 5001")  # Log when the app starts
    app.run(port=5001, debug=True)