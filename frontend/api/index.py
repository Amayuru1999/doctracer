from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path

app = FastAPI(title="Government Structure API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data structure for demonstration
# In production, this would connect to your actual database
MOCK_TREE_DATA = {
    "name": "Government of Sri Lanka",
    "children": [
        {
            "name": "Ministry of Finance",
            "type": "minister",
            "source": "base",
            "status": "unchanged",
            "children": [
                {
                    "name": "Department of Treasury",
                    "type": "department",
                    "source": "base",
                    "status": "unchanged"
                },
                {
                    "name": "Department of Customs",
                    "type": "department",
                    "source": "base",
                    "status": "unchanged"
                }
            ]
        },
        {
            "name": "Ministry of Education",
            "type": "minister",
            "source": "base",
            "status": "unchanged",
            "children": [
                {
                    "name": "Department of Schools",
                    "type": "department",
                    "source": "base",
                    "status": "unchanged"
                }
            ]
        },
        {
            "name": "Ministry of Health",
            "type": "minister",
            "source": "amendment",
            "status": "added",
            "children": [
                {
                    "name": "Department of Public Health",
                    "type": "department",
                    "source": "amendment",
                    "status": "added"
                }
            ]
        }
    ]
}

MOCK_SUMMARY_DATA = {
    "node_counts": [
        {"NodeType": "Department", "Count": 195},
        {"NodeType": "Function", "Count": 251},
        {"NodeType": "Law", "Count": 160},
        {"NodeType": "Gazette", "Count": 1}
    ],
    "changes": [
        {"Status": "ADDED_DEPARTMENTS", "Count": 2},
        {"Status": "ADDED_LAWS", "Count": 2},
        {"Status": "ADDED_FUNCTIONS", "Count": 1}
    ]
}

MOCK_DEPARTMENT_CHANGES = {
    "all_changes": [
        {
            "minister": "Ministry of Finance",
            "department": "Department of Treasury",
            "status": "unchanged",
            "type": "department"
        },
        {
            "minister": "Ministry of Health",
            "department": "Department of Public Health",
            "status": "added",
            "type": "department"
        }
    ]
}

@app.get("/")
async def root():
    return {"message": "Government Structure API is running"}

@app.get("/api/tree")
async def get_tree_data():
    """Get the government structure tree data"""
    try:
        return MOCK_TREE_DATA
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tree data: {str(e)}")

@app.get("/api/summary")
async def get_summary_data():
    """Get summary statistics and node counts"""
    try:
        return MOCK_SUMMARY_DATA
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary data: {str(e)}")

@app.get("/api/departments")
async def get_department_changes():
    """Get department changes and modifications"""
    try:
        return MOCK_DEPARTMENT_CHANGES
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching department changes: {str(e)}")

@app.get("/api/filter")
async def filter_data(source: str, status: str):
    """Filter data based on source and status"""
    try:
        # Mock filtering logic
        filtered_data = {
            "name": "Filtered Government Structure",
            "children": []
        }
        
        # Filter ministers based on criteria
        for minister in MOCK_TREE_DATA["children"]:
            if (source == "all" or minister["source"] == source) and \
               (status == "all" or minister["status"] == status):
                filtered_data["children"].append(minister)
        
        return filtered_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Government Structure API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
