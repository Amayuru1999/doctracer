# DocTracer MCP Servers

This directory contains Model Context Protocol (MCP) servers that separate the extraction and prompt engineering functionality from the main DocTracer application.

## Overview

The DocTracer project has been refactored to use MCP servers for better modularity and service separation:

1. **Extraction Server** (`extraction_server/`) - Handles PDF text extraction and gazette processing
2. **Prompt Server** (`prompt_server/`) - Manages AI model interactions and prompt execution

## Architecture

```
mcp_servers/
├── extraction_server/          # PDF extraction and gazette processing
│   ├── server.py              # Main MCP server implementation
│   ├── requirements.txt       # Python dependencies
│   ├── config.json           # MCP server configuration
│   └── start_server.sh       # Startup script
├── prompt_server/             # AI prompt execution and management
│   ├── server.py              # Main MCP server implementation
│   ├── requirements.txt       # Python dependencies
│   ├── config.json           # MCP server configuration
│   └── start_server.sh       # Startup script
├── client_example.py          # Example client usage
└── README.md                  # This file
```

## Prerequisites

- Python 3.9+
- Access to the main DocTracer package
- Required API keys for AI services (OpenAI, Anthropic)

## Installation

### 1. Install Dependencies

For each server, install the required dependencies:

```bash
# Extraction server
cd mcp_servers/extraction_server
pip install -r requirements.txt

# Prompt server
cd mcp_servers/prompt_server
pip install -r requirements.txt
```

### 2. Set Environment Variables

For the prompt server, set your API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Usage

### Starting the Servers

#### Extraction Server

```bash
cd mcp_servers/extraction_server
./start_server.sh
```

Or manually:

```bash
cd mcp_servers/extraction_server
export PYTHONPATH="../../:$PYTHONPATH"
python server.py
```

#### Prompt Server

```bash
cd mcp_servers/prompt_server
./start_server.sh
```

Or manually:

```bash
cd mcp_servers/prompt_server
export PYTHONPATH="../../:$PYTHONPATH"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
python server.py
```

### Using the Client Example

```bash
cd mcp_servers
python client_example.py
```

## API Reference

### Extraction Server Tools

#### `extract_pdf_text`
Extract text from a PDF document.

**Arguments:**
- `pdf_path` (required): Path to the PDF file
- `output_dir` (optional): Output directory for results (default: "output")

**Returns:** Extracted text content

#### `process_gazette`
Process government gazette documents.

**Arguments:**
- `gazette_text` (required): Text content of the gazette
- `gazette_type` (optional): Type of gazette ("base" or "amendment", default: "base")

**Returns:** Processed gazette data

#### `extract_gazette_amendments`
Extract amendments from gazette documents.

**Arguments:**
- `gazette_text` (required): Text content of the gazette

**Returns:** Extracted amendments data

### Prompt Server Tools

#### `execute_prompt`
Execute a text-based prompt with an AI model.

**Arguments:**
- `prompt` (required): The prompt text to execute
- `provider` (optional): AI provider ("openai" or "anthropic", default: "openai")
- `model` (optional): Model name (e.g., "gpt-4", "claude-3", default: "gpt-4")

**Returns:** AI model response

#### `execute_vision_prompt`
Execute a vision-based prompt with an AI model.

**Arguments:**
- `prompt` (required): The prompt text to execute
- `image_path` (required): Path to the image file
- `provider` (optional): AI provider (currently only "openai" supported)
- `model` (optional): Model name (default: "gpt-4-vision")

**Returns:** AI model response

#### `get_prompt_template`
Retrieve a specific prompt template from the catalog.

**Arguments:**
- `template_name` (required): Name of the template to retrieve

**Returns:** Template content

#### `list_available_prompts`
List all available prompt templates.

**Arguments:** None

**Returns:** List of available prompt templates

## Configuration

### MCP Server Configuration

Each server includes a `config.json` file that defines the MCP server configuration:

```json
{
  "mcpServers": {
    "server_name": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "PYTHONPATH": "../../",
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### Environment Variables

- `PYTHONPATH`: Path to include the main DocTracer package
- `OPENAI_API_KEY`: OpenAI API key for the prompt server
- `ANTHROPIC_API_KEY`: Anthropic API key for the prompt server

## Integration with Main DocTracer

The MCP servers import functionality from the main DocTracer package:

```python
import sys
sys.path.append('../../')
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.prompt.executor import PromptExecutor
```

This allows the servers to leverage existing functionality while providing a clean MCP interface.

## Development

### Adding New Tools

To add new tools to either server:

1. Add the tool method to the server class
2. Register it in the `setup_handlers()` method
3. Update the `call_tool()` handler to route to the new tool

### Testing

Test the servers individually:

```bash
# Test extraction server
cd mcp_servers/extraction_server
python -c "from server import ExtractionMCPServer; print('Server imported successfully')"

# Test prompt server
cd mcp_servers/prompt_server
python -c "from server import PromptMCPServer; print('Server imported successfully')"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes the main DocTracer package
2. **API Key Errors**: Verify environment variables are set correctly
3. **Dependency Issues**: Install requirements for each server separately

### Logs

Both servers include logging configuration. Check console output for error messages and debugging information.

## Contributing

When contributing to the MCP servers:

1. Follow the existing code structure
2. Add appropriate error handling
3. Include logging for debugging
4. Update this README for new features
5. Test with the client example

## License

This project follows the same license as the main DocTracer project.
