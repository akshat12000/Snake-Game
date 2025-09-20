"""
Version Management System for Snake Game
Handles version tracking, comparison, and update notifications
"""

import json
import os
from datetime import datetime

class VersionManager:
    def __init__(self, version_file="version.json"):
        self.version_file = version_file
        self.current_version = self.load_current_version()
    
    def load_current_version(self):
        """Load current version information"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            else:
                # Default version for first run
                default_version = {
                    "version": "1.0.0",
                    "build": "001",
                    "release_date": datetime.now().strftime("%Y-%m-%d"),
                    "features": [
                        "Classic Snake gameplay",
                        "Professional audio system",
                        "Persistent high scores",
                        "Progressive difficulty",
                        "Self-collision detection",
                        "Custom window icon",
                        "Auto-update system"
                    ]
                }
                self.save_version_info(default_version)
                return default_version
        except Exception as e:
            print(f"Error loading version: {e}")
            return {"version": "1.0.0", "build": "001", "release_date": "2024-01-01", "features": []}
    
    def save_version_info(self, version_info):
        """Save version information to file"""
        try:
            with open(self.version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
        except Exception as e:
            print(f"Error saving version: {e}")
    
    def get_current_version(self):
        """Get current version string"""
        return self.current_version.get("version", "1.0.0")
    
    def get_full_version_info(self):
        """Get complete version information"""
        return self.current_version
    
    def compare_versions(self, version1, version2):
        """Compare two version strings (returns -1, 0, or 1)"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_length = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_length - len(v1_parts)))
            v2_parts.extend([0] * (max_length - len(v2_parts)))
            
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            return 0
        except Exception as e:
            print(f"Error comparing versions: {e}")
            return 0
    
    def is_newer_version(self, remote_version):
        """Check if remote version is newer than current"""
        return self.compare_versions(self.get_current_version(), remote_version) < 0
    
    def update_version(self, new_version_info):
        """Update to new version"""
        self.current_version = new_version_info
        self.save_version_info(new_version_info)