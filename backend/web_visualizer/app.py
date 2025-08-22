#!/usr/bin/env python3
"""
DocTracer Web Visualizer - Standalone Flask Application
A web-based visualization tool for government structure analysis
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import doctracer modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_visualizer import app

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting DocTracer Web Visualizer on {host}:{port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Access the application at: http://{host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
