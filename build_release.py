#!/usr/bin/env python3
"""
Professional Release Builder for Snake Game
Creates automated builds with version management and distribution packaging
"""

import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class ReleaseBuilder:
    """Automated build system for creating game releases"""
    
    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path(__file__).parent
        self.version_file = self.project_dir / "version.json"
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.releases_dir = self.project_dir / "releases"
        
        # Ensure directories exist
        for directory in [self.build_dir, self.dist_dir, self.releases_dir]:
            directory.mkdir(exist_ok=True)
    
    def load_version_info(self) -> Dict:
        """Load current version information"""
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Version file not found: {self.version_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in version file: {e}")
            return None
    
    def save_version_info(self, version_data: Dict) -> bool:
        """Save updated version information"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"ERROR: Failed to save version file: {e}")
            return False
    
    def increment_version(self, version_str: str, increment_type: str = 'patch') -> str:
        """Increment version number"""
        try:
            parts = [int(x) for x in version_str.split('.')]
            if len(parts) != 3:
                raise ValueError("Version must be in format x.y.z")
            
            major, minor, patch = parts
            
            if increment_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif increment_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            return f"{major}.{minor}.{patch}"
        except Exception as e:
            print(f"ERROR: Invalid version format '{version_str}': {e}")
            return None
    
    def bump_version(self, increment_type: str = 'patch', changelog_entry: str = None) -> bool:
        """Bump version and update changelog"""
        print(f"INFO: Bumping {increment_type} version...")
        
        version_data = self.load_version_info()
        if not version_data:
            return False
        
        old_version = version_data['version']
        new_version = self.increment_version(old_version, increment_type)
        
        if not new_version:
            return False
        
        # Update version info
        version_data['version'] = new_version
        
        # Handle build number properly (convert string to int, increment, format back)
        current_build = version_data.get('build', '001')
        if isinstance(current_build, str):
            try:
                build_num = int(current_build) + 1
            except ValueError:
                build_num = 1
        else:
            build_num = current_build + 1
        
        version_data['build'] = f"{build_num:03d}"  # Format as 3-digit string
        version_data['release_date'] = datetime.datetime.now().isoformat()
        
        # Add changelog entry
        if changelog_entry:
            if 'changelog' not in version_data:
                version_data['changelog'] = []
            
            changelog_item = {
                'version': new_version,
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'changes': [changelog_entry]
            }
            version_data['changelog'].insert(0, changelog_item)
        
        if self.save_version_info(version_data):
            print(f"SUCCESS: Version bumped: {old_version} -> {new_version} (Build {version_data['build']})")
            return True
        
        return False
    
    def clean_build_dirs(self) -> bool:
        """Clean previous build artifacts"""
        print("Cleaning build directories...")
        
        try:
            # Clean build and dist directories
            for directory in [self.build_dir, self.dist_dir]:
                if directory.exists():
                    shutil.rmtree(directory)
                directory.mkdir(exist_ok=True)
            
            print("Build directories cleaned")
            return True
        except Exception as e:
            print(f"Failed to clean build directories: {e}")
            return False
    
    def build_executable(self) -> bool:
        """Create executable using PyInstaller"""
        print("Building executable...")
        
        try:
            # Check if PyInstaller is available
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'pyinstaller'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Installing PyInstaller...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            
            # Build command
            build_cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name', 'SnakeGame',
                '--icon', 'snake_icon.ico',
                '--distpath', str(self.dist_dir),
                '--workpath', str(self.build_dir),
                '--clean',
                'snake_game.py'
            ]
            
            # Run PyInstaller
            result = subprocess.run(build_cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("SUCCESS: Executable built successfully")
                return True
            else:
                print(f"ERROR: Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"ERROR: Build error: {e}")
            return False
    
    def create_release_package(self) -> bool:
        """Package release with version info"""
        print("INFO: Creating release package...")
        
        version_data = self.load_version_info()
        if not version_data:
            return False
        
        version = version_data['version']
        release_name = f"SnakeGame_v{version}"
        release_dir = self.releases_dir / release_name
        
        try:
            # Create release directory
            if release_dir.exists():
                shutil.rmtree(release_dir)
            release_dir.mkdir()
            
            # Copy executable
            exe_source = self.dist_dir / "SnakeGame.exe"
            if exe_source.exists():
                shutil.copy2(exe_source, release_dir / "SnakeGame.exe")
            else:
                print("ERROR: Executable not found!")
                return False
            
            # Copy version info
            shutil.copy2(self.version_file, release_dir / "version.json")
            
            # Copy readme if exists
            readme_file = self.project_dir / "Readme.md"
            if readme_file.exists():
                shutil.copy2(readme_file, release_dir / "README.txt")
            
            # Create release info file
            release_info = {
                'version': version,
                'build': version_data.get('build', 1),
                'release_date': version_data.get('release_date'),
                'files': ['SnakeGame.exe', 'version.json', 'README.txt']
            }
            
            with open(release_dir / "release_info.json", 'w') as f:
                json.dump(release_info, f, indent=2)
            
            print(f"SUCCESS: Release package created: {release_name}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create release package: {e}")
            return False
    
    def upload_to_server(self, server_url: str = None) -> bool:
        """Upload release to update server (placeholder for actual upload)"""
        print("INFO: Preparing server upload...")
        
        if not server_url:
            print("INFO: No server URL provided - skipping upload")
            print("INFO: To enable uploads, provide server URL as parameter")
            return True
        
        # This is a placeholder for actual server upload functionality
        # In a real implementation, you would:
        # 1. Authenticate with the server
        # 2. Upload the executable file
        # 3. Update the server's version info
        # 4. Notify the server of the new release
        
        print("INFO: Server upload functionality not implemented yet")
        print(f"    Target server: {server_url}")
        print("    Files to upload:")
        
        version_data = self.load_version_info()
        version = version_data['version'] if version_data else "unknown"
        release_dir = self.releases_dir / f"SnakeGame_v{version}"
        
        if release_dir.exists():
            for file in release_dir.iterdir():
                print(f"      - {file.name}")
        
        return True
    
    def build_full_release(self, increment_type: str = 'patch', changelog_entry: str = None, server_url: str = None) -> bool:
        """Complete release build process"""
        print("Starting full release build...")
        print("=" * 50)
        
        # Step 1: Bump version
        if not self.bump_version(increment_type, changelog_entry):
            print("Release build failed at version bump")
            return False
        
        # Step 2: Clean build directories
        if not self.clean_build_dirs():
            print("Release build failed at cleanup")
            return False
        
        # Step 3: Build executable
        if not self.build_executable():
            print("Release build failed at executable creation")
            return False
        
        # Step 4: Create release package
        if not self.create_release_package():
            print("Release build failed at packaging")
            return False
        
        # Step 5: Upload to server (if configured)
        if not self.upload_to_server(server_url):
            print("Release build failed at server upload")
            return False
        
        print("=" * 50)
        print("Release build completed successfully!")
        
        version_data = self.load_version_info()
        if version_data:
            print(f"Version: {version_data['version']}")
            print(f"Build: {version_data.get('build', 'N/A')}")
            print(f"Date: {version_data.get('release_date', 'N/A')}")
        
        return True

def main():
    """Command line interface for release builder"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Snake Game Release Builder')
    parser.add_argument('--type', choices=['patch', 'minor', 'major'], default='patch',
                       help='Version increment type (default: patch)')
    parser.add_argument('--changelog', type=str, help='Changelog entry for this release')
    parser.add_argument('--server', type=str, help='Update server URL for upload')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')
    parser.add_argument('--build-only', action='store_true', help='Only build executable (no version bump)')
    
    args = parser.parse_args()
    
    builder = ReleaseBuilder()
    
    if args.clean_only:
        builder.clean_build_dirs()
        return
    
    if args.build_only:
        builder.clean_build_dirs()
        builder.build_executable()
        builder.create_release_package()
        return
    
    # Full release build
    success = builder.build_full_release(
        increment_type=args.type,
        changelog_entry=args.changelog,
        server_url=args.server
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()