from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Neo4j connection
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def convert_neo4j_types(obj):
    """Convert Neo4j types to JSON-serializable types"""
    if hasattr(obj, '__dict__'):
        # Handle Neo4j objects
        if hasattr(obj, 'iso_format'):
            # Neo4j DateTime object
            return obj.iso_format()
        elif hasattr(obj, 'to_native'):
            # Neo4j Date object
            return obj.to_native().isoformat()
        elif hasattr(obj, 'to_native'):
            # Neo4j Time object
            return obj.to_native().isoformat()
        else:
            # Regular object, convert to dict
            return {k: convert_neo4j_types(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: convert_neo4j_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_neo4j_types(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def get_government_tree():
    """Get government structure as a tree for visualization - ministries with departments"""
    
    try:
        with driver.session() as session:
            # Get base structure with departments
            base_data = session.run("""
                MATCH (g:BaseGazette)-[:HAS_MINISTER]->(m:BaseMinister)
                OPTIONAL MATCH (m)-[:OVERSEES_DEPARTMENT]->(d:BaseDepartment)
                RETURN g, m, collect(d) as departments
                ORDER BY m.name
            """).data()
            
            # Get amendment structure with departments
            amendment_data = session.run("""
                MATCH (g:AmendmentGazette)-[:HAS_MINISTER]->(m:AmendmentMinister)
                OPTIONAL MATCH (m)-[:OVERSEES_DEPARTMENT]->(d:AmendmentDepartment)
                RETURN g, m, collect(d) as departments
                ORDER BY m.name
            """).data()
        
        # Build tree structure
        tree = {
            "name": "Government Structure",
            "type": "root",
            "children": []
        }
        
        # Process base data
        ministers_base = {}
        for record in base_data:
            minister_name = record['m']['name']
            if minister_name not in ministers_base:
                ministers_base[minister_name] = {
                    "name": minister_name,
                    "type": "minister",
                    "source": "base",
                    "departments": []
                }
            
            # Add departments
            for dept in record['departments']:
                if dept and dept['name']:
                    ministers_base[minister_name]["departments"].append({
                        "name": dept['name'],
                        "type": "department",
                        "source": "base"
                    })
        
        # Process amendment data
        ministers_amendment = {}
        for record in amendment_data:
            minister_name = record['m']['name']
            if minister_name not in ministers_amendment:
                ministers_amendment[minister_name] = {
                    "name": minister_name,
                    "type": "minister",
                    "source": "amendment",
                    "departments": []
                }
            
            # Add departments
            for dept in record['departments']:
                if dept and dept['name']:
                    ministers_amendment[minister_name]["departments"].append({
                        "name": dept['name'],
                        "type": "department",
                        "source": "amendment"
                    })
        
        # Merge and mark changes
        all_ministers = set(ministers_base.keys()) | set(ministers_amendment.keys())
        
        for minister_name in sorted(all_ministers):
            minister_node = {
                "name": minister_name,
                "type": "minister",
                "children": []
            }
            
            # Check if minister exists in both
            if minister_name in ministers_base and minister_name in ministers_amendment:
                minister_node["source"] = "both"
                minister_node["status"] = "unchanged"
                
                # Merge departments
                base_depts = {d['name']: d for d in ministers_base[minister_name]["departments"]}
                amendment_depts = {d['name']: d for d in ministers_amendment[minister_name]["departments"]}
                
                all_dept_names = set(base_depts.keys()) | set(amendment_depts.keys())
                
                for dept_name in sorted(all_dept_names):
                    dept_node = {"name": dept_name, "type": "department"}
                    
                    if dept_name in base_depts and dept_name in amendment_depts:
                        dept_node["source"] = "both"
                        dept_node["status"] = "unchanged"
                    elif dept_name in base_depts:
                        dept_node["source"] = "base"
                        dept_node["status"] = "removed"
                    else:
                        dept_node["source"] = "amendment"
                        dept_node["status"] = "added"
                    
                    minister_node["children"].append(dept_node)
                    
            elif minister_name in ministers_base:
                minister_node["source"] = "base"
                minister_node["status"] = "removed"
                # Add base departments as removed
                for dept in ministers_base[minister_name]["departments"]:
                    dept_node = {
                        "name": dept['name'],
                        "type": "department",
                        "source": "base",
                        "status": "removed"
                    }
                    minister_node["children"].append(dept_node)
            else:
                minister_node["source"] = "amendment"
                minister_node["status"] = "added"
                # Add amendment departments as added
                for dept in ministers_amendment[minister_name]["departments"]:
                    dept_node = {
                        "name": dept['name'],
                        "type": "department",
                        "source": "amendment",
                        "status": "added"
                    }
                    minister_node["children"].append(dept_node)
            
            tree["children"].append(minister_node)
        
        return tree
        
    except Exception as e:
        print(f"Error in get_government_tree: {e}")
        # Return minimal tree on error
        return {
            "name": "Government Structure",
            "children": []
        }

def get_changes_summary():
    """Get summary of changes for the dashboard - showing actual changes"""
    
    try:
        with driver.session() as session:
            # Count nodes by type and source
            node_counts = session.run("""
                MATCH (n) 
                WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction
                   OR n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction
                WITH labels(n) as labels
                UNWIND labels as label
                WITH label
                WHERE label IN ['BaseGazette', 'AmendmentGazette', 'BaseMinister', 'AmendmentMinister', 
                               'BaseDepartment', 'AmendmentDepartment', 'BaseLaw', 'AmendmentLaw',
                               'BaseFunction', 'AmendmentFunction']
                WITH 
                    CASE 
                        WHEN label CONTAINS 'Base' THEN 'base'
                        WHEN label CONTAINS 'Amendment' THEN 'amendment'
                    END as source,
                    CASE
                        WHEN label CONTAINS 'Minister' THEN 'Minister'
                        WHEN label CONTAINS 'Department' THEN 'Department'
                        WHEN label CONTAINS 'Law' THEN 'Law'
                        WHEN label CONTAINS 'Function' THEN 'Function'
                        WHEN label CONTAINS 'Gazette' THEN 'Gazette'
                    END as nodeType
                RETURN nodeType as NodeType, source as Source, count(*) as Count
                ORDER BY NodeType, Source
            """).data()
            
            # Count actual changes at different levels
            changes = []
            
            # Department changes
            dept_changes = session.run("""
                // Added departments
                MATCH (ad:AmendmentDepartment)
                WHERE NOT EXISTS {
                    MATCH (bd:BaseDepartment {name: ad.name})
                }
                RETURN 'ADDED_DEPARTMENTS' as Status, count(ad) as Count
                UNION ALL
                // Removed departments
                MATCH (bd:BaseDepartment)
                WHERE NOT EXISTS {
                    MATCH (ad:AmendmentDepartment {name: bd.name})
                }
                RETURN 'REMOVED_DEPARTMENTS' as Status, count(bd) as Count
                UNION ALL
                // Added laws
                MATCH (al:AmendmentLaw)
                WHERE NOT EXISTS {
                    MATCH (bl:BaseLaw {name: al.name})
                }
                RETURN 'ADDED_LAWS' as Status, count(al) as Count
                UNION ALL
                // Removed laws
                MATCH (bl:BaseLaw)
                WHERE NOT EXISTS {
                    MATCH (al:AmendmentLaw {name: bl.name})
                }
                RETURN 'REMOVED_LAWS' as Status, count(bl) as Count
                UNION ALL
                // Added functions
                MATCH (af:AmendmentFunction)
                WHERE NOT EXISTS {
                    MATCH (bf:BaseFunction {description: af.description})
                }
                RETURN 'ADDED_FUNCTIONS' as Status, count(af) as Count
                UNION ALL
                // Removed functions
                MATCH (bf:BaseFunction)
                WHERE NOT EXISTS {
                    MATCH (af:AmendmentFunction {description: bf.description})
                }
                RETURN 'REMOVED_FUNCTIONS' as Status, count(bf) as Count
            """).data()
            
            changes.extend(dept_changes)
            
            # Get recent amendments with actual changes
            recent = session.run("""
                MATCH (n) 
                WHERE n.amendment_date IS NOT NULL
                AND (n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction)
                AND NOT EXISTS {
                    MATCH (base)
                    WHERE (base:BaseDepartment AND base.name = n.name)
                       OR (base:BaseLaw AND base.name = n.name)
                       OR (base:BaseFunction AND base.description = n.description)
                }
                RETURN n.name as Name, n.amendment_date as Date, 
                       CASE 
                           WHEN n:AmendmentDepartment THEN 'Department'
                           WHEN n:AmendmentLaw THEN 'Law'
                           WHEN n:AmendmentFunction THEN 'Function'
                       END as Type
                ORDER BY n.amendment_date DESC
                LIMIT 10
            """).data()
        
        return {
            "node_counts": node_counts,
            "changes": changes,
            "recent": recent
        }
    except Exception as e:
        print(f"Error in get_changes_summary: {e}")
        # Return empty data on error
        return {
            "node_counts": [],
            "changes": [],
            "recent": []
        }

def get_department_changes():
    """Get detailed department changes for card display"""
    
    try:
        with driver.session() as session:
            # Get base departments
            base_departments = session.run("""
                MATCH (m:BaseMinister)-[:OVERSEES_DEPARTMENT]->(d:BaseDepartment)
                RETURN m.name as minister, d.name as department, 'base' as source
                ORDER BY m.name, d.name
            """).data()
            
            # Get amendment departments
            amendment_departments = session.run("""
                MATCH (m:AmendmentMinister)-[:OVERSEES_DEPARTMENT]->(d:AmendmentDepartment)
                RETURN m.name as minister, d.name as department, 'amendment' as source
                ORDER BY m.name, d.name
            """).data()
            
            # Get changes with status
            changes = session.run("""
                MATCH (m:AmendmentMinister)-[r:OVERSEES_DEPARTMENT]->(d:AmendmentDepartment)
                WHERE r.status IS NOT NULL
                RETURN m.name as minister, d.name as department, r.status as status, r.amendment_date as date
                ORDER BY m.name, d.name
            """).data()
        
        # Process changes
        changes_data = []
        
        # Process base departments
        base_dict = {}
        for record in base_departments:
            minister = record['minister']
            dept = record['department']
            if minister not in base_dict:
                base_dict[minister] = set()
            base_dict[minister].add(dept)
        
        # Process amendment departments
        amendment_dict = {}
        for record in amendment_departments:
            minister = record['minister']
            dept = record['department']
            if minister not in amendment_dict:
                amendment_dict[minister] = set()
            amendment_dict[minister].add(dept)
        
        # Find all ministers
        all_ministers = set(base_dict.keys()) | set(amendment_dict.keys())
        
        for minister in sorted(all_ministers):
            base_depts = base_dict.get(minister, set())
            amendment_depts = amendment_dict.get(minister, set())
            
            # Added departments
            for dept in amendment_depts - base_depts:
                changes_data.append({
                    "minister": minister,
                    "department": dept,
                    "status": "added",
                    "type": "department"
                })
            
            # Removed departments
            for dept in base_depts - amendment_depts:
                changes_data.append({
                    "minister": minister,
                    "department": dept,
                    "status": "removed",
                    "type": "department"
                })
            
            # Unchanged departments
            for dept in base_depts & amendment_depts:
                changes_data.append({
                    "minister": minister,
                    "department": dept,
                    "status": "unchanged",
                    "type": "department"
                })
        
        return changes_data
        
    except Exception as e:
        print(f"Error in get_department_changes: {e}")
        return []

def get_law_changes():
    """Get detailed law changes for card display"""
    
    try:
        with driver.session() as session:
            # Get base laws
            base_laws = session.run("""
                MATCH (m:BaseMinister)-[:RESPONSIBLE_FOR_LAW]->(l:BaseLaw)
                RETURN m.name as minister, l.name as law, 'base' as source
                ORDER BY m.name, l.name
            """).data()
            
            # Get amendment laws
            amendment_laws = session.run("""
                MATCH (m:AmendmentMinister)-[:RESPONSIBLE_FOR_LAW]->(l:AmendmentLaw)
                RETURN m.name as minister, l.name as law, 'amendment' as source
                ORDER BY m.name, l.name
            """).data()
        
        # Process changes
        changes_data = []
        
        # Process base laws
        base_dict = {}
        for record in base_laws:
            minister = record['minister']
            law = record['law']
            if minister not in base_dict:
                base_dict[minister] = set()
            base_dict[minister].add(law)
        
        # Process amendment laws
        amendment_dict = {}
        for record in amendment_laws:
            minister = record['minister']
            law = record['law']
            if minister not in amendment_dict:
                amendment_dict[minister] = set()
            amendment_dict[minister].add(law)
        
        # Find all ministers
        all_ministers = set(base_dict.keys()) | set(amendment_dict.keys())
        
        for minister in sorted(all_ministers):
            base_laws_set = base_dict.get(minister, set())
            amendment_laws_set = amendment_dict.get(minister, set())
            
            # Added laws
            for law in amendment_laws_set - base_laws_set:
                changes_data.append({
                    "minister": minister,
                    "department": law,
                    "status": "added",
                    "type": "law"
                })
            
            # Removed laws
            for law in base_laws_set - amendment_laws_set:
                changes_data.append({
                    "minister": minister,
                    "department": law,
                    "status": "removed",
                    "type": "law"
                })
            
            # Unchanged laws
            for law in base_laws_set & amendment_laws_set:
                changes_data.append({
                    "minister": minister,
                    "department": law,
                    "status": "unchanged",
                    "type": "law"
                })
        
        return changes_data
        
    except Exception as e:
        print(f"Error in get_law_changes: {e}")
        return []

def get_function_changes():
    """Get detailed function changes for card display"""
    
    try:
        with driver.session() as session:
            # Get base functions
            base_functions = session.run("""
                MATCH (m:BaseMinister)-[:PERFORMS_FUNCTION]->(f:BaseFunction)
                RETURN m.name as minister, f.description as function, 'base' as source
                ORDER BY m.name, f.description
            """).data()
            
            # Get amendment functions
            amendment_functions = session.run("""
                MATCH (m:AmendmentMinister)-[:PERFORMS_FUNCTION]->(f:AmendmentFunction)
                RETURN m.name as minister, f.description as function, 'amendment' as source
                ORDER BY m.name, f.description
            """).data()
        
        # Process changes
        changes_data = []
        
        # Process base functions
        base_dict = {}
        for record in base_functions:
            minister = record['minister']
            func = record['function']
            if minister not in base_dict:
                base_dict[minister] = set()
            base_dict[minister].add(func)
        
        # Process amendment functions
        amendment_dict = {}
        for record in amendment_functions:
            minister = record['minister']
            func = record['function']
            if minister not in amendment_dict:
                amendment_dict[minister] = set()
            amendment_dict[minister].add(func)
        
        # Find all ministers
        all_ministers = set(base_dict.keys()) | set(amendment_dict.keys())
        
        for minister in sorted(all_ministers):
            base_funcs = base_dict.get(minister, set())
            amendment_funcs = amendment_dict.get(minister, set())
            
            # Added functions
            for func in amendment_funcs - base_funcs:
                changes_data.append({
                    "minister": minister,
                    "department": func,
                    "status": "added",
                    "type": "function"
                })
            
            # Removed functions
            for func in base_funcs - amendment_funcs:
                changes_data.append({
                    "minister": minister,
                    "department": func,
                    "status": "removed",
                    "type": "function"
                })
            
            # Unchanged functions
            for func in base_funcs & amendment_funcs:
                changes_data.append({
                    "minister": minister,
                    "department": func,
                    "status": "unchanged",
                    "type": "function"
                })
        
        return changes_data
        
    except Exception as e:
        print(f"Error in get_function_changes: {e}")
        return []

@app.route('/')
def index():
    """Main page with tree visualization"""
    return render_template('index.html')

@app.route('/api/tree')
def api_tree():
    """API endpoint for tree data"""
    try:
        tree_data = get_government_tree()
        # Convert Neo4j types before JSON serialization
        tree_data = convert_neo4j_types(tree_data)
        return jsonify(tree_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary')
def api_summary():
    """API endpoint for changes summary"""
    try:
        summary_data = get_changes_summary()
        # Convert Neo4j types before JSON serialization
        summary_data = convert_neo4j_types(summary_data)
        return jsonify(summary_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/filter')
def api_filter():
    """API endpoint for filtered tree data"""
    try:
        source = request.args.get('source', 'all')
        status = request.args.get('status', 'all')
        
        tree_data = get_government_tree()
        
        # Apply filters
        if source != 'all' or status != 'all':
            tree_data = filter_tree(tree_data, source, status)
        
        # Convert Neo4j types before JSON serialization
        tree_data = convert_neo4j_types(tree_data)
        return jsonify(tree_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/departments')
def departments_view():
    """Department changes view with cards"""
    return render_template('departments.html')

@app.route('/api/departments')
def api_departments():
    """API endpoint for department changes"""
    try:
        dept_changes = get_department_changes()
        law_changes = get_law_changes()
        func_changes = get_function_changes()
        
        all_changes = dept_changes + law_changes + func_changes
        
        # Convert Neo4j types before JSON serialization
        all_changes = convert_neo4j_types(all_changes)
        
        return jsonify({
            "departments": dept_changes,
            "laws": law_changes,
            "functions": func_changes,
            "all_changes": all_changes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def filter_tree(tree, source, status):
    """Filter tree based on source and status"""
    if source == 'all' and status == 'all':
        return tree
    
    filtered_children = []
    for child in tree.get('children', []):
        if should_include_node(child, source, status):
            filtered_child = child.copy()
            filtered_child['children'] = [c for c in child.get('children', []) 
                                        if should_include_node(c, source, status)]
            if filtered_child['children'] or should_include_node(child, source, status):
                filtered_children.append(filtered_child)
    
    filtered_tree = tree.copy()
    filtered_tree['children'] = filtered_children
    return filtered_tree

def should_include_node(node, source, status):
    """Check if node should be included based on filters"""
    if source != 'all' and node.get('source') != source:
        return False
    if status != 'all' and node.get('status') != status:
        return False
    return True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
