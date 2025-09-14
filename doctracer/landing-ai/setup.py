#!/usr/bin/env python3
"""
Setup script for Government Gazette Structure Analyzer

This script helps users set up the environment and dependencies
for the Landing AI-based gazette analyzer.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    api_key = input("Enter your Landing AI API key (or press Enter to skip): ").strip()
    openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    env_content = f"""# Landing AI Government Gazette Analyzer Environment Variables

# Landing AI API Key
# Get your API key from: https://landing.ai/
VISION_AGENT_API_KEY={api_key}

# OpenAI API Key (for intelligent analysis)
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY={openai_key}

# Optional: Custom output directory
# OUTPUT_DIR=./output

# Optional: Custom upload directory (for web interface)
# UPLOAD_DIR=./uploads
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "output",
        "uploads",
        "data"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        # Test imports
        import dotenv
        print("✅ python-dotenv imported successfully")
        
        # Test if we can import agentic_doc (if API key is set)
        try:
            from agentic_doc.parse import parse
            print("✅ agentic-doc imported successfully")
        except ImportError:
            print("⚠️ agentic-doc not available (may need API key)")
        
        # Test OpenAI
        try:
            import openai
            print("✅ OpenAI imported successfully")
        except ImportError:
            print("⚠️ OpenAI not available")
        
        # Test Flask
        try:
            import flask
            print("✅ Flask imported successfully")
        except ImportError:
            print("❌ Flask import failed")
            return False
        
        print("✅ Setup test completed")
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Government Gazette Structure Analyzer Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Create directories
    create_directories()
    
    # Test setup
    if not test_setup():
        return 1
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your Landing AI API key")
    print("2. Place your gazette PDF files in the data/ directory")
    print("3. Run the example: python example_usage.py")
    print("4. Or start the web interface: python web_interface.py")
    print("\n📚 For more information, see README.md")
    
    return 0

if __name__ == "__main__":
    exit(main())
