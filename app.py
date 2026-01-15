"""
WSGI Entry Point for Production
Used by production WSGI servers like Gunicorn
"""

import os
from app import create_app

# Set environment
os.environ.setdefault('FLASK_ENV', 'production')

# Create application
app = create_app('production')

if __name__ == '__main__':
    app.run()
