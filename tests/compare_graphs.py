import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def compare_graphs():
    """Compare base and amendment graphs to show changes"""
    
    print("🔍 Comparing Base* vs Amendment* labels...")
    print("=" * 60)
    
    # Get base graph statistics
    with driver.session() as session:
        base_stats = session.run("""
            MATCH (n) 
            WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction
            RETURN labels(n)[0] as NodeType, count(n) as Count
            ORDER BY NodeType
        """).data()
        
        base_rels = session.run("""
            MATCH (a)-[r]->(b) 
            WHERE a:BaseMinister OR a:BaseGazette
            RETURN type(r) as RelType, count(r) as Count
            ORDER BY RelType
        """).data()
    
    # Get amendment graph statistics
    with driver.session() as session:
        amend_stats = session.run("""
            MATCH (n) 
            WHERE n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction
            RETURN labels(n)[0] as NodeType, count(n) as Count
            ORDER BY NodeType
        """).data()
        
        amend_rels = session.run("""
            MATCH (a)-[r]->(b) 
            WHERE a:AmendmentMinister OR a:AmendmentGazette
            RETURN type(r) as RelType, count(r) as Count
            ORDER BY RelType
        """).data()
        
        # Get change summary
        changes = session.run("""
            MATCH (a:AmendmentMinister)-[r]->(b) 
            WHERE r.status IS NOT NULL
            RETURN r.status as Status, count(r) as Count
            ORDER BY Status
        """).data()
    
    print("📊 NODE COMPARISON:")
    print(f"{'Node Type':<15} {'Base':<8} {'Amendment':<10} {'Difference':<12}")
    print("-" * 50)
    
    base_dict = {stat['NodeType']: stat['Count'] for stat in base_stats}
    amend_dict = {stat['NodeType']: stat['Count'] for stat in amend_stats}
    
    all_types = set(base_dict.keys()) | set(amend_dict.keys())
    
    for node_type in sorted(all_types):
        base_count = base_dict.get(node_type, 0)
        amend_count = amend_dict.get(node_type, 0)
        diff = amend_count - base_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"{node_type:<15} {base_count:<8} {amend_count:<10} {diff_str:<12}")
    
    print("\n🔗 RELATIONSHIP COMPARISON:")
    print(f"{'Rel Type':<20} {'Base':<8} {'Amendment':<10} {'Difference':<12}")
    print("-" * 55)
    
    base_rel_dict = {rel['RelType']: rel['Count'] for rel in base_rels}
    amend_rel_dict = {rel['RelType']: rel['Count'] for rel in amend_rels}
    
    all_rel_types = set(base_rel_dict.keys()) | set(amend_rel_dict.keys())
    
    for rel_type in sorted(all_rel_types):
        base_count = base_rel_dict.get(rel_type, 0)
        amend_count = amend_rel_dict.get(rel_type, 0)
        diff = amend_count - base_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"{rel_type:<20} {base_count:<8} {amend_count:<10} {diff_str:<12}")
    
    print("\n📝 CHANGE SUMMARY:")
    for change in changes:
        print(f"  {change['Status']}: {change['Count']} relationships")
    
    print("\n🌐 VISUALIZATION QUERIES:")
    print("Use these labels to filter data in Neo4j Browser:")
    print("  - Base* labels: Original government structure")
    print("  - Amendment* labels: Structure with amendments applied")
    print("\nUseful comparison queries:")
    print("  // View all changes")
    print("  MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IS NOT NULL RETURN a, r, b")
    print("  // View added vs deleted")
    print("  MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IN ['ADDED', 'DELETED'] RETURN a, r, b")
    print("  // View timeline of changes")
    print("  MATCH (n) WHERE n.amendment_date IS NOT NULL RETURN n ORDER BY n.amendment_date")
    print("  // Compare base vs amendment")
    print("  MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction OR n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction RETURN labels(n)[0] as Type, n.source as Source, count(n) as Count")

def export_comparison():
    """Export comparison data to JSON for external analysis"""
    
    comparison_data = {
        "base_graph": {},
        "amendment_graph": {},
        "changes": {},
        "summary": {}
    }
    
    # Get base graph data
    with driver.session() as session:
        base_nodes = session.run("MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction RETURN n").data()
        base_rels = session.run("MATCH (a)-[r]->(b) WHERE a:BaseMinister OR a:BaseGazette RETURN a, r, b").data()
        
        comparison_data["base_graph"]["nodes"] = len(base_nodes)
        comparison_data["base_graph"]["relationships"] = len(base_rels)
    
    # Get amendment graph data
    with driver.session() as session:
        amend_nodes = session.run("MATCH (n) WHERE n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction RETURN n").data()
        amend_rels = session.run("MATCH (a)-[r]->(b) WHERE a:AmendmentMinister OR a:AmendmentGazette RETURN a, r, b").data()
        changes = session.run("MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IS NOT NULL RETURN a, r, b").data()
        
        comparison_data["amendment_graph"]["nodes"] = len(amend_nodes)
        comparison_data["amendment_graph"]["relationships"] = len(amend_rels)
        comparison_data["changes"] = len(changes)
    
    # Calculate summary
    comparison_data["summary"]["node_difference"] = comparison_data["amendment_graph"]["nodes"] - comparison_data["base_graph"]["nodes"]
    comparison_data["summary"]["relationship_difference"] = comparison_data["amendment_graph"]["relationships"] - comparison_data["base_graph"]["relationships"]
    
    # Export to file
    with open("graph_comparison.json", "w") as f:
        json.dump(comparison_data, f, indent=2, default=str)
    
    print("💾 Comparison data exported to graph_comparison.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare Base and Amendment Neo4j Graphs")
    parser.add_argument("--export", action="store_true", help="Export comparison data to JSON")
    args = parser.parse_args()
    
    compare_graphs()
    
    if args.export:
        export_comparison()
