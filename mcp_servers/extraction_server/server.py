#!/usr/bin/env python3
"""
Extraction MCP Server for DocTracer
Handles PDF text extraction and gazette processing
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ErrorData,
    RequestId,
    JSONRPCError,
    INTERNAL_ERROR,
    PARSE_ERROR,
    ServerCapabilities,
    ResourcesCapability,
    ToolsCapability,
)

# Import the extraction logic from the main doctracer package
import sys
sys.path.append('../../')
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.extract.gazette.extragazetteamendment import ExtraGazetteAmendmentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractionMCPServer:
    def __init__(self):
        self.server = Server("extraction-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="extraction:pdf",
                    name="PDF Extraction",
                    description="Extract text from PDF documents",
                    mimeType="application/pdf"
                ),
                Resource(
                    uri="extraction:gazette",
                    name="Gazette Processing",
                    description="Process government gazette documents",
                    mimeType="text/plain"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Read resource content"""
            if uri.startswith("extraction:pdf"):
                return [TextContent(
                    type="text",
                    text="PDF extraction service available"
                )]
            elif uri.startswith("extraction:gazette"):
                return [TextContent(
                    type="text",
                    text="Gazette processing service available"
                )]
            else:
                raise JSONRPCError(
                    code=PARSE_ERROR,
                    message=f"Resource not found: {uri}"
                )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Execute extraction tools"""
            
            if name == "extract_pdf_text":
                return await self.extract_pdf_text(arguments)
            elif name == "process_gazette":
                return await self.process_gazette(arguments)
            elif name == "extract_gazette_amendments":
                return await self.extract_gazette_amendments(arguments)
            else:
                raise JSONRPCError(
                    code=PARSE_ERROR,
                    message=f"Unknown tool: {name}"
                )
    
    async def extract_pdf_text(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Extract text from PDF file"""
        try:
            pdf_path = arguments.get("pdf_path")
            output_dir = arguments.get("output_dir", "output")
            
            if not pdf_path:
                raise ValueError("pdf_path is required")
            
            # Extract text using the existing doctracer logic
            extracted_text = extract_text_from_pdfplumber(pdf_path, output_dir)
            
            return [TextContent(
                type="text",
                text=extracted_text
            )]
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to extract PDF text: {str(e)}"
            )
    
    async def process_gazette(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Process government gazette document"""
        try:
            gazette_text = arguments.get("gazette_text")
            gazette_type = arguments.get("gazette_type", "base")
            
            if not gazette_text:
                raise ValueError("gazette_text is required")
            
            # Use the appropriate processor based on type
            if gazette_type == "amendment":
                processor = ExtraGazetteAmendmentProcessor()
            else:
                processor = BaseGazetteProcessor()
            
            # Process the gazette
            result = processor.process(gazette_text)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error processing gazette: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to process gazette: {str(e)}"
            )
    
    async def extract_gazette_amendments(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Extract amendments from gazette document"""
        try:
            gazette_text = arguments.get("gazette_text")
            
            if not gazette_text:
                raise ValueError("gazette_text is required")
            
            processor = ExtraGazetteAmendmentProcessor()
            amendments = processor.extract_amendments(gazette_text)
            
            return [TextContent(
                type="text",
                text=json.dumps(amendments, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error extracting amendments: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to extract amendments: {str(e)}"
            )

async def main():
    """Main entry point"""
    server = ExtractionMCPServer()
    
    # Create stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="extraction-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    resources=ResourcesCapability(),
                    tools=ToolsCapability(),
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
