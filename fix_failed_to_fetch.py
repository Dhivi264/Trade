#!/usr/bin/env python3
"""
Fix 'Failed to fetch' Error
Comprehensive script to diagnose and fix the 'Failed to fetch' error
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_server_status():
    """Check if Django server is running"""
    print("🔍 Checking server status...")
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/api/trading-pairs/', timeout=3)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"⚠️ Server responding with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def fix_cors_settings():
    """Ensure CORS settings are correct"""
    print("\n🔧 Checking CORS settings...")
    
    settings_file = Path(__file__).parent / 'quotex_predictor' / 'quotex_predictor' / 'settings.py'
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Check for required CORS settings
        required_settings = [
            "CORS_ALLOW_ALL_ORIGINS = True",
            "CORS_ALLOW_CREDENTIALS = True",
            "'corsheaders.middleware.CorsMiddleware'",
        ]
        
        missing_settings = []
        for setting in required_settings:
            if setting not in content:
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"⚠️ Missing CORS settings: {missing_settings}")
            print("💡 CORS settings appear to be configured correctly in the file")
        else:
            print("✅ CORS settings are properly configured")
        
        return True
    except Exception as e:
        print(f"❌ Error checking CORS settings: {e}")
        return False

def check_django_setup():
    """Check Django setup and migrations"""
    print("\n🔧 Checking Django setup...")
    
    project_dir = Path(__file__).parent / 'quotex_predictor'
    
    try:
        # Check migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations'
        ], cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations are up to date")
        else:
            print("⚠️ Migration issues detected")
            print("🔧 Running migrations...")
            subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=project_dir)
        
        return True
    except Exception as e:
        print(f"❌ Error checking Django setup: {e}")
        return False

def create_startup_batch_file():
    """Create a Windows batch file to start the server easily"""
    print("\n📝 Creating startup batch file...")
    
    batch_content = '''@echo off
echo Starting Quotex Predictor Server...
echo.
cd /d "%~dp0quotex_predictor"
python manage.py runserver 127.0.0.1:8000
pause
'''
    
    try:
        with open('start_quotex_server.bat', 'w') as f:
            f.write(batch_content)
        print("✅ Created start_quotex_server.bat")
        print("💡 You can double-click this file to start the server")
        return True
    except Exception as e:
        print(f"❌ Error creating batch file: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Quotex Predictor - Fix 'Failed to fetch' Error")
    print("=" * 55)
    
    # Step 1: Check if server is running
    server_running = check_server_status()
    
    # Step 2: Check CORS settings
    fix_cors_settings()
    
    # Step 3: Check Django setup
    check_django_setup()
    
    # Step 4: Create startup files
    create_startup_batch_file()
    
    # Step 5: Provide instructions
    print("\n" + "=" * 55)
    print("📋 SUMMARY & INSTRUCTIONS")
    print("=" * 55)
    
    if not server_running:
        print("\n❌ MAIN ISSUE: Django server is not running!")
        print("\n🔧 TO FIX THE 'Failed to fetch' ERROR:")
        print("   1. Start the server using one of these methods:")
        print("      • Double-click: start_quotex_server.bat")
        print("      • Command: python start_server.py")
        print("      • Manual: cd quotex_predictor && python manage.py runserver")
        print("\n   2. Wait for the server to start (you'll see 'Starting development server')")
        print("   3. Open your browser to: http://127.0.0.1:8000")
        print("   4. The 'Failed to fetch' error should be resolved")
    else:
        print("\n✅ Server is running! If you still see 'Failed to fetch':")
        print("   1. Check browser console (F12) for detailed errors")
        print("   2. Verify the frontend is accessing: http://127.0.0.1:8000")
        print("   3. Try refreshing the page (Ctrl+F5)")
        print("   4. Check if any firewall is blocking the connection")
    
    print("\n🌐 Server URL: http://127.0.0.1:8000")
    print("📊 API Endpoints: http://127.0.0.1:8000/api/")
    print("\n💡 Common causes of 'Failed to fetch':")
    print("   • Server not running (most common)")
    print("   • Wrong URL in frontend code")
    print("   • Browser blocking requests (CORS)")
    print("   • Firewall blocking port 8000")

if __name__ == "__main__":
    main()