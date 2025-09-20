"""
Simple Update Server for Snake Game
This would typically run on a cloud server (AWS, Heroku, etc.)
Run with: python update_server.py
"""

from flask import Flask, request, jsonify, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

# This would typically be in a database
LATEST_VERSION_INFO = {
    "version": "1.0.1",
    "build": "002", 
    "release_date": "2025-09-20",
    "features": [
        "Classic Snake gameplay with smooth controls",
        "Professional stereo audio system", 
        "Persistent high score tracking",
        "Progressive difficulty scaling",
        "Thread-safe auto-update system",
        "Custom window icon and branding",
        "Self-collision detection"
    ],
    "changes": [
        "Fixed threading issues in update system",
        "Improved update notification system", 
        "Enhanced console-based update checking",
        "Better error handling and reliability",
        "Professional update pipeline integration"
    ],
    "download_url": "http://localhost:5000/api/download/SnakeGame.exe",
    "filename": "SnakeGame_v1.1.0.exe",
    "file_size": 25600000,  # 25MB example
    "checksum": "sha256:abc123def456",
    "min_version": "1.0.0"  # Minimum version that can auto-update
}

@app.route('/api/check-update', methods=['GET'])
def check_update():
    """Check if updates are available"""
    try:
        current_version = request.args.get('current_version', '1.0.0')
        current_build = request.args.get('current_build', '001')
        platform = request.args.get('platform', 'windows')
        client_id = request.args.get('client_id', 'unknown')
        
        # Enhanced logging
        print(f"📊 Update check: v{current_version} build {current_build} from client {client_id}")
        
        # Compare versions
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
        
        latest_version = LATEST_VERSION_INFO['version']
        update_available = compare_versions(current_version, latest_version) < 0
        
        if update_available:
            print(f"🚀 Update available: {current_version} → {latest_version}")
        else:
            print(f"✅ Client up to date: v{current_version}")
        
        response = {
            'update_available': update_available,
            'current_version': current_version,
            'latest_version': latest_version,
            'server_time': datetime.now().isoformat()
        }
        
        if update_available:
            response.update(LATEST_VERSION_INFO)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
@app.route('/api/download/<filename>', methods=['GET'])
def download_update(filename=None):
    """Serve update files"""
    try:
        if not filename:
            # If no filename provided, suggest the latest version
            return jsonify({
                'error': 'No filename specified',
                'suggestion': 'Try /api/download/SnakeGame.exe',
                'latest_version': LATEST_VERSION_INFO['version'],
                'available_files': ['SnakeGame.exe', 'version.json', 'README.txt']
            }), 400
            
        # In production, this would serve from cloud storage
        file_path = f"updates/{filename}"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            # For demo purposes, create a dummy file or provide helpful response
            if filename == 'SnakeGame.exe':
                return jsonify({
                    'message': 'Demo server - executable not available for download',
                    'instructions': [
                        'To set up real downloads:',
                        '1. Run: python build_release.py --type patch',
                        '2. Copy files from releases/ to updates/',
                        '3. Restart server'
                    ]
                }), 404
            else:
                return jsonify({'error': f'File {filename} not found'}), 404
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/version-info', methods=['GET'])
def get_version_info():
    """Get detailed version information"""
    return jsonify(LATEST_VERSION_INFO)

@app.route('/api/stats', methods=['POST'])
def record_stats():
    """Record game statistics (optional)"""
    try:
        stats_data = request.get_json()
        # In production, save to database
        print(f"Stats received: {stats_data}")
        return jsonify({'status': 'recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Simple index page"""
    return """
    <h1>🐍 Snake Game Update Server</h1>
    <p>Server is running!</p>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><a href="/api/check-update">/api/check-update</a> - Check for updates</li>
        <li><a href="/api/version-info">/api/version-info</a> - Get version info</li>
        <li><a href="/api/download">/api/download</a> - Download updates</li>
        <li>/api/stats - Record statistics (POST)</li>
    </ul>
    <h2>Current Version Available:</h2>
    <p>Version: """ + LATEST_VERSION_INFO['version'] + """</p>
    <p>Build: """ + LATEST_VERSION_INFO['build'] + """</p>
    <p>Release Date: """ + LATEST_VERSION_INFO['release_date'] + """</p>
    """

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to avoid 404s"""
    return '', 204  # No content

if __name__ == '__main__':
    # Create updates directory
    os.makedirs('updates', exist_ok=True)
    
    print("🚀 Snake Game Update Server")
    print("📍 Server will run at: http://localhost:5000")
    print("🔍 Check updates at: http://localhost:5000/api/check-update")
    print("📊 Version info at: http://localhost:5000/api/version-info")
    print("\n💡 To test updates:")
    print("1. Run this server: python update_server.py")
    print("2. Run your game: python snake_game.py")
    print("3. Press F5 in game to check for updates")
    print("\n⚠️  Note: This is a demo server. In production, deploy to cloud platforms.")
    
    app.run(host='0.0.0.0', port=5000, debug=True)