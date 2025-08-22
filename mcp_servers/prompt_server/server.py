#!/usr/bin/env python3
"""
Prompt Engineering MCP Server for DocTracer
Handles AI model interactions and prompt execution
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
import json
import os

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

# Import the prompt logic from the main doctracer package
import sys
sys.path.append('../../')
from doctracer.prompt.executor import PromptExecutor, PromptConfigChat, PromptConfigImage
from doctracer.prompt.provider import ServiceProvider, AIModelProvider
from doctracer.prompt.config import SimpleMessageConfig
from doctracer.prompt.catalog import PromptCatalog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptMCPServer:
    def __init__(self):
        self.server = Server("prompt-server")
        self.prompt_catalog = PromptCatalog()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="prompt:openai",
                    name="OpenAI Integration",
                    description="OpenAI API integration for prompt execution",
                    mimeType="application/json"
                ),
                Resource(
                    uri="prompt:anthropic",
                    name="Anthropic Integration",
                    description="Anthropic API integration for prompt execution",
                    mimeType="application/json"
                ),
                Resource(
                    uri="prompt:catalog",
                    name="Prompt Catalog",
                    description="Available prompt templates and configurations",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Read resource content"""
            if uri.startswith("prompt:catalog"):
                return [TextContent(
                    type="text",
                    text=json.dumps(self.prompt_catalog.get_available_prompts(), indent=2)
                )]
            elif uri.startswith("prompt:openai"):
                return [TextContent(
                    type="text",
                    text="OpenAI prompt execution service available"
                )]
            elif uri.startswith("prompt:anthropic"):
                return [TextContent(
                    type="text",
                    text="Anthropic prompt execution service available"
                )]
            else:
                raise JSONRPCError(
                    code=PARSE_ERROR,
                    message=f"Resource not found: {uri}"
                )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Execute prompt tools"""
            
            if name == "execute_prompt":
                return await self.execute_prompt(arguments)
            elif name == "execute_vision_prompt":
                return await self.execute_vision_prompt(arguments)
            elif name == "get_prompt_template":
                return await self.get_prompt_template(arguments)
            elif name == "list_available_prompts":
                return await self.list_available_prompts(arguments)
            else:
                raise JSONRPCError(
                    code=PARSE_ERROR,
                    message=f"Unknown tool: {name}"
                )
    
    async def execute_prompt(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a text-based prompt"""
        try:
            prompt_text = arguments.get("prompt")
            provider_name = arguments.get("provider", "openai")
            model_name = arguments.get("model", "gpt-4")
            
            if not prompt_text:
                raise ValueError("prompt is required")
            
            # Map provider names to ServiceProvider enum
            provider_map = {
                "openai": ServiceProvider.OPENAI,
                "anthropic": ServiceProvider.ANTHROPIC
            }
            
            # Map model names to AIModelProvider enum
            model_map = {
                "gpt-4": AIModelProvider.GPT4,
                "gpt-3.5-turbo": AIModelProvider.GPT35TURBO,
                "claude-3": AIModelProvider.CLAUDE3
            }
            
            provider = provider_map.get(provider_name.lower())
            model = model_map.get(model_name.lower())
            
            if not provider or not model:
                raise ValueError(f"Unsupported provider: {provider_name} or model: {model_name}")
            
            # Create message config and executor
            message_config = SimpleMessageConfig()
            executor = PromptExecutor(provider, model, message_config)
            
            # Execute prompt
            config = PromptConfigChat(prompt_text)
            result = executor.execute_prompt(config)
            
            return [TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            logger.error(f"Error executing prompt: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to execute prompt: {str(e)}"
            )
    
    async def execute_vision_prompt(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a vision-based prompt"""
        try:
            prompt_text = arguments.get("prompt")
            image_path = arguments.get("image_path")
            provider_name = arguments.get("provider", "openai")
            model_name = arguments.get("model", "gpt-4-vision")
            
            if not prompt_text or not image_path:
                raise ValueError("prompt and image_path are required")
            
            # For vision prompts, we'll use OpenAI vision strategy
            if provider_name.lower() != "openai":
                raise ValueError("Vision prompts currently only support OpenAI")
            
            # Create message config and executor
            message_config = SimpleMessageConfig()
            executor = PromptExecutor(ServiceProvider.OPENAI_VISION, AIModelProvider.GPT4VISION, message_config)
            
            # Execute vision prompt
            config = PromptConfigImage(prompt_text, image_path)
            result = executor.execute_prompt(config)
            
            return [TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            logger.error(f"Error executing vision prompt: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to execute vision prompt: {str(e)}"
            )
    
    async def get_prompt_template(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get a specific prompt template from the catalog"""
        try:
            template_name = arguments.get("template_name")
            
            if not template_name:
                raise ValueError("template_name is required")
            
            template = self.prompt_catalog.get_prompt(template_name)
            
            if not template:
                raise ValueError(f"Template not found: {template_name}")
            
            return [TextContent(
                type="text",
                text=json.dumps(template, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error getting prompt template: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to get prompt template: {str(e)}"
            )
    
    async def list_available_prompts(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """List all available prompt templates"""
        try:
            prompts = self.prompt_catalog.get_available_prompts()
            
            return [TextContent(
                type="text",
                text=json.dumps(prompts, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            raise JSONRPCError(
                code=INTERNAL_ERROR,
                message=f"Failed to list prompts: {str(e)}"
            )

async def main():
    """Main entry point"""
    server = PromptMCPServer()
    
    # Create stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="prompt-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    resources=ResourcesCapability(),
                    tools=ToolsCapability(),
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
