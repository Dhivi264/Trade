#!/usr/bin/env python3
"""
Setup script for Quotex Trading Predictor
Automates the initial setup process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Quotex Trading Predictor...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create .env file if it doesn't exist
    env_file = Path("quotex_predictor/.env")
    env_example = Path("quotex_predictor/.env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from template")
        print("⚠️  Please edit quotex_predictor/.env with your API keys")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Navigate to Django project directory
    os.chdir("quotex_predictor")
    
    # Run Django setup commands
    print("\n🗄️  Setting up database...")
    commands = [
        "python manage.py makemigrations",
        "python manage.py migrate",
        "python manage.py setup_trading_pairs"
    ]
    
    for command in commands:
        if not run_command(command):
            print(f"❌ Failed to run: {command}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit quotex_predictor/.env with your Alpha Vantage API key")
    print("2. Run: cd quotex_predictor && python manage.py runserver")
    print("3. Open http://localhost:8000 in your browser")
    print("\n💡 For production setup, see README.md")

if __name__ == "__main__":
    main()