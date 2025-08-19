#!/usr/bin/env python3
"""
Production configuration for Career AI Agent
Use this for deployment to cloud platforms
"""

import os
from app import app

if __name__ == '__main__':
    # Production settings
    port = int(os.environ.get('PORT', 5000))
    
    # For production, use 0.0.0.0 to bind to all interfaces
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Disable debug mode in production
    )
