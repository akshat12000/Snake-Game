"""Test that the executable can read its embedded version.json"""
import sys
import os

# Add the current directory to the path so we can import update_system
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_system import UpdateChecker

def test_version_reading():
    checker = UpdateChecker()
    version = checker.get_current_version()
    print(f"Current version detected: {version}")
    
    # Also test the version reading logic manually
    print("\nTesting version file locations:")
    
    # Check possible paths
    possible_paths = [
        "version.json",
        os.path.join(os.path.dirname(sys.executable), "version.json"),
    ]
    
    if hasattr(sys, '_MEIPASS'):
        possible_paths.append(os.path.join(sys._MEIPASS, "version.json"))
        print(f"PyInstaller detected, _MEIPASS: {sys._MEIPASS}")
    else:
        print("Not running from PyInstaller executable")
    
    for path in possible_paths:
        exists = os.path.exists(path)
        print(f"  {path}: {'EXISTS' if exists else 'NOT FOUND'}")

if __name__ == "__main__":
    test_version_reading()