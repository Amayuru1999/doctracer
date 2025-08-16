# Graph Comparison System for Doctracer

This system creates **separate labeled nodes** in a single Neo4j database to visualize changes between base gazette data and amendments, making it easy to see what has changed.

## 🏷️ Label Structure

### **Base Labels (Original Data)**
- `BaseGazette`: Original gazette information
- `BaseMinister`: Original ministers
- `BaseDepartment`: Original departments
- `BaseLaw`: Original laws
- `BaseFunction`: Original functions

### **Amendment Labels (Modified Data)**
- `AmendmentGazette`: Modified gazette information
- `AmendmentMinister`: Modified ministers
- `AmendmentDepartment`: Modified departments
- `AmendmentLaw`: Modified laws
- `AmendmentFunction`: Modified functions

### **Common Labels**
- All nodes also have their base type (e.g., `Minister`, `Department`)
- `source` property: `'base'` or `'amendment'`
- `amendment_date` for tracking when changes occurred

## 🚀 How to Use

### **Step 1: Load Base Data**
```bash
# Load base gazette data (clears existing base data)
python tests/table_to_neo4j.py --clear --input output/base/ranil/2289-43_E.json
```

### **Step 2: Apply Amendments**
```bash
# Copy base data to amendment labels and apply changes
python tests/amendment_to_neo4j.py --copy-base --input output/amendment/ranil/2297-78_E.json
```

### **Step 3: Compare Graphs**
```bash
# View comparison
python tests/compare_graphs.py

# Export comparison data
python tests/compare_graphs.py --export
```

## 🌐 Web Visualization

### **Interactive Tree UI**
For a beautiful, interactive tree visualization of the changes:

```bash
# Make the script executable
chmod +x tests/run_web_visualizer.sh

# Run the web visualizer
./tests/run_web_visualizer.sh
```

Or manually:
```bash
cd tests
pip install -r requirements_web.txt
python web_visualizer.py
```

Then open `http://localhost:5000` in your browser.

### **Features of the Web UI**
- **Interactive Tree**: Click to expand/collapse nodes
- **Color Coding**: 
  - 🟢 Green: Added items
  - 🔴 Red: Removed items
  - 🟡 Yellow: Modified items
  - ⚫ Gray: Unchanged items
- **Filtering**: Filter by data source and change status
- **Statistics Dashboard**: Real-time counts and summaries
- **Responsive Design**: Works on desktop and mobile
- **Tooltips**: Hover for detailed information

### **Web UI Screenshots**
The web interface provides:
- **Left Sidebar**: Filters, statistics, and legend
- **Main Area**: Interactive tree visualization
- **Real-time Updates**: Refresh button to get latest data
- **Mobile Friendly**: Responsive design for all devices

## 🌐 Visualizing in Neo4j Browser

1. Open `http://localhost:7474`
2. Use label filters to explore different data sets
3. Use these queries to explore:

### **Base Data Queries**
```cypher
// View all base nodes
MATCH (n:BaseGazette:BaseMinister:BaseDepartment:BaseLaw:BaseFunction) RETURN n LIMIT 100

// View base government structure
MATCH (m:BaseMinister)-[r]->(n) RETURN m, r, n

// Count base nodes by type
MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction 
RETURN labels(n)[0] as NodeType, count(n) as Count
```

### **Amendment Data Queries**
```cypher
// View all amendment nodes
MATCH (n:AmendmentGazette:AmendmentMinister:AmendmentDepartment:AmendmentLaw:AmendmentFunction) RETURN n LIMIT 100

// View all changes
MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IS NOT NULL RETURN a, r, b

// View added vs deleted relationships
MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IN ['ADDED', 'DELETED'] RETURN a, r, b

// Timeline of changes
MATCH (n) WHERE n.amendment_date IS NOT NULL RETURN n ORDER BY n.amendment_date
```

### **Comparison Queries**
```cypher
// Compare base vs amendment
MATCH (n) WHERE n:BaseGazette OR n:BaseMinister OR n:BaseDepartment OR n:BaseLaw OR n:BaseFunction 
   OR n:AmendmentGazette OR n:AmendmentMinister OR n:AmendmentDepartment OR n:AmendmentLaw OR n:AmendmentFunction 
RETURN labels(n)[0] as Type, n.source as Source, count(n) as Count

// View changes by status
MATCH (a:AmendmentMinister)-[r]->(b) WHERE r.status IS NOT NULL RETURN a, r, b
```

## 🔍 Understanding the Changes

### **Node Properties**
- `source`: Shows if node is from base or amendment
- `amendment_date`: When the change was made

### **Relationship Properties**
- `status`: 'ADDED' for new relationships, 'DELETED' for removed ones
- `amendment_date`: When the relationship changed

### **Visual Indicators**
- **Base* labels**: Original data (unchanged)
- **Amendment* labels**: Modified data (with changes)
- **Red relationships**: Deleted connections
- **Green relationships**: Added connections

## 📊 Comparison Output

The comparison script shows:
- Node count differences between base and amendment
- Relationship count differences
- Summary of changes (ADDED/DELETED)
- Useful Cypher queries for exploration

## 🎯 Use Cases

1. **Government Structure Analysis**: See how ministries change over time
2. **Impact Assessment**: Understand what amendments affect
3. **Audit Trail**: Track all changes with timestamps
4. **Visual Comparison**: Side-by-side view of before/after
5. **Interactive Exploration**: Web UI for stakeholders and presentations

## 🛠️ Troubleshooting

### **Database Connection Issues**
- Ensure Neo4j is running: `docker ps | grep neo4j`
- Check `.env` file has correct credentials
- Verify ports 7474 and 7687 are accessible

### **Data Loading Issues**
- Verify JSON files exist and are valid
- Check file paths are correct
- Use `--clear` flag to reset data if needed

### **Label Filtering Issues**
- Use exact label names (case-sensitive)
- Combine labels with `:` for multiple labels
- Use `WHERE` clauses for complex filtering

### **Web UI Issues**
- Ensure Flask dependencies are installed
- Check if port 5000 is available
- Verify Neo4j connection before starting web server

## 🔄 Workflow

1. **Load Base**: `table_to_neo4j.py --clear --input <file>`
2. **Apply Amendments**: `amendment_to_neo4j.py --copy-base --input <file>`
3. **Compare**: `compare_graphs.py`
4. **Visualize**: Use Neo4j Browser with label filters
5. **Web UI**: `run_web_visualizer.sh` for interactive tree view
6. **Export**: `compare_graphs.py --export` for external analysis
