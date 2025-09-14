#!/usr/bin/env python3
"""
Test script to verify MCP servers can be imported correctly
"""

import sys
import os

def test_extraction_server():
    """Test if extraction server can be imported"""
    try:
        sys.path.append('extraction_server')
        from extraction_server.server import ExtractionMCPServer
        print("✅ Extraction server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import extraction server: {e}")
        return False

def test_prompt_server():
    """Test if prompt server can be imported"""
    try:
        sys.path.append('prompt_server')
        from prompt_server.server import PromptMCPServer
        print("✅ Prompt server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import prompt server: {e}")
        return False

def test_doctracer_imports():
    """Test if main doctracer modules can be imported"""
    try:
        # Add the main doctracer package to path
        sys.path.append('../../')
        
        # Test extraction imports
        from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
        print("✅ PDF extractor imported successfully")
        
        # Test prompt imports
        from doctracer.prompt.executor import PromptExecutor
        print("✅ Prompt executor imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import doctracer modules: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing MCP Server Imports...\n")
    
    # Test doctracer imports first
    doctracer_ok = test_doctracer_imports()
    print()
    
    if doctracer_ok:
        # Test individual servers
        extraction_ok = test_extraction_server()
        prompt_ok = test_prompt_server()
        
        print(f"\nTest Results:")
        print(f"  Doctracer imports: {'✅ PASS' if doctracer_ok else '❌ FAIL'}")
        print(f"  Extraction server: {'✅ PASS' if extraction_ok else '❌ FAIL'}")
        print(f"  Prompt server: {'✅ PASS' if prompt_ok else '❌ FAIL'}")
        
        if all([doctracer_ok, extraction_ok, prompt_ok]):
            print("\n🎉 All tests passed! MCP servers are ready to use.")
        else:
            print("\n⚠️  Some tests failed. Check the error messages above.")
    else:
        print("\n❌ Cannot test MCP servers without doctracer imports working.")

if __name__ == "__main__":
    main()
