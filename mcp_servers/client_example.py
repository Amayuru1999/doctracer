#!/usr/bin/env python3
"""
Example client for using both Extraction and Prompt MCP servers
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any

class MCPClientExample:
    def __init__(self):
        self.extraction_server_url = "extraction:server"
        self.prompt_server_url = "prompt:server"
    
    async def extract_pdf_text(self, pdf_path: str, output_dir: str = "output") -> str:
        """Extract text from PDF using the extraction MCP server"""
        # This would typically connect to the MCP server
        # For demonstration, we'll show the expected interface
        
        arguments = {
            "pdf_path": pdf_path,
            "output_dir": output_dir
        }
        
        print(f"Calling extraction server with arguments: {arguments}")
        
        # In a real implementation, this would make an MCP call
        # result = await self.extraction_server.call_tool("extract_pdf_text", arguments)
        
        return f"Extracted text from {pdf_path} would be returned here"
    
    async def process_gazette(self, gazette_text: str, gazette_type: str = "base") -> Dict[str, Any]:
        """Process gazette using the extraction MCP server"""
        arguments = {
            "gazette_text": gazette_text,
            "gazette_type": gazette_type
        }
        
        print(f"Calling extraction server with arguments: {arguments}")
        
        # In a real implementation, this would make an MCP call
        # result = await self.extraction_server.call_tool("process_gazette", arguments)
        
        return {"status": "processed", "type": gazette_type}
    
    async def execute_prompt(self, prompt: str, provider: str = "openai", model: str = "gpt-4") -> str:
        """Execute a prompt using the prompt MCP server"""
        arguments = {
            "prompt": prompt,
            "provider": provider,
            "model": model
        }
        
        print(f"Calling prompt server with arguments: {arguments}")
        
        # In a real implementation, this would make an MCP call
        # result = await self.prompt_server.call_tool("execute_prompt", arguments)
        
        return f"Response from {provider} {model} would be returned here"
    
    async def get_prompt_template(self, template_name: str) -> Dict[str, Any]:
        """Get a prompt template from the prompt MCP server"""
        arguments = {
            "template_name": template_name
        }
        
        print(f"Calling prompt server with arguments: {arguments}")
        
        # In a real implementation, this would make an MCP call
        # result = await self.prompt_server.call_tool("get_prompt_template", arguments)
        
        return {"template": template_name, "content": "Template content would be returned here"}
    
    async def run_example_workflow(self):
        """Run a complete example workflow using both servers"""
        print("=== DocTracer MCP Client Example ===\n")
        
        # Example 1: Extract text from PDF
        print("1. Extracting text from PDF...")
        pdf_path = "data/testdata/base/ranil/2289-43_E_2022_07_22.pdf"
        extracted_text = await self.extract_pdf_text(pdf_path)
        print(f"   Result: {extracted_text}\n")
        
        # Example 2: Process gazette
        print("2. Processing gazette...")
        sample_gazette_text = "Sample gazette text content..."
        gazette_result = await self.process_gazette(sample_gazette_text, "amendment")
        print(f"   Result: {gazette_result}\n")
        
        # Example 3: Execute prompt
        print("3. Executing prompt...")
        sample_prompt = "Extract key information from this government document"
        prompt_result = await self.execute_prompt(sample_prompt, "openai", "gpt-4")
        print(f"   Result: {prompt_result}\n")
        
        # Example 4: Get prompt template
        print("4. Getting prompt template...")
        template_result = await self.get_prompt_template("metadata_extraction")
        print(f"   Result: {template_result}\n")
        
        print("=== Workflow completed ===")

async def main():
    """Main entry point"""
    client = MCPClientExample()
    await client.run_example_workflow()

if __name__ == "__main__":
    asyncio.run(main())
