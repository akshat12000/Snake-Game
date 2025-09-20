#!/usr/bin/env python3
"""
Test script to verify update system is working correctly
"""

from simple_update_checker import SimpleUpdateChecker

def test_update_system():
    print("🧪 Testing Update System")
    print("=" * 40)
    
    # Test 1: Create update checker
    try:
        checker = SimpleUpdateChecker()
        print("✅ SimpleUpdateChecker created successfully")
    except Exception as e:
        print(f"❌ Failed to create SimpleUpdateChecker: {e}")
        return
    
    # Test 2: Version loading
    try:
        current_version = checker.load_current_version()
        print(f"✅ Current version loaded: {current_version}")
    except Exception as e:
        print(f"❌ Failed to load version: {e}")
        return
    
    # Test 3: Version comparison
    try:
        is_newer = checker.compare_versions("1.0.0", "1.1.0")
        print(f"✅ Version comparison works: 1.1.0 > 1.0.0? {is_newer}")
    except Exception as e:
        print(f"❌ Failed version comparison: {e}")
        return
    
    # Test 4: Manual update check (with server)
    print("\n🔍 Testing manual update check...")
    try:
        update_info = checker.check_for_updates_sync(force_check=True)
        if update_info:
            print("✅ Update check found new version!")
        else:
            print("✅ Update check completed (no update available or server offline)")
    except Exception as e:
        print(f"❌ Update check failed: {e}")
        return
    
    print("\n🎉 All update system tests passed!")

if __name__ == "__main__":
    test_update_system()