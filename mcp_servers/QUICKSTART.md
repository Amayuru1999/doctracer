# Quick Start Guide - DocTracer MCP Servers

This guide will get you up and running with the DocTracer MCP servers in under 10 minutes.

## Prerequisites

- Python 3.9+
- Git (to clone the repository)
- API keys for AI services (OpenAI, Anthropic) - optional for basic testing

## Step 1: Clone and Navigate

```bash
git clone <your-repo-url>
cd doctracer/mcp_servers
```

## Step 2: Setup Environment

```bash
# Run the automated setup script
./setup_environment.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Set up the Python path

## Step 3: Test the Setup

```bash
# Test if everything is working
python test_servers.py
```

You should see:
```
✅ Doctracer imports: PASS
✅ Extraction server: PASS  
✅ Prompt server: PASS

🎉 All tests passed! MCP servers are ready to use.
```

## Step 4: Start the Servers

### Option A: Using Startup Scripts

```bash
# Terminal 1 - Start extraction server
./extraction_server/start_server.sh

# Terminal 2 - Start prompt server  
./prompt_server/start_server.sh
```

### Option B: Manual Start

```bash
# Terminal 1
cd extraction_server
export PYTHONPATH="../../:$PYTHONPATH"
python server.py

# Terminal 2
cd prompt_server
export PYTHONPATH="../../:$PYTHONPATH"
export OPENAI_API_KEY="your-key"  # if using OpenAI
export ANTHROPIC_API_KEY="your-key"  # if using Anthropic
python server.py
```

## Step 5: Test with Example Client

```bash
# In a new terminal
python client_example.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the mcp_servers directory
   pwd  # Should show .../doctracer/mcp_servers
   
   # Check if virtual environment is activated
   which python  # Should show .../venv/bin/python
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall requirements
   pip install -r extraction_server/requirements.txt
   pip install -r prompt_server/requirements.txt
   ```

3. **Python Path Issues**
   ```bash
   # Set Python path manually
   export PYTHONPATH="../../:$PYTHONPATH"
   echo $PYTHONPATH  # Should include the main doctracer directory
   ```

### Getting Help

- Check the logs in the terminal where you started the servers
- Run `python test_servers.py` to identify specific issues
- Ensure all dependencies are installed in the virtual environment

## Next Steps

Once the servers are running:

1. **Explore the API**: Check the `README.md` for detailed API documentation
2. **Customize**: Modify the server configurations in `config.json` files
3. **Extend**: Add new tools by following the patterns in the existing code
4. **Deploy**: Use Docker Compose for containerized deployment

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│  Extraction    │    │    Prompt       │
│   MCP Server   │    │   MCP Server    │
│                 │    │                 │
│ • PDF Extract  │    │ • AI Prompts    │
│ • Gazette Proc │    │ • OpenAI/Claude │
│ • Table Recog  │    │ • Templates     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│           Main DocTracer               │
│        (Your Application)              │
└─────────────────────────────────────────┘
```

## Support

- Check the `ARCHITECTURE.md` for detailed technical information
- Review the `README.md` for comprehensive documentation
- Test with the provided examples to understand usage patterns

Happy coding! 🚀
