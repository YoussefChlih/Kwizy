"""
Vercel/WSGI entry point for production deployments
"""
import os
import sys

# Ensure uploads directory exists in /tmp
os.makedirs('/tmp/uploads', exist_ok=True)
os.environ['UPLOAD_FOLDER'] = '/tmp/uploads'
os.environ['FLASK_ENV'] = 'production'

from app import app, socketio

# WSGI application entry point for production servers
if __name__ == '__main__':
    # For Vercel deployment
    app.run()
