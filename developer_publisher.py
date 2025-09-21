"""
Developer Publishing System - One-Click Release
Handles version bumping, building, and deployment
"""
import json
import os
import subprocess
import sys
from datetime import datetime
import shutil

class DeveloperPublisher:
    def __init__(self):
        self.version_file = "version.json"
        self.server_version_file = "update_server.py"
        
    def load_current_version(self):
        """Load current version from version.json"""
        try:
            with open(self.version_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": "1.0.0",
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "changelog": []
            }
    
    def increment_version(self, version_type="patch"):
        """Increment version number (patch, minor, major)"""
        version_data = self.load_current_version()
        current = version_data["version"]
        
        major, minor, patch = map(int, current.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
            
        new_version = f"{major}.{minor}.{patch}"
        return new_version
    
    def update_version_file(self, new_version, changelog_message):
        """Update version.json with new version and changelog"""
        version_data = self.load_current_version()
        version_data["version"] = new_version
        version_data["release_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Add new changelog entry
        new_entry = {
            "version": new_version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "changes": [changelog_message]
        }
        
        if "changelog" not in version_data:
            version_data["changelog"] = []
        
        version_data["changelog"].insert(0, new_entry)  # Add to beginning
        
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        print(f"Updated version.json to {new_version}")
        return version_data
    
    def update_server_version(self, new_version, changelog):
        """Update the server's version info"""
        try:
            with open(self.server_version_file, 'r') as f:
                server_content = f.read()
            
            # Update the version in server code
            new_server_content = server_content.replace(
                '"version": "1.1.0"',
                f'"version": "{new_version}"'
            )
            
            # Update changelog in server
            changelog_items = changelog.get("changelog", [{}])
            if changelog_items:
                latest_changes = changelog_items[0].get("changes", [])
                changelog_str = '",\n                    "'.join(latest_changes)
                
                # Find and replace the changelog section
                import re
                pattern = r'("changelog": \[)(.*?)(\])'
                replacement = f'\\1\n                    "{changelog_str}"\n                \\3'
                new_server_content = re.sub(pattern, replacement, new_server_content, flags=re.DOTALL)
            
            with open(self.server_version_file, 'w') as f:
                f.write(new_server_content)
            
            print(f"Updated server version to {new_version}")
        except Exception as e:
            print(f"Warning: Could not update server version: {e}")
    
    def build_executable(self):
        """Build the executable with PyInstaller"""
        print("Building executable...")
        
        try:
            # Clean previous builds
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            
            # Build using spec file (which includes version.json)
            result = subprocess.run([
                "pyinstaller", 
                "snake_game.spec", 
                "--clean", 
                "--noconfirm"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Copy to root for server
                if os.path.exists("dist/snake_game.exe"):
                    shutil.copy2("dist/snake_game.exe", "SnakeGame.exe")
                    print("Executable built successfully")
                    return True
                else:
                    print("Executable not found in dist/")
                    return False
            else:
                print(f"Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Build error: {e}")
            return False
    
    def create_release_package(self, version):
        """Create a release package"""
        release_dir = f"releases/v{version}"
        os.makedirs(release_dir, exist_ok=True)
        
        # Copy files to release directory
        files_to_copy = [
            "SnakeGame.exe",
            "version.json",
            "README_UPDATE.md"
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, release_dir)
        
        print(f"Release package created in {release_dir}")
        return release_dir
    
    def publish_release(self, version_type="patch", changelog_message="Bug fixes and improvements"):
        """Complete publishing workflow"""
        print("Starting release publishing...")
        print(f"Version type: {version_type}")
        print(f"Changelog: {changelog_message}")
        print("-" * 50)
        
        # Step 1: Increment version
        new_version = self.increment_version(version_type)
        print(f"New version: {new_version}")
        
        # Step 2: Update version.json
        version_data = self.update_version_file(new_version, changelog_message)
        
        # Step 3: Update server version
        self.update_server_version(new_version, version_data)
        
        # Step 4: Build executable
        if not self.build_executable():
            print("Publishing failed - could not build executable")
            return False
        
        # Step 5: Create release package
        release_dir = self.create_release_package(new_version)
        
        print("-" * 50)
        print(f"Successfully published version {new_version}!")
        print(f"Release available in: {release_dir}")
        print(f"Update server now serves version {new_version}")
        print("\nNext steps:")
        print("1. Test the update system with the new version")
        print("2. Deploy server updates to Railway")
        print("3. Distribute SnakeGame.exe to users")
        
        return True

def main():
    """Command line interface for publishing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="One-Click Game Publisher")
    parser.add_argument("--type", choices=["patch", "minor", "major"], 
                       default="patch", help="Version increment type")
    parser.add_argument("--message", required=True, 
                       help="Changelog message for this release")
    
    args = parser.parse_args()
    
    publisher = DeveloperPublisher()
    success = publisher.publish_release(args.type, args.message)
    
    if success:
        print("\nPublishing complete!")
        sys.exit(0)
    else:
        print("\nPublishing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()