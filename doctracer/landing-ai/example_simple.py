#!/usr/bin/env python3
"""
Example Usage of Simplified Government Gazette Structure Analyzer

This script demonstrates how to use the SimpleGazetteAnalyzer
with the existing gazette files in the data directory.
"""

import os
import sys
from pathlib import Path

# Import the simplified analyzer
from gazette_structure_analyzer_simple import SimpleGazetteAnalyzer

def main():
    """Example usage of the simplified gazette structure analyzer"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define paths to the existing gazette files
    base_gazette_path = current_dir / "data" / "2289-43_E_2022_07_22.pdf"
    amendment_gazette_path = current_dir / "data" / "2297-78_E_2022_09_16.pdf"
    
    # Check if files exist
    if not base_gazette_path.exists():
        print(f"❌ Base gazette file not found: {base_gazette_path}")
        print("Please ensure the file exists in the data directory.")
        return 1
    
    if not amendment_gazette_path.exists():
        print(f"❌ Amendment gazette file not found: {amendment_gazette_path}")
        print("Please ensure the file exists in the data directory.")
        return 1
    
    try:
        # Initialize the analyzer
        print("🚀 Initializing Simplified Gazette Structure Analyzer...")
        analyzer = SimpleGazetteAnalyzer()
        
        print("📋 Processing Base Gazette...")
        print(f"   File: {base_gazette_path}")
        base_data = analyzer.extract_gazette_content(str(base_gazette_path))
        
        print("📋 Processing Amendment Gazette...")
        print(f"   File: {amendment_gazette_path}")
        amendment_data = analyzer.extract_gazette_content(str(amendment_gazette_path))
        
        print("🔄 Applying Amendments...")
        current_structure = analyzer.apply_amendments(
            base_data["structure"], 
            amendment_data
        )
        
        print("📊 Generating Report...")
        report = analyzer.generate_report(
            base_data, 
            amendment_data, 
            current_structure
        )
        
        # Save results
        analyzer.save_results(base_data, amendment_data, current_structure, report)
        
        # Print summary
        print("\n🎉 Analysis Complete!")
        print("\n📋 Summary:")
        print(f"   - Base Gazette ID: {base_data['metadata']['gazette_id']}")
        print(f"   - Amendment Gazette ID: {amendment_data['metadata']['gazette_id']}")
        print(f"   - Current Ministers: {len(current_structure.get('ministers', []))}")
        print(f"   - Current State Ministers: {len(current_structure.get('state_ministers', []))}")
        
        # Print some details about the current structure
        print("\n👥 Current Government Structure:")
        
        if current_structure.get('ministers'):
            print("\n   Ministers:")
            for i, minister in enumerate(current_structure['ministers'][:3], 1):  # Show first 3
                print(f"   {i}. {minister['name']}")
                if minister.get('departments'):
                    print(f"      📁 Departments: {len(minister['departments'])}")
                if minister.get('laws'):
                    print(f"      ⚖️ Laws: {len(minister['laws'])}")
                if minister.get('functions'):
                    print(f"      🔧 Functions: {len(minister['functions'])}")
        
        if current_structure.get('state_ministers'):
            print("\n   State Ministers:")
            for i, minister in enumerate(current_structure['state_ministers'][:3], 1):  # Show first 3
                print(f"   {i}. {minister['name']}")
                if minister.get('departments'):
                    print(f"      📁 Departments: {len(minister['departments'])}")
                if minister.get('laws'):
                    print(f"      ⚖️ Laws: {len(minister['laws'])}")
                if minister.get('functions'):
                    print(f"      🔧 Functions: {len(minister['functions'])}")
        
        print(f"\n📄 Full results saved to: {analyzer.output_dir}/")
        print("   - base_gazette_data.json")
        print("   - amendment_gazette_data.json") 
        print("   - current_government_structure.json")
        print("   - government_structure_report.md")
        print("   - amendment_impact.json")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure OPENAI_API_KEY environment variable is set")
        print("2. Check that the PDF files exist and are readable")
        print("3. Ensure you have the required dependencies installed:")
        print("   pip install PyPDF2 PyMuPDF openai python-dotenv")
        return 1

if __name__ == "__main__":
    exit(main())
