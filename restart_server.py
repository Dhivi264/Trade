#!/usr/bin/env python3
"""
Restart server script to apply prediction improvements
"""

import subprocess
import sys
import time
import os

def restart_server():
    print("🔄 Restarting Quotex Predictor Server...")
    print("=" * 40)
    
    # Change to project directory
    os.chdir("quotex_predictor")
    
    print("🚀 Starting server with improved predictions...")
    
    try:
        # Start the Django server
        subprocess.run([sys.executable, "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Try running manually:")
        print("   cd quotex_predictor")
        print("   python manage.py runserver")

if __name__ == "__main__":
    restart_server()