# DocTracer MCP Server Architecture

## Overview

This document describes the architecture of the DocTracer MCP (Model Context Protocol) servers, which separate the extraction and prompt engineering functionality into modular, independently deployable services.

## Architecture Goals

1. **Separation of Concerns**: Extract PDF processing and AI prompt execution into separate services
2. **Modularity**: Each server can be developed, tested, and deployed independently
3. **Scalability**: Services can be scaled horizontally based on demand
4. **Maintainability**: Clear interfaces and separation make the codebase easier to maintain
5. **Reusability**: MCP servers can be used by other applications beyond DocTracer

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main App     │    │  Extraction     │    │   Prompt        │
│  (DocTracer)   │◄──►│   MCP Server    │    │   MCP Server    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Neo4j DB     │    │   PDF Files     │    │   AI Models     │
│                 │    │                 │    │  (OpenAI, etc.) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Server Details

### 1. Extraction MCP Server

**Purpose**: Handles PDF text extraction and gazette document processing

**Key Components**:
- PDF text extraction using docling
- Gazette document processing
- Amendment extraction
- Table structure recognition

**Tools Available**:
- `extract_pdf_text`: Extract text from PDF documents
- `process_gazette`: Process government gazette documents
- `extract_gazette_amendments`: Extract amendments from gazettes

**Dependencies**:
- docling (PDF processing)
- pdfplumber (PDF text extraction)
- Main DocTracer extraction modules

### 2. Prompt MCP Server

**Purpose**: Manages AI model interactions and prompt execution

**Key Components**:
- OpenAI integration
- Anthropic integration
- Prompt template management
- Vision model support

**Tools Available**:
- `execute_prompt`: Execute text-based prompts
- `execute_vision_prompt`: Execute vision-based prompts
- `get_prompt_template`: Retrieve prompt templates
- `list_available_prompts`: List all available templates

**Dependencies**:
- OpenAI Python client
- Anthropic Python client
- Main DocTracer prompt modules

## Integration Points

### 1. Import Strategy

Both servers import functionality from the main DocTracer package:

```python
import sys
sys.path.append('../../')
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.prompt.executor import PromptExecutor
```

This approach:
- Maintains existing functionality
- Allows for gradual migration
- Preserves the current API

### 2. Data Flow

```
PDF Document → Extraction Server → Extracted Text → Prompt Server → AI Analysis → Results
```

### 3. Configuration Management

Each server has its own configuration:
- Environment variables for API keys
- Python path configuration
- MCP server settings

## Deployment Options

### 1. Local Development

```bash
# Setup environment
./setup_environment.sh

# Start servers
./extraction_server/start_server.sh
./prompt_server/start_server.sh
```

### 2. Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Individual containers
docker build -f extraction_server/Dockerfile .
docker build -f prompt_server/Dockerfile .
```

### 3. Production Deployment

- Use process managers (systemd, supervisor)
- Implement health checks
- Add monitoring and logging
- Use reverse proxies for HTTP interfaces

## API Design

### MCP Protocol Compliance

Both servers implement the MCP protocol:
- Resource listing and reading
- Tool execution
- Error handling
- Async/await support

### Tool Interface

All tools follow a consistent pattern:
```python
async def tool_name(self, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        # Validate arguments
        # Execute logic
        # Return results
    except Exception as e:
        # Handle errors
        raise ResponseError(...)
```

## Error Handling

### 1. Input Validation

- Required parameter checking
- Type validation
- Path existence verification

### 2. Exception Handling

- Graceful degradation
- Detailed error messages
- Logging for debugging

### 3. Response Codes

- Success: 200 OK
- Client Error: 400 Bad Request
- Server Error: 500 Internal Server Error
- Not Found: 404 Resource Not Found

## Testing Strategy

### 1. Unit Tests

- Individual tool testing
- Mock external dependencies
- Error condition testing

### 2. Integration Tests

- End-to-end workflow testing
- Server communication testing
- Real PDF processing

### 3. Performance Tests

- Load testing
- Memory usage monitoring
- Response time measurement

## Monitoring and Observability

### 1. Logging

- Structured logging
- Different log levels
- Request/response logging

### 2. Metrics

- Request counts
- Response times
- Error rates
- Resource usage

### 3. Health Checks

- Service availability
- Dependency status
- Performance indicators

## Future Enhancements

### 1. HTTP Interface

- REST API endpoints
- GraphQL support
- WebSocket for real-time updates

### 2. Authentication

- API key management
- OAuth integration
- Role-based access control

### 3. Caching

- Redis integration
- Response caching
- Template caching

### 4. Queue System

- Async job processing
- Background tasks
- Job scheduling

## Migration Path

### Phase 1: MCP Server Implementation
- [x] Create server structure
- [x] Implement basic tools
- [x] Add configuration files

### Phase 2: Integration Testing
- [ ] Test with real documents
- [ ] Validate performance
- [ ] Fix integration issues

### Phase 3: Production Deployment
- [ ] Deploy to staging
- [ ] Load testing
- [ ] Production rollout

### Phase 4: Feature Enhancement
- [ ] Add new tools
- [ ] Improve error handling
- [ ] Add monitoring

## Conclusion

The MCP server architecture provides a solid foundation for:
- Modular development
- Independent scaling
- Better maintainability
- Enhanced reusability

This design allows the DocTracer project to evolve while maintaining backward compatibility and providing clear interfaces for future enhancements.
