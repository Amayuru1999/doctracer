#!/usr/bin/env python3
"""
Simplified Government Gazette Structure Analyzer using OpenAI

This version works without Landing AI, using basic PDF text extraction
and OpenAI for intelligent analysis.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import openai
import PyPDF2
import fitz  # PyMuPDF

# Load environment variables
load_dotenv()

class SimpleGazetteAnalyzer:
    """Simplified analyzer that works without Landing AI"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the analyzer with OpenAI API key"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"⚠️ PyMuPDF failed: {e}. Trying PyPDF2...")
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                return text
            except Exception as e2:
                print(f"❌ Both PDF extractors failed: {e2}")
                return ""
    
    def extract_gazette_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content from a gazette PDF using basic text extraction and OpenAI"""
        print(f"📄 Extracting content from: {pdf_path}")
        
        try:
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_path)
            
            if not text_content.strip():
                raise Exception("No text content extracted from PDF")
            
            # Extract metadata and structure using OpenAI
            metadata = self._extract_metadata_with_openai(text_content)
            structure = self._extract_government_structure_with_openai(text_content)
            
            return {
                "metadata": metadata,
                "structure": structure,
                "text_content": text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            }
            
        except Exception as e:
            print(f"❌ Error extracting content from {pdf_path}: {str(e)}")
            raise
    
    def _extract_metadata_with_openai(self, content: str) -> Dict[str, str]:
        """Extract metadata using OpenAI"""
        try:
            prompt = f"""
Extract metadata from this government gazette text. Return only a JSON object with these fields:
- gazette_id: The gazette number/ID
- published_date: The publication date
- published_by: Who published it (usually "Authority")

Text:
{content[:4000]}

Return only valid JSON, no explanations.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert government document analyst. Extract metadata from government gazettes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response and parse JSON
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            metadata = json.loads(result)
            
            # Ensure all required fields exist
            metadata.setdefault("gazette_id", "UNKNOWN")
            metadata.setdefault("published_date", "UNKNOWN")
            metadata.setdefault("published_by", "UNKNOWN")
            
            return metadata
            
        except Exception as e:
            print(f"⚠️ OpenAI metadata extraction failed: {e}. Using fallback.")
            return {
                "gazette_id": "UNKNOWN",
                "published_date": "UNKNOWN",
                "published_by": "UNKNOWN"
            }
    
    def _extract_government_structure_with_openai(self, content: str) -> Dict[str, Any]:
        """Extract government structure using OpenAI"""
        try:
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
{content[:8000]}

Return only valid JSON. Do not include any explanations or markdown formatting.
"""
            
            response = self.client.chat.completions.create(
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
            print(f"⚠️ OpenAI structure extraction failed: {e}. Using fallback.")
            return {
                "ministers": [],
                "state_ministers": []
            }
    
    def apply_amendments(self, base_structure: Dict[str, Any], amendment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply amendments to the base structure using OpenAI"""
        try:
            amendment_content = amendment_data.get("text_content", "")
            
            prompt = f"""
You are an expert in analyzing government gazette amendments. Extract all amendment operations from the following amendment gazette content.

Identify and extract all amendment operations such as:
- Deletions of ministers/portfolios
- Insertions of new ministers/portfolios  
- Renumbering of sections
- Modifications to existing portfolios
- Changes to departments, laws, or functions

Return the data in the following JSON format:
{{
    "operations": [
        {{
            "type": "DELETE|INSERT|RENUMBER|MODIFY",
            "heading_number": "section number if applicable",
            "minister_name": "name of minister/portfolio",
            "details": "description of the change",
            "departments_added": ["dept1", "dept2"],
            "departments_removed": ["dept1", "dept2"],
            "laws_added": ["law1", "law2"],
            "laws_removed": ["law1", "law2"],
            "functions_added": ["func1", "func2"],
            "functions_removed": ["func1", "func2"]
        }}
    ]
}}

Amendment Gazette Content:
{amendment_content[:8000]}

Return only valid JSON. Do not include any explanations or markdown formatting.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert government amendment analyst. Extract structured amendment operations from government gazettes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response and parse JSON
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            parsed_result = json.loads(result)
            operations = parsed_result.get("operations", [])
            
            # Apply operations to base structure
            current_structure = json.loads(json.dumps(base_structure))  # Deep copy
            
            for operation in operations:
                current_structure = self._apply_operation(current_structure, operation)
            
            return current_structure
            
        except Exception as e:
            print(f"⚠️ OpenAI amendment analysis failed: {e}. Returning base structure unchanged.")
            return base_structure
    
    def _apply_operation(self, structure: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single amendment operation to the structure"""
        op_type = operation["type"]
        
        if op_type == "DELETE":
            # Remove minister from structure
            minister_name = operation.get("minister_name", "")
            structure["ministers"] = [
                m for m in structure["ministers"] 
                if minister_name not in m["name"]
            ]
            structure["state_ministers"] = [
                m for m in structure["state_ministers"] 
                if minister_name not in m["name"]
            ]
        
        elif op_type == "INSERT":
            # Add new minister with details from operation
            new_minister = {
                "name": operation.get("minister_name", "New Minister"),
                "departments": operation.get("departments_added", []),
                "laws": operation.get("laws_added", []),
                "functions": operation.get("functions_added", []),
                "purview": operation.get("details", ""),
                "special_priorities": []
            }
            structure["ministers"].append(new_minister)
        
        elif op_type == "MODIFY":
            # Modify existing minister
            minister_name = operation.get("minister_name", "")
            for minister in structure["ministers"] + structure["state_ministers"]:
                if minister_name in minister["name"]:
                    # Add new departments/laws/functions
                    minister["departments"].extend(operation.get("departments_added", []))
                    minister["laws"].extend(operation.get("laws_added", []))
                    minister["functions"].extend(operation.get("functions_added", []))
                    
                    # Remove departments/laws/functions
                    for dept in operation.get("departments_removed", []):
                        if dept in minister["departments"]:
                            minister["departments"].remove(dept)
                    for law in operation.get("laws_removed", []):
                        if law in minister["laws"]:
                            minister["laws"].remove(law)
                    for func in operation.get("functions_removed", []):
                        if func in minister["functions"]:
                            minister["functions"].remove(func)
                    break
        
        return structure
    
    def analyze_amendment_impact(self, base_structure: Dict[str, Any], current_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of amendments"""
        def index_by_name(ministers: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
            return {m.get("name", ""): m for m in ministers}

        base_min = base_structure.get("ministers", [])
        base_state_min = base_structure.get("state_ministers", [])
        curr_min = current_structure.get("ministers", [])
        curr_state_min = current_structure.get("state_ministers", [])

        base_min_map = index_by_name(base_min)
        base_state_min_map = index_by_name(base_state_min)
        curr_min_map = index_by_name(curr_min)
        curr_state_min_map = index_by_name(curr_state_min)

        base_min_names = set(base_min_map.keys())
        curr_min_names = set(curr_min_map.keys())
        base_state_names = set(base_state_min_map.keys())
        curr_state_names = set(curr_state_min_map.keys())

        ministers_added = sorted(list(curr_min_names - base_min_names))
        ministers_removed = sorted(list(base_min_names - curr_min_names))
        state_ministers_added = sorted(list(curr_state_names - base_state_names))
        state_ministers_removed = sorted(list(base_state_names - curr_state_names))

        def list_diff(base_list: List[str], curr_list: List[str]) -> Dict[str, List[str]]:
            base_set = set(base_list or [])
            curr_set = set(curr_list or [])
            return {
                "added": sorted(list(curr_set - base_set)),
                "removed": sorted(list(base_set - curr_set)),
            }

        modified_ministers: List[Dict[str, Any]] = []
        for name in sorted(list(base_min_names & curr_min_names)):
            b = base_min_map.get(name, {})
            c = curr_min_map.get(name, {})
            dept_diff = list_diff(b.get("departments", []), c.get("departments", []))
            law_diff = list_diff(b.get("laws", []), c.get("laws", []))
            func_diff = list_diff(b.get("functions", []), c.get("functions", []))

            if any([dept_diff["added"], dept_diff["removed"],
                    law_diff["added"], law_diff["removed"],
                    func_diff["added"], func_diff["removed"]]):
                modified_ministers.append({
                    "name": name,
                    "departments": dept_diff,
                    "laws": law_diff,
                    "functions": func_diff,
                })

        modified_state_ministers: List[Dict[str, Any]] = []
        for name in sorted(list(base_state_names & curr_state_names)):
            b = base_state_min_map.get(name, {})
            c = curr_state_min_map.get(name, {})
            dept_diff = list_diff(b.get("departments", []), c.get("departments", []))
            law_diff = list_diff(b.get("laws", []), c.get("laws", []))
            func_diff = list_diff(b.get("functions", []), c.get("functions", []))

            if any([dept_diff["added"], dept_diff["removed"],
                    law_diff["added"], law_diff["removed"],
                    func_diff["added"], func_diff["removed"]]):
                modified_state_ministers.append({
                    "name": name,
                    "departments": dept_diff,
                    "laws": law_diff,
                    "functions": func_diff,
                })

        return {
            "ministers_added": ministers_added,
            "ministers_removed": ministers_removed,
            "state_ministers_added": state_ministers_added,
            "state_ministers_removed": state_ministers_removed,
            "modified_ministers": modified_ministers,
            "modified_state_ministers": modified_state_ministers,
        }
    
    def generate_report(self, base_data: Dict[str, Any], amendment_data: Dict[str, Any], 
                       current_structure: Dict[str, Any]) -> str:
        """Generate a comprehensive report"""
        report = []
        report.append("# Government Gazette Structure Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Base Gazette Information
        report.append("## Base Gazette Information")
        report.append(f"- **Gazette ID**: {base_data.get('metadata', {}).get('gazette_id', 'UNKNOWN')}")
        report.append(f"- **Published Date**: {base_data.get('metadata', {}).get('published_date', 'UNKNOWN')}")
        report.append(f"- **Total Ministers**: {len(base_data.get('structure', {}).get('ministers', []))}")
        report.append(f"- **Total State Ministers**: {len(base_data.get('structure', {}).get('state_ministers', []))}")
        report.append("")
        
        # Amendment Gazette Information
        report.append("## Amendment Gazette Information")
        report.append(f"- **Gazette ID**: {amendment_data.get('metadata', {}).get('gazette_id', 'UNKNOWN')}")
        report.append(f"- **Published Date**: {amendment_data.get('metadata', {}).get('published_date', 'UNKNOWN')}")
        report.append("")
        
        # Current Government Structure
        report.append("## Current Government Structure")
        report.append("")
        
        # Ministers
        if current_structure.get('ministers'):
            report.append("### Ministers")
            for i, minister in enumerate(current_structure['ministers'], 1):
                report.append(f"{i}. **{minister['name']}**")
                if minister.get('purview'):
                    report.append(f"   - **Purview**: {minister['purview'][:100]}...")
                if minister.get('departments'):
                    report.append(f"   - **Departments**: {len(minister['departments'])} departments")
                if minister.get('laws'):
                    report.append(f"   - **Laws**: {len(minister['laws'])} laws")
                report.append("")
        
        # State Ministers
        if current_structure.get('state_ministers'):
            report.append("### State Ministers")
            for i, minister in enumerate(current_structure['state_ministers'], 1):
                report.append(f"{i}. **{minister['name']}**")
                if minister.get('purview'):
                    report.append(f"   - **Purview**: {minister['purview'][:100]}...")
                if minister.get('departments'):
                    report.append(f"   - **Departments**: {len(minister['departments'])} departments")
                if minister.get('laws'):
                    report.append(f"   - **Laws**: {len(minister['laws'])} laws")
                report.append("")
        
        # Amendment Impact Analysis
        try:
            impact = self.analyze_amendment_impact(
                base_data.get('structure', {}),
                current_structure
            )
            report.append("## Amendment Impact Analysis")
            report.append("")
            report.append(f"- **Ministers Added**: {len(impact.get('ministers_added', []))}")
            report.append(f"- **Ministers Removed**: {len(impact.get('ministers_removed', []))}")
            report.append(f"- **State Ministers Added**: {len(impact.get('state_ministers_added', []))}")
            report.append(f"- **State Ministers Removed**: {len(impact.get('state_ministers_removed', []))}")
            report.append("")
            if impact.get('modified_ministers'):
                report.append("### Modified Ministers")
                for m in impact['modified_ministers']:
                    report.append(f"- {m['name']}")
                    if m['departments']['added'] or m['departments']['removed']:
                        report.append(f"  - Departments: +{len(m['departments']['added'])} / -{len(m['departments']['removed'])}")
                    if m['laws']['added'] or m['laws']['removed']:
                        report.append(f"  - Laws: +{len(m['laws']['added'])} / -{len(m['laws']['removed'])}")
                    if m['functions']['added'] or m['functions']['removed']:
                        report.append(f"  - Functions: +{len(m['functions']['added'])} / -{len(m['functions']['removed'])}")
                report.append("")
            if impact.get('modified_state_ministers'):
                report.append("### Modified State Ministers")
                for m in impact['modified_state_ministers']:
                    report.append(f"- {m['name']}")
                    if m['departments']['added'] or m['departments']['removed']:
                        report.append(f"  - Departments: +{len(m['departments']['added'])} / -{len(m['departments']['removed'])}")
                    if m['laws']['added'] or m['laws']['removed']:
                        report.append(f"  - Laws: +{len(m['laws']['added'])} / -{len(m['laws']['removed'])}")
                    if m['functions']['added'] or m['functions']['removed']:
                        report.append(f"  - Functions: +{len(m['functions']['added'])} / -{len(m['functions']['removed'])}")
                report.append("")
        except Exception as e:
            report.append(f"⚠️ Could not generate amendment impact analysis: {e}")
        
        return "\n".join(report)
    
    def save_results(self, base_data: Dict[str, Any], amendment_data: Dict[str, Any], 
                    current_structure: Dict[str, Any], report: str):
        """Save all results to files"""
        
        # Save base gazette data
        base_file = self.output_dir / "base_gazette_data.json"
        with open(base_file, 'w', encoding='utf-8') as f:
            json.dump(base_data, f, indent=2, ensure_ascii=False)
        
        # Save amendment gazette data
        amendment_file = self.output_dir / "amendment_gazette_data.json"
        with open(amendment_file, 'w', encoding='utf-8') as f:
            json.dump(amendment_data, f, indent=2, ensure_ascii=False)
        
        # Save current structure
        current_file = self.output_dir / "current_government_structure.json"
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(current_structure, f, indent=2, ensure_ascii=False)
        
        # Save report
        report_file = self.output_dir / "government_structure_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save impact analysis
        impact = self.analyze_amendment_impact(base_data["structure"], current_structure)
        impact_file = self.output_dir / "amendment_impact.json"
        with open(impact_file, 'w', encoding='utf-8') as f:
            json.dump(impact, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to {self.output_dir}/")
        print(f"   - Base gazette data: {base_file}")
        print(f"   - Amendment gazette data: {amendment_file}")
        print(f"   - Current structure: {current_file}")
        print(f"   - Analysis report: {report_file}")
        print(f"   - Amendment impact: {impact_file}")

def main():
    """Main function to run the simplified gazette analyzer"""
    parser = argparse.ArgumentParser(
        description="Analyze government gazette structure using OpenAI (no Landing AI required)"
    )
    parser.add_argument(
        "base_gazette",
        help="Path to the base government gazette PDF"
    )
    parser.add_argument(
        "amendment_gazette", 
        help="Path to the amendment gazette PDF"
    )
    parser.add_argument(
        "--openai-api-key",
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for results (default: output)"
    )
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.base_gazette):
        print(f"❌ Base gazette file not found: {args.base_gazette}")
        return 1
    
    if not os.path.exists(args.amendment_gazette):
        print(f"❌ Amendment gazette file not found: {args.amendment_gazette}")
        return 1
    
    try:
        # Initialize analyzer
        analyzer = SimpleGazetteAnalyzer(openai_api_key=args.openai_api_key)
        
        print("🚀 Starting Simplified Government Gazette Structure Analysis")
        print("=" * 60)
        
        # Extract content from base gazette
        print("\n📋 Processing Base Gazette...")
        base_data = analyzer.extract_gazette_content(args.base_gazette)
        
        # Extract content from amendment gazette
        print("\n📋 Processing Amendment Gazette...")
        amendment_data = analyzer.extract_gazette_content(args.amendment_gazette)
        
        # Apply amendments to get current structure
        print("\n🔄 Analyzing Changes...")
        current_structure = analyzer.apply_amendments(
            base_data["structure"], 
            amendment_data
        )
        
        # Generate report
        print("\n📊 Generating Report...")
        report = analyzer.generate_report(
            base_data, 
            amendment_data, 
            current_structure
        )
        
        # Save results
        analyzer.save_results(base_data, amendment_data, current_structure, report)
        
        print("\n🎉 Analysis Complete!")
        print("\n📋 Summary:")
        print(f"   - Base Gazette: {base_data['metadata']['gazette_id']}")
        print(f"   - Amendment Gazette: {amendment_data['metadata']['gazette_id']}")
        print(f"   - Current Ministers: {len(current_structure.get('ministers', []))}")
        print(f"   - Current State Ministers: {len(current_structure.get('state_ministers', []))}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
