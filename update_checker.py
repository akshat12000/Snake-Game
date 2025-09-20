"""
Update Checker System for Snake Game
Handles checking for updates from remote server
"""

import requests
import json
import os
import uuid
from datetime import datetime, timedelta
from version_manager import VersionManager

class UpdateChecker:
    def __init__(self, update_server_url="http://localhost:5000/api"):
        self.server_url = update_server_url
        self.version_manager = VersionManager()
        self.last_check_file = "last_update_check.json"
    
    def should_check_for_updates(self, force_check=False):
        """Determine if we should check for updates (daily check by default)"""
        if force_check:
            return True
            
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r') as f:
                    last_check_data = json.load(f)
                    last_check = datetime.fromisoformat(last_check_data['last_check'])
                    return datetime.now() - last_check > timedelta(days=1)
            return True
        except Exception as e:
            print(f"Error checking update schedule: {e}")
            return True
    
    def record_update_check(self):
        """Record that we checked for updates"""
        try:
            check_data = {
                'last_check': datetime.now().isoformat(),
                'status': 'completed'
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(check_data, f)
        except Exception as e:
            print(f"Error recording update check: {e}")
    
    def check_for_updates(self, timeout=10):
        """Check remote server for updates"""
        try:
            # Prepare request data
            current_version_info = self.version_manager.get_full_version_info()
            request_data = {
                'current_version': current_version_info.get('version'),
                'current_build': current_version_info.get('build'),
                'platform': 'windows',  # Can be made dynamic
                'client_id': self.get_client_id()
            }
            
            # Make request to update server
            response = requests.get(
                f"{self.server_url}/check-update",
                params=request_data,
                timeout=timeout,
                headers={'User-Agent': 'SnakeGame-UpdateChecker/1.0'}
            )
            
            if response.status_code == 200:
                update_info = response.json()
                self.record_update_check()
                return update_info
            else:
                print(f"Update server returned status: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Update check timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("Could not connect to update server")
            return None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
    
    def get_client_id(self):
        """Generate or retrieve unique client ID"""
        client_file = "client_id.json"
        try:
            if os.path.exists(client_file):
                with open(client_file, 'r') as f:
                    return json.load(f)['client_id']
            else:
                client_id = str(uuid.uuid4())
                with open(client_file, 'w') as f:
                    json.dump({'client_id': client_id, 'created': datetime.now().isoformat()}, f)
                return client_id
        except Exception as e:
            print(f"Error managing client ID: {e}")
            return "unknown"
    
    def download_update(self, update_info, progress_callback=None):
        """Download update package from server"""
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                return False, "No download URL provided"
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            filename = update_info.get('filename', 'SnakeGame_Update.exe')
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return True, filename
            
        except Exception as e:
            return False, f"Download failed: {e}"
    
    def is_update_available(self):
        """Simple check if update is available"""
        if not self.should_check_for_updates():
            return False, None
            
        update_info = self.check_for_updates()
        if not update_info:
            return False, None
        
        if update_info.get('update_available', False):
            remote_version = update_info.get('latest_version')
            if self.version_manager.is_newer_version(remote_version):
                return True, update_info
        
        return False, None