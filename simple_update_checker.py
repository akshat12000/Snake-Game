"""
Simple Thread-Safe Update Checker for Snake Game
Provides console-based update checking without Tkinter threading issues
"""

import threading
import time
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class SimpleUpdateChecker:
    """Thread-safe update checker that uses console output"""
    
    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.update_server_url = "http://localhost:5000"
        self.last_check_time = 0
        self.check_interval = 300  # 5 minutes
        
    def load_current_version(self):
        """Load version from version.json if available"""
        try:
            with open('version.json', 'r') as f:
                version_data = json.load(f)
                return version_data.get('version', self.current_version)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.current_version
    
    def compare_versions(self, version1, version2):
        """Compare two version strings (returns True if version2 is newer)"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v2_parts[i] > v1_parts[i]:
                    return True
                elif v2_parts[i] < v1_parts[i]:
                    return False
            
            return False  # Versions are equal
            
        except ValueError:
            return False
    
    def check_for_updates_sync(self, force_check=False):
        """Synchronously check for updates"""
        if not REQUESTS_AVAILABLE:
            if force_check:
                print("❌ Update checking requires 'requests' library")
            return None
            
        current_time = time.time()
        
        # Rate limiting - don't check too frequently unless forced
        if not force_check and (current_time - self.last_check_time) < self.check_interval:
            return None
            
        self.last_check_time = current_time
        
        try:
            current_version = self.load_current_version()
            
            # Check server for updates
            response = requests.get(f"{self.update_server_url}/api/check-update", 
                                  params={'current_version': current_version},
                                  timeout=5)
            
            if response.status_code == 200:
                update_info = response.json()
                
                if update_info.get('update_available', False):
                    server_version = update_info.get('latest_version', 'Unknown')
                    print(f"\n🎉 UPDATE AVAILABLE!")
                    print(f"📋 Current version: {current_version}")
                    print(f"📋 Latest version: {server_version}")
                    print(f"📝 What's new: {update_info.get('changelog', 'Bug fixes and improvements')}")
                    print(f"🌐 Download from: {self.update_server_url}/api/download")
                    print("=" * 50)
                    return update_info
                else:
                    if force_check:
                        print(f"✅ You're running the latest version! (v{current_version})")
                    return None
            else:
                if force_check:
                    print(f"❌ Update server unavailable (HTTP {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            if force_check:
                print(f"❌ Failed to check for updates: {e}")
            return None
        except Exception as e:
            if force_check:
                print(f"❌ Update check error: {e}")
            return None
    
    def background_update_check(self):
        """Perform background update check (non-blocking)"""
        def check():
            try:
                time.sleep(3)  # Wait for game to start
                update_info = self.check_for_updates_sync(force_check=False)
                if update_info:
                    print(f"\n🔔 Background update check found new version!")
                    print("Press F5 during gameplay for more details.")
            except Exception as e:
                # Silently ignore background check errors
                pass
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def manual_update_check(self):
        """Perform manual update check (shows all results)"""
        def check():
            print("\n🔍 Checking for updates...")
            self.check_for_updates_sync(force_check=True)
            
        thread = threading.Thread(target=check, daemon=True)
        thread.start()