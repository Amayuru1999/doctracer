# Interactive Frontend Setup for DocTracer

This guide explains how to set up and use the interactive frontend for visualizing your Neo4j graph data loaded from the DocTracer commands.

## Prerequisites

1. **Neo4j Database**: Ensure Neo4j is running and accessible
2. **Data Loaded**: Your gazette data should be loaded using the provided commands:
   ```bash
   # Base gazette
   doctracer extract --type extragazette_table --input data/testdata/base/maithripala/1897-15_E.pdf --output output/base/maithripala/1897-15_E.json
   
   # Amendment gazette
   doctracer extract --type extragazette_amendment --input data/testdata/amendment/maithripala/1905-04_E.pdf --output output/amendment/maithripala/1905-04_E.json
   
   # Load to Neo4j
   python doctracer/cli/table_to_neo4j.py --input output/base/maithripala/1897-15_E_sample.json --gazette_id 1897/15 --published_date 2015-01-18
   python doctracer/cli/amendment_to_neo4j.py --input output/amendment/maithripala/1905-04_E_1.json --base output/base/maithripala/1897-15_E_sample.json
   ```

## Setup Instructions

### 1. Start the Backend API

```bash
# Navigate to the project root
cd /Users/amayuruamarasinghe/Documents/University/7\ Semester/Doctracer/doctracer

# Start the Flask API server
python backend/api.py
```

The API will start on `http://localhost:5000`

### 2. Start the Frontend

```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Test the Integration

```bash
# Run the API test script
python test_api.py
```

## Features

### Interactive Network Graph

The enhanced NetworkGraph component provides:

1. **Multiple View Modes**:
   - **Complete Graph**: Shows all gazettes and their relationships
   - **Amendment Focus**: Shows a specific amendment and its related gazettes
   - **Base Gazette Focus**: Shows a specific base gazette and its amendments

2. **Interactive Controls**:
   - Drag nodes to reposition them
   - Zoom in/out with mouse wheel
   - Click nodes/links for details
   - Search functionality for gazettes

3. **Visual Elements**:
   - Color-coded nodes (blue for amendments, gray for base gazettes)
   - Animated links showing relationships
   - Real-time statistics panel
   - Comprehensive legend

### API Endpoints

The backend provides these new endpoints:

- `GET /gazettes` - Get all base gazettes
- `GET /amendments` - Get all amendment gazettes
- `GET /graph/complete` - Get complete graph data
- `GET /amendments/{id}/graph` - Get graph for specific amendment
- `GET /gazettes/{id}/details` - Get detailed gazette information
- `GET /search?q={query}&type={type}` - Search gazettes

## Usage

1. **Navigate to Network View**: Click on "Network" in the navigation menu
2. **Choose View Mode**: Select from Complete Graph, Amendment Focus, or Base Gazette Focus
3. **Select Specific Gazette**: If not using Complete Graph, select a gazette from the dropdown
4. **Search**: Use the search bar to find specific gazettes
5. **Interact**: Drag nodes, zoom, and click for more details

## Troubleshooting

### Common Issues

1. **Connection Errors**: 
   - Ensure Flask server is running on port 5000
   - Check Neo4j connection settings in `backend/api.py`

2. **No Data Showing**:
   - Verify data has been loaded into Neo4j
   - Run the test script to check API endpoints
   - Check Neo4j browser for data existence

3. **Frontend Not Loading**:
   - Ensure all npm dependencies are installed
   - Check that the development server is running
   - Verify API_URL in frontend configuration

### Environment Variables

Make sure these environment variables are set (or use defaults):

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123
```

## Data Structure

The system expects Neo4j nodes with these labels:
- `BaseGazette` - Base gazette documents
- `AmendmentGazette` - Amendment documents
- `Minister` - Minister entities
- `Department` - Department entities
- `Law` - Law entities

With properties:
- `gazette_id` - Unique identifier
- `published_date` - Publication date
- `parent_gazette_id` - For amendments, the parent gazette ID

## Next Steps

1. **Add More Data**: Load additional gazettes and amendments
2. **Enhance Visualization**: Add more interactive features
3. **Export Functionality**: Add ability to export graph data
4. **Advanced Filtering**: Add more sophisticated filtering options
5. **Performance Optimization**: Optimize for larger datasets

## Support

If you encounter issues:
1. Check the browser console for errors
2. Check the Flask server logs
3. Verify Neo4j connectivity
4. Run the test script to diagnose API issues
