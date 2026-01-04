# ============================================================================
# FILE 4: run.py
# LOCATION: run.py (Project Root)
# PURPOSE: Development server entry point
# ============================================================================

"""
Development Server Entry Point
Run this file to start the development server
"""

import os
from app import create_app
from app.config import get_config

# Create app
app = create_app()
config = get_config()

if __name__ == '__main__':
    print("\n" + "="*70)
    print(f"{config.APP_NAME} - Development Server")
    print("="*70)
    print(f"Version: {config.VERSION}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print("="*70 + "\n")
    
    # Run development server
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
