"""
Simple Update Server - Separate from game
Serves version info and game downloads
Run with: python update_server.py
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path

# Load environment variables from .env file if it exists
def load_env():
    env_vars = {}
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

# Load environment configuration
ENV = load_env()

# Server configuration with environment variables
SERVER_HOST = ENV.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(ENV.get('SERVER_PORT', os.environ.get('PORT', '8080')))
DOWNLOAD_CHUNK_SIZE = int(ENV.get('DOWNLOAD_CHUNK_SIZE', '1024'))
EXECUTABLE_PATH = ENV.get('EXECUTABLE_PATH', './SnakeGame.exe')
VERSION_FILE_PATH = ENV.get('VERSION_FILE_PATH', './version.json')

class UpdateHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_api_info()
        elif self.path == '/health':
            self.serve_health_check()
        elif self.path == '/version':
            self.serve_version_info()
        elif self.path == '/download':
            self.serve_download()
        else:
            self.send_error(404)
    
    def serve_api_info(self):
        """Serve API information at root path"""
        try:
            api_info = {
                "service": "Snake Game Update Server",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "version": "/version", 
                    "download": "/download"
                },
                "status": "active"
            }
            
            response = json.dumps(api_info, indent=2).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
            
        except Exception as e:
            print(f"Error serving API info: {e}")
            self.send_error(500)
    
    def serve_health_check(self):
        """Serve health check endpoint"""
        try:
            health_info = {
                "status": "healthy",
                "timestamp": "2025-09-21T15:48:00.000000",
                "uptime": "unknown"
            }
            
            response = json.dumps(health_info).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
            
        except Exception as e:
            print(f"Health check error: {e}")
            self.send_error(500)
    
    def serve_version_info(self):
        """Serve current version information"""
        try:
            # Load version from version.json file
            if os.path.exists(VERSION_FILE_PATH):
                with open(VERSION_FILE_PATH, 'r') as f:
                    version_data = json.load(f)
            else:
                # Fallback version if file doesn't exist
                version_data = {
                    "version": "1.0.0",
                    "release_date": "2025-09-21",
                    "changelog": [
                    "Added name, special scoring for name, 2nd time play fixes, pause functionality."
                ]
                }
            
            response = json.dumps(version_data).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
            
        except Exception as e:
            print(f"Error serving version info: {e}")
            self.send_error(500)
    
    def serve_download(self):
        """Serve game executable download"""
        try:
            # Use configured executable path
            exe_path = EXECUTABLE_PATH
            if not os.path.exists(exe_path):
                # Try alternative paths
                alternative_paths = [
                    './SnakeGame.exe',
                    './dist/SnakeGame.exe',
                    './snake_game.py'  # Fallback to Python script
                ]
                for path in alternative_paths:
                    if os.path.exists(path):
                        exe_path = path
                        break
                else:
                    self.send_error(404, "Game executable not found")
                    return
            
            # Get file size
            file_size = os.path.getsize(exe_path)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="SnakeGame.exe"')
            self.send_header('Content-Length', str(file_size))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Stream the file
            with open(exe_path, 'rb') as f:
                while True:
                    chunk = f.read(DOWNLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except ConnectionResetError:
                        print("Client disconnected during download")
                        break
                        
        except Exception as e:
            print(f"Error serving download: {e}")
            self.send_error(500)

def run_server(port=None):
    """Run the update server"""
    # Use configured port with Railway fallback
    if port is None:
        port = SERVER_PORT
    
    server_address = (SERVER_HOST, port)
    httpd = HTTPServer(server_address, UpdateHandler)
    
    print(f"Update Server running on http://{SERVER_HOST}:{port}")
    print(f"API Info: http://localhost:{port}/")
    print(f"Version endpoint: http://localhost:{port}/version")
    print(f"Download endpoint: http://localhost:{port}/download")
    print(f"Health endpoint: http://localhost:{port}/health")
    print("Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nUpdate server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()