"""
Production Update Server for Snake Game
Designed for cloud hosting with proper security, logging, and configuration
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import hashlib

# Initialize Flask app
app = Flask(__name__)

# Handle proxy headers for cloud deployment
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Enable CORS for all routes
CORS(app)

# Configuration
class Config:
    # Environment-based configuration
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Server URLs for different environments
    BASE_URL = os.environ.get('BASE_URL', f'http://localhost:{PORT}')
    
    # File paths
    UPDATES_DIR = os.path.join(os.path.dirname(__file__), 'updates')
    VERSION_FILE = os.path.join(os.path.dirname(__file__), 'version.json')
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

app.config.from_object(Config)

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_version_info():
    """Load current version information from version.json"""
    try:
        if os.path.exists(Config.VERSION_FILE):
            with open(Config.VERSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default fallback version
            return {
                "version": "2.0.0",
                "build": "001",
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "changelog": [
                    {
                        "version": "2.0.0",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "changes": [
                            "Production server deployment",
                            "Cloud hosting support",
                            "Enhanced update system",
                            "Professional distribution pipeline"
                        ]
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error loading version info: {e}")
        return {"version": "1.0.0", "build": "001", "release_date": "2025-09-20"}

def get_file_info(filepath):
    """Get file size and checksum"""
    try:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            with open(filepath, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            return size, checksum
        return None, None
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return None, None

@app.route('/', methods=['GET'])
def home():
    """Server information endpoint"""
    version_info = load_version_info()
    return jsonify({
        'service': 'Snake Game Update Server',
        'status': 'online',
        'environment': Config.ENV,
        'current_version': version_info.get('version', '1.0.0'),
        'server_time': datetime.now().isoformat(),
        'endpoints': {
            'version_check': '/api/version',
            'download': '/api/download',
            'health': '/health'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'unknown'  # Could implement actual uptime tracking
    }), 200

@app.route('/api/version', methods=['GET'])
def check_version():
    """Check current version and update availability"""
    try:
        # Get client information
        client_version = request.args.get('version', '1.0.0')
        client_build = request.args.get('build', '001')
        platform = request.args.get('platform', 'windows')
        client_id = request.args.get('client_id', 'unknown')
        
        # Load current version info
        version_info = load_version_info()
        current_version = version_info.get('version', '2.0.0')
        current_build = version_info.get('build', '001')
        
        # Log the request
        logger.info(f"Version check: client v{client_version}.{client_build} | server v{current_version}.{current_build}")
        
        # Version comparison logic
        def compare_versions(v1, v2):
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            max_length = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_length - len(v1_parts)))
            v2_parts.extend([0] * (max_length - len(v2_parts)))
            
            for a, b in zip(v1_parts, v2_parts):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            return 0
        
        # Check if update is available
        update_available = (compare_versions(client_version, current_version) < 0 or 
                          (client_version == current_version and client_build < current_build))
        
        # Prepare response
        response = {
            'update_available': update_available,
            'client_version': client_version,
            'client_build': client_build,
            'server_version': current_version,
            'server_build': current_build,
            'server_time': datetime.now().isoformat(),
            'platform': platform
        }
        
        # Include update information if available
        if update_available:
            exe_path = os.path.join(Config.UPDATES_DIR, 'SnakeGame.exe')
            file_size, checksum = get_file_info(exe_path)
            
            response.update({
                'version': current_version,
                'build': current_build,
                'release_date': version_info.get('release_date'),
                'download_url': f"{Config.BASE_URL}/api/download",
                'filename': 'SnakeGame.exe',
                'file_size': file_size,
                'checksum': checksum,
                'changelog': version_info.get('changelog', [])
            })
            
            logger.info(f"Update available: {client_version} -> {current_version}")
        else:
            logger.info(f"Client up to date: v{client_version}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Version check error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/download', methods=['GET'])
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename=None):
    """Download the latest executable"""
    try:
        if not filename:
            filename = 'SnakeGame.exe'
        
        file_path = os.path.join(Config.UPDATES_DIR, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"Download requested for non-existent file: {filename}")
            return jsonify({
                'error': 'File not found',
                'filename': filename,
                'available_files': os.listdir(Config.UPDATES_DIR) if os.path.exists(Config.UPDATES_DIR) else []
            }), 404
        
        logger.info(f"Download started: {filename}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    try:
        stats = {
            'server_status': 'online',
            'version_info': load_version_info(),
            'environment': Config.ENV,
            'updates_directory': Config.UPDATES_DIR,
            'files_available': []
        }
        
        # List available files
        if os.path.exists(Config.UPDATES_DIR):
            for filename in os.listdir(Config.UPDATES_DIR):
                filepath = os.path.join(Config.UPDATES_DIR, filename)
                if os.path.isfile(filepath):
                    size, checksum = get_file_info(filepath)
                    stats['files_available'].append({
                        'filename': filename,
                        'size': size,
                        'checksum': checksum[:16] + '...' if checksum else None  # Truncate for display
                    })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Stats unavailable'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/health', 
            '/api/version',
            '/api/download',
            '/api/stats'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure updates directory exists
    os.makedirs(Config.UPDATES_DIR, exist_ok=True)
    
    logger.info(f"Starting Snake Game Update Server...")
    logger.info(f"Environment: {Config.ENV}")
    logger.info(f"Base URL: {Config.BASE_URL}")
    logger.info(f"Updates directory: {Config.UPDATES_DIR}")
    
    # Run the app
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )