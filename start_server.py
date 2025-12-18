#!/usr/bin/env python3
"""
Start Server Script
Starts the Django development server with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def start_server():
    """Start the Django development server"""
    print("🚀 Starting Quotex Predictor Server")
    print("=" * 40)
    
    # Change to the correct directory
    project_dir = Path(__file__).parent / 'quotex_predictor'
    
    print(f"📁 Project directory: {project_dir}")
    print("🔧 Running Django checks...")
    
    # Run Django checks first
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'check'
        ], cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Django checks passed")
        else:
            print(f"❌ Django checks failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running checks: {e}")
        return False
    
    print("\n🌐 Starting development server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
        ], cwd=project_dir)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server()