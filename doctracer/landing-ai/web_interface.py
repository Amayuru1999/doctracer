#!/usr/bin/env python3
"""
Web Interface for Government Gazette Structure Analyzer

A Flask web application that allows users to upload government gazettes
and view the current government structure using Landing AI.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from agentic_doc.parse import parse
from agentic_doc.utils import viz_parsed_document
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class GazetteAnalyzer:
    """Analyzer class for processing gazettes"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.api_key = os.getenv("VISION_AGENT_API_KEY")
        if not self.api_key:
            raise ValueError("VISION_AGENT_API_KEY environment variable is not set")
        
        # Initialize OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️ Warning: OPENAI_API_KEY not set. Intelligent analysis will be limited.")
    
    def extract_gazette_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content from a gazette PDF using Landing AI"""
        try:
            # Parse the document using Landing AI
            results = parse(pdf_path)
            parsed_doc = results[0]
            
            # Extract markdown content
            markdown_content = parsed_doc.markdown
            chunks = parsed_doc.chunks
            
            # Generate visual output
            try:
                images = viz_parsed_document(
                    pdf_path,
                    parsed_doc,
                    output_dir=app.config['OUTPUT_FOLDER']
                )
                # Convert image objects to file paths for JSON serialization
                visual_output = [str(img) if hasattr(img, '__str__') else 'image' for img in images] if images else []
            except Exception as e:
                print(f"Warning: Could not generate visual output: {e}")
                visual_output = []
            
            # Extract metadata and structure
            metadata = self._extract_metadata(markdown_content)
            structure = self._extract_government_structure(markdown_content)
            
            return {
                "metadata": metadata,
                "structure": structure,
                "markdown_content": markdown_content,
                "chunks": [chunk.dict() for chunk in chunks],
                "visual_output": visual_output
            }
            
        except Exception as e:
            raise Exception(f"Error extracting content: {str(e)}")
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from gazette content"""
        import re
        
        metadata = {
            "gazette_id": "UNKNOWN",
            "published_date": "UNKNOWN",
            "published_by": "UNKNOWN"
        }
        
        # Extract Gazette ID
        gazette_id_pattern = r'No\.\s*(\d+/\d+)'
        match = re.search(gazette_id_pattern, content)
        if match:
            metadata["gazette_id"] = match.group(1)
        
        # Extract date
        date_pattern = r'(\d{4}-\d{2}-\d{2})|(\d{2}\.\d{2}\.\d{4})'
        match = re.search(date_pattern, content)
        if match:
            metadata["published_date"] = match.group(0)
        
        # Extract publisher
        if "Published by Authority" in content:
            metadata["published_by"] = "Authority"
        
        return metadata
    
    def _extract_government_structure(self, content: str) -> Dict[str, Any]:
        """Extract government structure from gazette content using OpenAI for intelligent parsing"""
        if not self.openai_api_key:
            # Fallback to basic parsing if OpenAI is not available
            return self._extract_government_structure_basic(content)
        
        try:
            if not self.openai_api_key or self.openai_api_key.startswith("{{"):
                print("⚠️ OpenAI API key not properly set. Falling back to basic parsing.")
                return self._extract_government_structure_basic(content)
            
            prompt = f"""
You are an expert in analyzing government gazette documents. Extract the government structure from the following gazette content.

Please identify and extract:
1. Ministers (including their names, departments, laws, functions, purview, and special priorities)
2. State Ministers (including their names, departments, laws, functions, purview, and special priorities)

Return the data in the following JSON format:
{{
    "ministers": [
        {{
            "name": "Minister of [Portfolio Name]",
            "departments": ["Department 1", "Department 2", ...],
            "laws": ["Law 1", "Law 2", ...],
            "functions": ["Function 1", "Function 2", ...],
            "purview": "Description of the minister's purview",
            "special_priorities": ["Priority 1", "Priority 2", ...]
        }}
    ],
    "state_ministers": [
        {{
            "name": "State Minister of [Portfolio Name]",
            "departments": ["Department 1", "Department 2", ...],
            "laws": ["Law 1", "Law 2", ...],
            "functions": ["Function 1", "Function 2", ...],
            "purview": "Description of the state minister's purview",
            "special_priorities": ["Priority 1", "Priority 2", ...]
        }}
    ]
}}

Gazette Content:
{content[:8000]}  # Limit content to avoid token limits

Return only valid JSON. Do not include any explanations or markdown formatting.
"""
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert government document analyst. Extract structured data from government gazettes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response and parse JSON
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            structure = json.loads(result)
            
            # Ensure all required fields exist
            structure.setdefault("ministers", [])
            structure.setdefault("state_ministers", [])
            
            return structure
            
        except Exception as e:
            print(f"⚠️ OpenAI analysis failed: {e}. Falling back to basic parsing.")
            return self._extract_government_structure_basic(content)
    
    def _extract_government_structure_basic(self, content: str) -> Dict[str, Any]:
        """Basic fallback extraction method"""
        import re
        
        structure = {
            "ministers": [],
            "state_ministers": [],
            "departments": {},
            "laws": {}
        }
        
        # Split content into sections
        sections = content.split('\n\n')
        
        current_minister = None
        current_section = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check for minister headings
            if re.match(r'^\d+\.\d+\s+', section) or "Minister of" in section:
                current_minister = {
                    "name": section,
                    "departments": [],
                    "laws": [],
                    "functions": [],
                    "purview": "",
                    "special_priorities": []
                }
                structure["ministers"].append(current_minister)
                current_section = None
            
            # Check for state minister headings
            elif "State Minister of" in section:
                current_minister = {
                    "name": section,
                    "departments": [],
                    "laws": [],
                    "functions": [],
                    "purview": "",
                    "special_priorities": []
                }
                structure["state_ministers"].append(current_minister)
                current_section = None
            
            # Check for section headers
            elif "Purview" in section:
                current_section = "purview"
            elif "Subjects and Functions" in section or "Subjects & Functions" in section:
                current_section = "functions"
            elif "Special Priorities" in section:
                current_section = "priorities"
            elif "Related Institutional and Legal Framework" in section:
                current_section = "framework"
            
            # Process content based on current section
            if current_minister and current_section:
                if current_section == "purview":
                    current_minister["purview"] = section
                elif current_section == "functions":
                    functions = self._extract_list_items(section)
                    current_minister["functions"].extend(functions)
                elif current_section == "priorities":
                    priorities = self._extract_list_items(section)
                    current_minister["special_priorities"].extend(priorities)
                elif current_section == "framework":
                    dept_law_data = self._extract_departments_and_laws(section)
                    current_minister["departments"].extend(dept_law_data.get("departments", []))
                    current_minister["laws"].extend(dept_law_data.get("laws", []))
        
        return structure
    
    def _extract_list_items(self, text: str) -> list:
        """Extract list items from text"""
        import re
        
        items = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                line = re.sub(r'^[\d\.\-\*]+\.?\s*', '', line)
                if line and len(line) > 3:
                    items.append(line)
        return items
    
    def _extract_departments_and_laws(self, text: str) -> Dict[str, list]:
        """Extract departments and laws from framework section"""
        result = {
            "departments": [],
            "laws": []
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                if any(keyword in line.lower() for keyword in ['department', 'authority', 'board', 'corporation', 'institute']):
                    result["departments"].append(line)
                elif any(keyword in line.lower() for keyword in ['act', 'law', 'ordinance', 'regulation']):
                    result["laws"].append(line)
        
        return result
    
    def apply_amendments(self, base_structure: Dict[str, Any], amendment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply amendments to the base structure to get current government structure"""
        import re
        
        current_structure = json.loads(json.dumps(base_structure))  # Deep copy
        
        # Extract amendment operations
        amendment_content = amendment_data.get("markdown_content", "")
        
        # Look for amendment patterns
        amendment_patterns = [
            r'By deleting.*?Heading.*?No\.\s*(\d+\.\d+).*?Minister of ([^,\n]+)',
            r'By insertion of.*?new Heading.*?No\.\s*(\d+\.\d+).*?Minister of ([^,\n]+)',
            r'By re-numbering.*?No\.\s*(\d+\.\d+).*?to.*?No\.\s*(\d+\.\d+)'
        ]
        
        for pattern in amendment_patterns:
            matches = re.finditer(pattern, amendment_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if "deleting" in pattern:
                    # Remove minister
                    minister_name = f"Minister of {match.group(2)}"
                    current_structure["ministers"] = [
                        m for m in current_structure["ministers"] 
                        if minister_name not in m["name"]
                    ]
                    current_structure["state_ministers"] = [
                        m for m in current_structure["state_ministers"] 
                        if minister_name not in m["name"]
                    ]
                elif "insertion" in pattern:
                    # Add new minister
                    new_minister = {
                        "name": f"Minister of {match.group(2)}",
                        "departments": [],
                        "laws": [],
                        "functions": [],
                        "purview": "",
                        "special_priorities": []
                    }
                    current_structure["ministers"].append(new_minister)
        
        return current_structure

    def analyze_amendment_impact(self, base_structure: Dict[str, Any], current_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Compute impact of the amendment compared to the base structure."""
        def index_by_name(ministers: list) -> dict:
            return {m.get("name", ""): m for m in (ministers or [])}

        base_min = base_structure.get("ministers", [])
        base_state = base_structure.get("state_ministers", [])
        curr_min = current_structure.get("ministers", [])
        curr_state = current_structure.get("state_ministers", [])

        base_min_map = index_by_name(base_min)
        curr_min_map = index_by_name(curr_min)
        base_state_map = index_by_name(base_state)
        curr_state_map = index_by_name(curr_state)

        base_min_names = set(base_min_map.keys())
        curr_min_names = set(curr_min_map.keys())
        base_state_names = set(base_state_map.keys())
        curr_state_names = set(curr_state_map.keys())

        def list_diff(a: list, b: list) -> dict:
            sa, sb = set(a or []), set(b or [])
            return {"added": sorted(list(sb - sa)), "removed": sorted(list(sa - sb))}

        modified_ministers = []
        for name in sorted(list(base_min_names & curr_min_names)):
            b = base_min_map.get(name, {})
            c = curr_min_map.get(name, {})
            d_diff = list_diff(b.get("departments", []), c.get("departments", []))
            l_diff = list_diff(b.get("laws", []), c.get("laws", []))
            f_diff = list_diff(b.get("functions", []), c.get("functions", []))
            if any([d_diff["added"], d_diff["removed"], l_diff["added"], l_diff["removed"], f_diff["added"], f_diff["removed"]]):
                modified_ministers.append({
                    "name": name,
                    "departments": d_diff,
                    "laws": l_diff,
                    "functions": f_diff,
                })

        modified_state_ministers = []
        for name in sorted(list(base_state_names & curr_state_names)):
            b = base_state_map.get(name, {})
            c = curr_state_map.get(name, {})
            d_diff = list_diff(b.get("departments", []), c.get("departments", []))
            l_diff = list_diff(b.get("laws", []), c.get("laws", []))
            f_diff = list_diff(b.get("functions", []), c.get("functions", []))
            if any([d_diff["added"], d_diff["removed"], l_diff["added"], l_diff["removed"], f_diff["added"], f_diff["removed"]]):
                modified_state_ministers.append({
                    "name": name,
                    "departments": d_diff,
                    "laws": l_diff,
                    "functions": f_diff,
                })

        return {
            "ministers_added": sorted(list(curr_min_names - base_min_names)),
            "ministers_removed": sorted(list(base_min_names - curr_min_names)),
            "state_ministers_added": sorted(list(curr_state_names - base_state_names)),
            "state_ministers_removed": sorted(list(base_state_names - curr_state_names)),
            "modified_ministers": modified_ministers,
            "modified_state_ministers": modified_state_ministers,
        }

# Initialize analyzer
try:
    analyzer = GazetteAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize analyzer: {e}")
    analyzer = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process gazettes"""
    try:
        # Check if files were uploaded
        if 'base_gazette' not in request.files or 'amendment_gazette' not in request.files:
            return jsonify({'error': 'Both base and amendment gazettes are required'}), 400
        
        base_file = request.files['base_gazette']
        amendment_file = request.files['amendment_gazette']
        
        # Check if files are valid
        if base_file.filename == '' or amendment_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not (allowed_file(base_file.filename) and allowed_file(amendment_file.filename)):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized. Check API key.'}), 500
        
        # Save uploaded files
        base_filename = secure_filename(base_file.filename)
        amendment_filename = secure_filename(amendment_file.filename)
        
        base_path = os.path.join(app.config['UPLOAD_FOLDER'], base_filename)
        amendment_path = os.path.join(app.config['UPLOAD_FOLDER'], amendment_filename)
        
        base_file.save(base_path)
        amendment_file.save(amendment_path)
        
        # Process gazettes
        print("Processing base gazette...")
        base_data = analyzer.extract_gazette_content(base_path)
        
        print("Processing amendment gazette...")
        amendment_data = analyzer.extract_gazette_content(amendment_path)
        
        print("Applying amendments...")
        current_structure = analyzer.apply_amendments(base_data["structure"], amendment_data)

        # Amendment impact analysis
        impact = analyzer.analyze_amendment_impact(base_data["structure"], current_structure)
        
        # Generate summary
        summary = {
            "base_gazette": {
                "id": base_data["metadata"]["gazette_id"],
                "date": base_data["metadata"]["published_date"],
                "ministers_count": len(base_data["structure"]["ministers"]),
                "state_ministers_count": len(base_data["structure"]["state_ministers"])
            },
            "amendment_gazette": {
                "id": amendment_data["metadata"]["gazette_id"],
                "date": amendment_data["metadata"]["published_date"]
            },
            "current_structure": {
                "ministers_count": len(current_structure["ministers"]),
                "state_ministers_count": len(current_structure["state_ministers"]),
                "ministers": current_structure["ministers"],
                "state_ministers": current_structure["state_ministers"]
            }
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(app.config['OUTPUT_FOLDER'], f'analysis_{timestamp}.json')
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "base_data": base_data,
                "amendment_data": amendment_data,
                "current_structure": current_structure,
                "amendment_impact": impact
            }, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'results_file': results_file,
            'amendment_impact': impact
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def download_results(filename):
    """Download analysis results"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'analyzer_initialized': analyzer is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
