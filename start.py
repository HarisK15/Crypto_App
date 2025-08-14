#!/usr/bin/env python3
"""
Crypto Alert Dashboard Startup Script

This script starts the app with proper error handling and setup checks.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

def check_requirements():
    """Makes sure all the required packages are installed."""
    try:
        import streamlit
        import pandas
        import requests
        import plotly
        import yaml
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Checks if the environment is set up properly."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating from template...")
        try:
            import shutil
            shutil.copy("env_template.txt", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env with your actual API keys")
        except FileNotFoundError:
            print("❌ env_template.txt not found")
            return False
    else:
        print("✅ .env file found")
    
    return True

def check_database():
    """Makes sure the database system is ready."""
    try:
        from database import db_manager
        print("✅ Database system ready")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_configuration():
    """Checks if the configuration can be loaded."""
    try:
        from config_loader import get_config
        app_name = get_config('app.name', 'Unknown')
        app_version = get_config('app.version', 'Unknown')
        print(f"✅ Configuration loaded: {app_name} v{app_version}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting Crypto Alert Dashboard...")
    print("=" * 50)
    
    # Run all the checks
    if not check_requirements():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    if not check_database():
        sys.exit(1)
    
    if not check_configuration():
        sys.exit(1)
    
    print("=" * 50)
    print("✅ All checks passed! Starting application...")
    print("🌐 The app will open in your browser at http://localhost:8501")
    print("📱 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Start Streamlit
        os.system("streamlit run app.py")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
