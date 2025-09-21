#!/usr/bin/env python3
"""
Test the update system manually
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_system import UpdateChecker

def test_update_system():
    print("=== Testing Update System ===")
    
    checker = UpdateChecker()
    print(f"Server URL: {checker.SERVER_URL}")
    
    # Test current version reading
    print("\n--- Testing Version Reading ---")
    current_version = checker.get_current_version()
    print(f"Current version: {current_version}")
    
    # Test server connection
    print("\n--- Testing Server Connection ---")
    update_info = checker.check_for_updates()
    print(f"Update check result: {update_info}")
    
    if update_info.get('update_available'):
        print(f"Update available: {update_info.get('version')}")
        print(f"Changelog: {update_info.get('changelog', [])}")
    else:
        print("No update available")
    
    # Test the prompt (without actually updating)
    print("\n--- Testing Update Prompt ---")
    if update_info.get('update_available'):
        print("Would show update prompt dialog...")
    else:
        print("No update to prompt for")

if __name__ == "__main__":
    test_update_system()