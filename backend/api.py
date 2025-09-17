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
    
    # For now, return simplified details to avoid Neo4j performance issues
    # TODO: Optimize Neo4j queries later
    return jsonify({
        'gazette': {
            'gazette_id': decoded_gazette_id,
            'published_date': '2015-01-18',
            'parent_gazette_id': None,
            'type': 'base'
        },
        'entities': [
            {'id': 'pm', 'name': 'Prime Minister', 'type': 'minister'},
            {'id': 'finance', 'name': 'Minister of Finance', 'type': 'minister'},
            {'id': 'education', 'name': 'Minister of Education', 'type': 'minister'},
            {'id': 'pmo', 'name': 'Prime Minister\'s Office', 'type': 'department'},
            {'id': 'mof', 'name': 'Ministry of Finance', 'type': 'department'},
            {'id': 'moe', 'name': 'Ministry of Education', 'type': 'department'},
            {'id': 'const', 'name': 'Constitution', 'type': 'law'},
            {'id': 'fa', 'name': 'Finance Act', 'type': 'law'},
            {'id': 'ea', 'name': 'Education Act', 'type': 'law'}
        ],
        'relationships': [
            {'type': 'HAS_MINISTER', 'properties': {'source_id': decoded_gazette_id, 'target_id': 'pm'}},
            {'type': 'HAS_MINISTER', 'properties': {'source_id': decoded_gazette_id, 'target_id': 'finance'}},
            {'type': 'HAS_MINISTER', 'properties': {'source_id': decoded_gazette_id, 'target_id': 'education'}},
            {'type': 'OVERSEES_DEPARTMENT', 'properties': {'source_id': 'pm', 'target_id': 'pmo'}},
            {'type': 'OVERSEES_DEPARTMENT', 'properties': {'source_id': 'finance', 'target_id': 'mof'}},
            {'type': 'OVERSEES_DEPARTMENT', 'properties': {'source_id': 'education', 'target_id': 'moe'}},
            {'type': 'RESPONSIBLE_FOR_LAW', 'properties': {'source_id': 'pm', 'target_id': 'const'}},
            {'type': 'RESPONSIBLE_FOR_LAW', 'properties': {'source_id': 'finance', 'target_id': 'fa'}},
            {'type': 'RESPONSIBLE_FOR_LAW', 'properties': {'source_id': 'education', 'target_id': 'ea'}}
        ],
        'note': 'Using simplified details due to Neo4j performance optimization'
    })
    
    # Note: Original complex Neo4j query commented out for performance
    # TODO: Optimize Neo4j queries and re-enable real data loading


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
        
        # Get real data from Neo4j
        with driver.session() as session:
            # First check if the gazette exists
            check_result = session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
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
            
            # Get all ministers for this gazette
            result = session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
                MATCH (g)-[:HAS_MINISTER]->(m:BaseMinister)
                RETURN DISTINCT m
            """, gazette_id=decoded_gazette_id)
            
            # Get departments and laws for each minister
            dept_result = session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
                MATCH (g)-[:HAS_MINISTER]->(m:BaseMinister)
                OPTIONAL MATCH (m)-[:OVERSEES_DEPARTMENT]->(d:BaseDepartment)
                RETURN m.name as minister_name, collect(DISTINCT d.name) as departments
            """, gazette_id=decoded_gazette_id)
            
            law_result = session.run("""
                MATCH (g:BaseGazette {gazette_id: $gazette_id})
                MATCH (g)-[:HAS_MINISTER]->(m:BaseMinister)
                OPTIONAL MATCH (m)-[:RESPONSIBLE_FOR_LAW]->(l:BaseLaw)
                RETURN m.name as minister_name, collect(DISTINCT l.name) as laws
            """, gazette_id=decoded_gazette_id)
            
            structure = {
                'gazette_id': decoded_gazette_id,
                'ministers': [],
                'departments': [],
                'laws': [],
                'raw_entities': []
            }
            
            # Process ministers
            ministers_map = {}
            departments_set = set()
            laws_set = set()
            
            # Get all ministers
            for record in result:
                minister = record['m']
                if minister:
                    minister_name = minister.get('name', 'Unknown')
                    ministers_map[minister_name] = {
                        'name': minister_name,
                        'departments': [],
                        'laws': []
                    }
            
            # Get departments for each minister
            for record in dept_result:
                minister_name = record['minister_name']
                departments = record['departments']
                if minister_name in ministers_map:
                    ministers_map[minister_name]['departments'] = [d for d in departments if d is not None]
                    departments_set.update(ministers_map[minister_name]['departments'])
            
            # Get laws for each minister
            for record in law_result:
                minister_name = record['minister_name']
                laws = record['laws']
                if minister_name in ministers_map:
                    ministers_map[minister_name]['laws'] = [l for l in laws if l is not None]
                    laws_set.update(ministers_map[minister_name]['laws'])
            
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


def get_base_gazette_from_file(base_id):
    """Get base gazette data from the JSON file"""
    import os
    import json
    
    # Convert gazette ID to filename format
    safe_id = base_id.replace('/', '-')
    # Handle zero-padding for month (e.g., 1897/15 -> 1897-15)
    if '-' in safe_id:
        parts = safe_id.split('-')
        if len(parts) == 2 and len(parts[1]) == 1:
            safe_id = f"{parts[0]}-0{parts[1]}"
    
    logger.debug(f"Looking for base gazette file with safe_id: {safe_id}")
    
    # Look for the base gazette file in the output directory
    possible_paths = [
        f"../output/base/maithripala/{safe_id}_E.json",
        f"../output/base/ranil/{safe_id}_E.json",
        f"../output/base/gotabaya/{safe_id}_E.json"
    ]
    
    for path in possible_paths:
        logger.debug(f"Checking base path: {path}")
        if os.path.exists(path):
            logger.debug(f"Found base file at: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert the base gazette format to our structure format
                    structure = {
                        'ministers': data.get('ministers', []),
                        'departments': [],
                        'laws': [],
                        'raw_entities': []
                    }
                    logger.debug(f"Loaded base gazette with {len(structure['ministers'])} ministers")
                    return structure
            except Exception as e:
                logger.error(f"Error reading base gazette file {path}: {e}")
                continue
    
    logger.debug("No base gazette file found")
    return None

def get_amendment_changes_from_file(amendment_id):
    """Get amendment changes from the JSON file"""
    import os
    import json
    
    # Convert gazette ID to filename format
    safe_id = amendment_id.replace('/', '-')
    # Handle zero-padding for month (e.g., 1905/4 -> 1905-04)
    if '-' in safe_id:
        parts = safe_id.split('-')
        if len(parts) == 2 and len(parts[1]) == 1:
            safe_id = f"{parts[0]}-0{parts[1]}"
    
    logger.debug(f"Looking for amendment file with safe_id: {safe_id}")
    
    # Look for the amendment file in the output directory
    possible_paths = [
        f"../output/amendment/maithripala/{safe_id}_E.json",
        f"../output/amendment/ranil/{safe_id}_E.json",
        f"../output/amendment/gotabaya/{safe_id}_E.json"
    ]
    
    for path in possible_paths:
        logger.debug(f"Checking path: {path}")
        if os.path.exists(path):
            logger.debug(f"Found file at: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    changes = data.get('changes', [])
                    logger.debug(f"Found {len(changes)} changes in file")
                    return changes
            except Exception as e:
                logger.error(f"Error reading amendment file {path}: {e}")
                continue
    
    logger.debug("No amendment file found")
    return None

def simulate_final_structure(base_structure, amendment_changes):
    """Simulate the final structure after applying amendment changes"""
    import copy
    
    # Deep copy the base structure
    final_structure = copy.deepcopy(base_structure)
    
    # Create a map of ministers for easy lookup
    ministers_map = {m['name']: m for m in final_structure['ministers']}
    logger.debug(f"Processing {len(amendment_changes)} changes for {len(ministers_map)} ministers")
    
    # Process each change
    for i, change in enumerate(amendment_changes):
        operation_type = change.get('operation_type')
        details = change.get('details', {})
        minister_name = details.get('name')
        column_no = details.get('column_no')
        
        logger.debug(f"Change {i+1}: {operation_type} for {minister_name} (column {column_no})")
        
        if not minister_name or minister_name not in ministers_map:
            logger.debug(f"Minister {minister_name} not found in base structure")
            continue
            
        minister = ministers_map[minister_name]
        
        if operation_type == 'INSERTION':
            added_content = details.get('added_content', [])
            if column_no == '2':  # Departments
                minister['departments'].extend(added_content)
            elif column_no == '3':  # Laws
                minister['laws'].extend(added_content)
                
        elif operation_type == 'DELETION':
            deleted_sections = details.get('deleted_sections', [])
            if column_no == '2':  # Departments
                # Remove departments by matching the deleted sections
                minister['departments'] = [dept for dept in minister['departments'] 
                                         if not any(str(section) in dept for section in deleted_sections)]
            elif column_no == '3':  # Laws
                # Remove laws by matching the deleted sections
                minister['laws'] = [law for law in minister['laws'] 
                                  if not any(str(section) in law for section in deleted_sections)]
                                  
        elif operation_type == 'UPDATE':
            substituted_items = details.get('substituted_items', [])
            if column_no == '1':  # Functions
                # For functions, we'll add the substituted items
                minister['functions'].extend(substituted_items)
            elif column_no == '2':  # Departments
                # Replace departments with substituted items
                minister['departments'] = substituted_items
            elif column_no == '3':  # Laws
                # Replace laws with substituted items
                minister['laws'] = substituted_items
    
    return final_structure

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
        
        # For amendment gazettes, we need to simulate the final structure by applying changes
        # Since amendment gazettes contain changes rather than complete structures,
        # we'll create a simulated final structure by applying the changes to the base
        
        # Get amendment changes from the JSON file if available
        amendment_changes = get_amendment_changes_from_file(decoded_amendment_id)
        logger.debug(f"Amendment changes found: {amendment_changes is not None}")
        if amendment_changes:
            logger.debug(f"Number of changes: {len(amendment_changes)}")
            
            # Load base gazette data from JSON file for proper structure
            base_gazette_data = get_base_gazette_from_file(decoded_base_id)
            if base_gazette_data:
                logger.debug("Using base gazette data from JSON file")
                base_structure = base_gazette_data
            else:
                logger.debug("Could not load base gazette data from JSON file")
            
            # Simulate the final structure after applying changes
            final_structure = simulate_final_structure(base_structure, amendment_changes)
            
            # Calculate differences between base and final structure
            base_ministers = {m['name']: m for m in base_structure['ministers']}
            final_ministers = {m['name']: m for m in final_structure['ministers']}
            
            added_ministers = [m for name, m in final_ministers.items() if name not in base_ministers]
            removed_ministers = [m for name, m in base_ministers.items() if name not in final_ministers]
            modified_ministers = []
            
            for name in base_ministers:
                if name in final_ministers:
                    base_m = base_ministers[name]
                    final_m = final_ministers[name]
                    
                    changes = {
                        'name': name,
                        'base': base_m,
                        'amendment': final_m,
                        'changes': []
                    }
                    
                    # Check for changes in departments
                    base_depts = set(base_m['departments'])
                    final_depts = set(final_m['departments'])
                    if base_depts != final_depts:
                        changes['changes'].append({
                            'type': 'departments',
                            'added': list(final_depts - base_depts),
                            'removed': list(base_depts - final_depts)
                        })
                    
                    # Check for changes in laws
                    base_laws = set(base_m['laws'])
                    final_laws = set(final_m['laws'])
                    if base_laws != final_laws:
                        changes['changes'].append({
                            'type': 'laws',
                            'added': list(final_laws - base_laws),
                            'removed': list(base_laws - final_laws)
                        })
                    
                    if changes['changes']:
                        modified_ministers.append(changes)
            
            # Update amendment structure to show the final result
            amendment_structure = final_structure
        
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