#!/usr/bin/env python3
"""
Quick launcher for the Publisher GUI
"""

import os
import sys
import subprocess

def main():
    print("🐍 Snake Game Publisher Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('snake_game.py'):
        print("❌ Please run this from the Snake Game directory!")
        input("Press Enter to exit...")
        return 1
    
    # Find Python executable
    python_exe = None
    
    if os.path.exists('.venv/Scripts/python.exe'):
        python_exe = '.venv/Scripts/python.exe'
        print("✅ Using virtual environment")
    elif os.path.exists('.venv/bin/python'):
        python_exe = '.venv/bin/python'
        print("✅ Using virtual environment (Unix)")
    else:
        python_exe = sys.executable
        print("⚠️  Using system Python")
    
    # Launch the publisher
    try:
        print("🚀 Starting Publisher GUI...")
        subprocess.run([python_exe, 'publisher_gui.py'])
    except Exception as e:
        print(f"❌ Failed to start publisher: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())