#!/usr/bin/env python3
"""
Setup script to configure Gemini API for CrimeLens
"""

import os
import sys
from pathlib import Path

# Get the backend directory
backend_dir = Path(__file__).parent
env_file = backend_dir / ".env"

def setup_gemini():
    """Setup Gemini API configuration"""
    print("🔧 Setting up Gemini API for CrimeLens...")
    
    # Get API key from user
    api_key = input("Enter your Gemini API key (from https://makersuite.google.com/app/apikey): ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Read current .env file
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        print("❌ .env file not found. Please ensure backend/.env exists.")
        return
    
    # Update the configuration
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            updated_lines.append(f'GEMINI_API_KEY={api_key}')
        elif line.startswith('USE_GEMINI_API='):
            updated_lines.append('USE_GEMINI_API=true')
        else:
            updated_lines.append(line)
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Gemini API configured successfully!")
    print("\n📦 Installing required dependencies...")
    
    # Install dependencies
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai>=0.8.0"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return
    
    print("\n🚀 Setup complete! Gemini API is now enabled.")
    print("📝 The chatbot will now use Gemini API instead of Ollama.")
    print("\nTo switch back to Ollama, run: python switch_to_ollama.py")

def switch_to_ollama():
    """Switch back to Ollama"""
    print("🔄 Switching back to Ollama...")
    
    if not env_file.exists():
        print("❌ .env file not found.")
        return
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update the configuration
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('USE_GEMINI_API='):
            updated_lines.append('USE_GEMINI_API=false')
        else:
            updated_lines.append(line)
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Switched back to Ollama successfully!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--switch-to-ollama":
        switch_to_ollama()
    else:
        setup_gemini()
