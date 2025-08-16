#!/usr/bin/env python3
"""
Setup API Keys for Government Gazette Structure Analyzer

This script helps you set up your API keys properly.
"""

import os
from pathlib import Path

def main():
    print("🔑 API Key Setup for Government Gazette Structure Analyzer")
    print("=" * 60)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    env_file = current_dir / ".env"
    
    print("\n📝 Setting up API keys...")
    
    # Get API keys from user
    landing_ai_key = input("Enter your Landing AI API key: ").strip()
    openai_key = input("Enter your OpenAI API key: ").strip()
    
    # Validate keys
    if not landing_ai_key:
        print("❌ Landing AI API key is required!")
        return 1
    
    if not openai_key:
        print("⚠️ Warning: OpenAI API key is not provided. Intelligent analysis will be limited.")
    
    # Create .env file content
    env_content = f"""# Landing AI Government Gazette Analyzer Environment Variables

# Landing AI API Key
# Get your API key from: https://landing.ai/
VISION_AGENT_API_KEY={landing_ai_key}

# OpenAI API Key (for intelligent analysis)
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY={openai_key}

# Optional: Custom output directory
# OUTPUT_DIR=./output

# Optional: Custom upload directory (for web interface)
# UPLOAD_DIR=./uploads
"""
    
    try:
        # Write .env file
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ API keys saved to {env_file}")
        
        # Test the keys
        print("\n🧪 Testing API keys...")
        
        # Test environment variable loading
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        landing_ai_test = os.getenv("VISION_AGENT_API_KEY")
        openai_test = os.getenv("OPENAI_API_KEY")
        
        if landing_ai_test and landing_ai_test == landing_ai_key:
            print("✅ Landing AI API key loaded successfully")
        else:
            print("❌ Landing AI API key not loaded correctly")
        
        if openai_test and openai_test == openai_key:
            print("✅ OpenAI API key loaded successfully")
        else:
            print("❌ OpenAI API key not loaded correctly")
        
        print("\n🎉 Setup completed!")
        print("\n📋 Next steps:")
        print("1. Run the example: python example_usage.py")
        print("2. Or start the web interface: python web_interface.py")
        print("3. Or use command line: python gazette_structure_analyzer.py <base.pdf> <amendment.pdf>")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error saving API keys: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

