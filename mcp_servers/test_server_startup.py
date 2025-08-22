#!/usr/bin/env python3
"""
Simple test to verify MCP servers can start without errors
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append('../../')

def test_extraction_server_import():
    """Test if extraction server can be imported"""
    try:
        from extraction_server.server import ExtractionMCPServer
        print("✅ Extraction server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import extraction server: {e}")
        return False

def test_prompt_server_import():
    """Test if prompt server can be imported"""
    try:
        from prompt_server.server import PromptMCPServer
        print("✅ Prompt server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import prompt server: {e}")
        return False

def test_server_creation():
    """Test if servers can be created without errors"""
    try:
        from extraction_server.server import ExtractionMCPServer
        from prompt_server.server import PromptMCPServer
        
        # Create server instances
        extraction_server = ExtractionMCPServer()
        prompt_server = PromptMCPServer()
        
        print("✅ Both servers created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create servers: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing MCP Server Startup...\n")
    
    # Test imports
    extraction_ok = test_extraction_server_import()
    prompt_ok = test_prompt_server_import()
    
    print()
    
    if extraction_ok and prompt_ok:
        # Test server creation
        creation_ok = test_server_creation()
        
        print(f"\nTest Results:")
        print(f"  Extraction server import: {'✅ PASS' if extraction_ok else '❌ FAIL'}")
        print(f"  Prompt server import: {'✅ PASS' if prompt_ok else '❌ FAIL'}")
        print(f"  Server creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
        
        if all([extraction_ok, prompt_ok, creation_ok]):
            print("\n🎉 All tests passed! MCP servers are ready to use.")
            print("\nTo start the servers:")
            print("  # Terminal 1 - Start extraction server")
            print("  cd extraction_server && python server.py")
            print("  # Terminal 2 - Start prompt server")
            print("  cd prompt_server && python server.py")
        else:
            print("\n⚠️  Some tests failed. Check the error messages above.")
    else:
        print("\n❌ Cannot test server creation without successful imports.")

if __name__ == "__main__":
    main()

