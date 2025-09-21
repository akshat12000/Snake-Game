"""
Test script to debug update checking
"""
import sys
import os

# Add the current directory to Python path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from update_system import UpdateChecker

def test_update_checker():
    print("=== Update Checker Debug ===")
    
    checker = UpdateChecker()
    print(f"Server URL: {checker.SERVER_URL}")
    
    # Test version reading
    print("\n--- Testing Version Reading ---")
    current_version = checker.get_current_version()
    print(f"Current version: {current_version}")
    
    # Test server connection
    print("\n--- Testing Server Connection ---")
    try:
        update_info = checker.check_for_updates()
        print(f"Update check result: {update_info}")
    except Exception as e:
        print(f"Error during update check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_checker()