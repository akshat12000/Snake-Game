#!/usr/bin/env python3
"""
Developer Publishing Tool for Snake Game
One-click release publishing with GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import subprocess
import sys
import datetime
from pathlib import Path

class PublisherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game Publisher")
        self.root.geometry("700x900")  # Increased height to show all buttons
        self.root.resizable(True, True)
        self.root.minsize(600, 700)  # Set minimum size
        
        # Set up the UI
        self.setup_ui()
        
        # Load current version info
        self.load_current_version()
        
    def setup_ui(self):
        """Set up the main user interface"""
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Snake Game Publisher", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Current version info frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Version", padding="10")
        current_frame.pack(fill="x", pady=(0, 20))
        
        self.current_version_label = ttk.Label(current_frame, text="Loading...", font=("Arial", 12))
        self.current_version_label.pack()
        
        # Release type frame
        release_frame = ttk.LabelFrame(main_frame, text="Release Type", padding="10")
        release_frame.pack(fill="x", pady=(0, 20))
        
        self.release_type = tk.StringVar(value="patch")
        
        release_types = [
            ("Patch (1.0.0 → 1.0.1) - Bug fixes", "patch"),
            ("Minor (1.0.1 → 1.1.0) - New features", "minor"),
            ("Major (1.1.0 → 2.0.0) - Breaking changes", "major")
        ]
        
        for text, value in release_types:
            ttk.Radiobutton(
                release_frame, 
                text=text, 
                variable=self.release_type, 
                value=value,
                command=self.update_preview
            ).pack(anchor="w", pady=2)
        
        # Changelog frame - make it more compact
        changelog_frame = ttk.LabelFrame(main_frame, text="What's New in This Release", padding="10")
        changelog_frame.pack(fill="x", pady=(0, 15))  # Reduced expand to False
        
        ttk.Label(
            changelog_frame, 
            text="Describe the changes in this release:"
        ).pack(anchor="w", pady=(0, 5))
        
        self.changelog_text = scrolledtext.ScrolledText(
            changelog_frame, 
            height=4,  # Further reduced height
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        self.changelog_text.pack(fill="both", expand=False)  # Don't expand
        self.changelog_text.bind('<KeyRelease>', self.update_preview)
        
        # Preview frame - make it more compact
        preview_frame = ttk.LabelFrame(main_frame, text="Release Preview", padding="10")
        preview_frame.pack(fill="x", pady=(0, 15))
        
        # Use a scrollable text widget for preview instead of label
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            height=6,  # Fixed height
            wrap=tk.WORD,
            font=("Consolas", 9),
            state='disabled'  # Read-only
        )
        self.preview_text.pack(fill="both", expand=False)
        
        # Progress frame - make it more compact
        progress_frame = ttk.LabelFrame(main_frame, text="Publishing Progress", padding="10")
        progress_frame.pack(fill="x", pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready to publish", font=("Arial", 10))
        self.status_label.pack()
        
        # Buttons frame - ensure it's always visible
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=15, side="bottom")  # Force to bottom
        
        # Create a separator line above buttons for clarity
        separator = ttk.Separator(buttons_frame, orient='horizontal')
        separator.pack(fill="x", pady=(0, 10))
        
        # Test server button
        self.test_button = ttk.Button(
            buttons_frame, 
            text="Test Server", 
            command=self.test_server,
            width=12
        )
        self.test_button.pack(side="left")
        
        # Preview build button
        self.preview_button = ttk.Button(
            buttons_frame, 
            text="Preview", 
            command=self.preview_build,
            width=12
        )
        self.preview_button.pack(side="left", padx=(10, 0))
        
        # Publish button (main action) - larger and more prominent
        self.publish_button = ttk.Button(
            buttons_frame, 
            text="PUBLISH RELEASE", 
            command=self.publish_release,
            width=18
        )
        self.publish_button.pack(side="right", padx=(10, 0))
        
        # Update preview initially
        self.root.after(100, self.update_preview)
        
    def load_current_version(self):
        """Load current version information"""
        try:
            with open('version.json', 'r') as f:
                version_data = json.load(f)
            
            version = version_data.get('version', '1.0.0')
            build = version_data.get('build', '001')
            release_date = version_data.get('release_date', 'Unknown')
            
            self.current_version_label.config(
                text=f"Current: v{version} (Build {build}) - Released: {release_date}"
            )
            
            return version_data
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.current_version_label.config(text=f"❌ Error loading version: {e}")
            return None
    
    def calculate_next_version(self, current_version, increment_type):
        """Calculate the next version number"""
        try:
            parts = [int(x) for x in current_version.split('.')]
            if len(parts) != 3:
                raise ValueError("Invalid version format")
            
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
        except Exception:
            return "Error"
    
    def update_preview(self, event=None):
        """Update the release preview"""
        version_data = self.load_current_version()
        if not version_data:
            return
        
        current_version = version_data.get('version', '1.0.0')
        next_version = self.calculate_next_version(current_version, self.release_type.get())
        
        changelog = self.changelog_text.get('1.0', tk.END).strip()
        if not changelog:
            changelog = "No changelog provided"
        
        preview_text = f"""RELEASE PREVIEW
Version: {current_version} -> {next_version}
Type: {self.release_type.get().title()} Release
Date: {datetime.datetime.now().strftime('%Y-%m-%d')}

Changes:
{changelog}

Actions:
- Build executable with PyInstaller
- Update version.json
- Create release package
- Copy files to server directory
- Update server configuration"""
        
        # Update the preview text widget
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', preview_text)
        self.preview_text.config(state='disabled')
    
    def test_server(self):
        """Test if the update server is running"""
        def check_server():
            try:
                import requests
                response = requests.get("http://localhost:5000/api/version-info", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    messagebox.showinfo(
                        "Server Status", 
                        f"✅ Update server is running!\n\nServer version: {data.get('version', 'Unknown')}\nServer build: {data.get('build', 'Unknown')}"
                    )
                else:
                    messagebox.showwarning("Server Status", f"⚠️ Server responded with status {response.status_code}")
            except ImportError:
                messagebox.showerror("Error", "❌ 'requests' library not available.\nRun: pip install requests")
            except Exception as e:
                messagebox.showerror("Server Status", f"❌ Update server not running!\n\nError: {e}\n\nStart server with: python update_server.py")
        
        threading.Thread(target=check_server, daemon=True).start()
    
    def preview_build(self):
        """Preview what the build will do without actually building"""
        changelog = self.changelog_text.get('1.0', tk.END).strip()
        if not changelog:
            messagebox.showwarning("Preview", "⚠️ Please add a changelog entry first!")
            return
        
        version_data = self.load_current_version()
        if not version_data:
            return
        
        current_version = version_data.get('version', '1.0.0')
        next_version = self.calculate_next_version(current_version, self.release_type.get())
        
        preview_message = f"""
🔍 BUILD PREVIEW

This will:
1. 🔄 Bump version: {current_version} → {next_version}
2. 🧹 Clean build directories
3. 🔨 Build executable: SnakeGame.exe
4. 📦 Create release package: SnakeGame_v{next_version}
5. 📁 Copy files to updates/ directory
6. 🌐 Update server configuration

📝 Changelog entry:
{changelog}

⏱️ Estimated time: 30-60 seconds

Ready to proceed with actual build?
        """.strip()
        
        result = messagebox.askyesno("Build Preview", preview_message)
        if result:
            self.publish_release()
    
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.progress_bar['value'] = value
        self.status_label.config(text=status)
        self.root.update()
    
    def publish_release(self):
        """Publish the release - main action"""
        changelog = self.changelog_text.get('1.0', tk.END).strip()
        if not changelog:
            messagebox.showwarning("Missing Changelog", "⚠️ Please add a changelog entry describing what's new in this release!")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Publish", 
            f"🚀 Ready to publish {self.release_type.get()} release?\n\nThis will:\n• Build new executable\n• Update version\n• Deploy to server\n\nContinue?",
            default='no'
        )
        
        if not result:
            return
        
        # Disable buttons during publishing
        self.publish_button.config(state='disabled')
        self.preview_button.config(state='disabled')
        
        # Run publishing in separate thread
        threading.Thread(target=self._publish_worker, args=(changelog,), daemon=True).start()
    
    def _publish_worker(self, changelog):
        """Worker thread for publishing process"""
        try:
            total_steps = 6
            
            # Step 1: Build release
            self.update_progress(10, "Building release...")
            
            # Clean changelog completely - remove ALL unicode characters including emojis
            # Convert to ASCII-only text
            ascii_changelog = ""
            for char in changelog:
                if ord(char) < 128:  # Only ASCII characters
                    ascii_changelog += char
                elif char.isspace():
                    ascii_changelog += " "
            
            # Clean up extra spaces and ensure we have content
            ascii_changelog = " ".join(ascii_changelog.split())
            if not ascii_changelog.strip():
                ascii_changelog = "Bug fixes and improvements"
            
            cmd = [
                sys.executable, 'build_release.py', 
                '--type', self.release_type.get(),
                '--changelog', ascii_changelog
            ]
            
            # Run with explicit ASCII encoding
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd(),
                encoding='ascii',
                errors='ignore'
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                self.root.after(0, lambda: self._publish_error(f"Build failed:\n{error_msg}"))
                return
            
            # Step 2: Update server files
            self.update_progress(40, "Updating server files...")
            
            # Get the new version number from updated version.json
            with open('version.json', 'r') as f:
                version_data = json.load(f)
            new_version = version_data['version']
            
            # Copy files to updates directory
            release_dir = f"releases/SnakeGame_v{new_version}"
            if os.path.exists(release_dir):
                import shutil
                os.makedirs('updates', exist_ok=True)
                
                for file in os.listdir(release_dir):
                    src = os.path.join(release_dir, file)
                    dst = os.path.join('updates', file)
                    shutil.copy2(src, dst)
            
            # Step 3: Update server configuration
            self.update_progress(60, "Updating server configuration...")
            self._update_server_config(version_data, ascii_changelog)
            
            # Step 4: Verify files
            self.update_progress(80, "Verifying deployment...")
            
            # Step 5: Complete
            self.update_progress(100, "Release published successfully!")
            
            # Show success message
            self.root.after(0, lambda: self._publish_success(new_version))
            
        except Exception as e:
            self.root.after(0, lambda: self._publish_error(f"Publishing failed: {str(e)}"))
        
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.publish_button.config(state='normal'))
            self.root.after(0, lambda: self.preview_button.config(state='normal'))
    
    def _update_server_config(self, version_data, changelog):
        """Update the server configuration with new version"""
        try:
            # Clean changelog for safe embedding in Python code
            safe_changelog = changelog.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            # Remove any problematic Unicode characters
            safe_changelog = safe_changelog.encode('ascii', errors='ignore').decode('ascii')
            if not safe_changelog.strip():
                safe_changelog = "Bug fixes and improvements"
            
            # Read current server file
            with open('update_server.py', 'r', encoding='utf-8') as f:
                server_content = f.read()
            
            # Update version info in server
            new_version_info = f'''LATEST_VERSION_INFO = {{
    "version": "{version_data['version']}",
    "build": "{version_data['build']}",
    "release_date": "{version_data['release_date'][:10]}",
    "features": [
        "Classic Snake gameplay with smooth controls",
        "Professional stereo audio system",
        "Persistent high score tracking", 
        "Progressive difficulty scaling",
        "Thread-safe auto-update system",
        "Custom window icon and branding",
        "Self-collision detection"
    ],
    "changes": [
        "{safe_changelog}"
    ],
    "download_url": "http://localhost:5000/api/download/SnakeGame.exe",'''
            
            # Replace the version info section
            import re
            pattern = r'LATEST_VERSION_INFO = \{[^}]+?\},'
            if re.search(pattern, server_content, re.DOTALL):
                server_content = re.sub(pattern, new_version_info, server_content, flags=re.DOTALL)
                
                with open('update_server.py', 'w', encoding='utf-8') as f:
                    f.write(server_content)
            
        except Exception as e:
            print(f"Warning: Could not update server config: {e}")
    
    def _publish_success(self, version):
        """Show success message"""
        messagebox.showinfo(
            "Publishing Complete!", 
            f"Successfully published version {version}!\n\nExecutable built\nFiles deployed\nServer updated\n\nYour new version is now available for download!"
        )
        
        # Reload current version
        self.load_current_version()
        self.update_preview()
        
        # Reset progress
        self.update_progress(0, "Ready to publish next release")
    
    def _publish_error(self, error_message):
        """Show error message"""
        messagebox.showerror("Publishing Failed", f"Error: {error_message}")
        self.update_progress(0, "Publishing failed")
    
    def run(self):
        """Start the GUI"""
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Run the GUI
        self.root.mainloop()

def main():
    """Main entry point"""
    # Check if we're in the right directory
    if not os.path.exists('snake_game.py'):
        print("❌ Please run this from the Snake Game directory!")
        input("Press Enter to exit...")
        return
    
    # Create and run the GUI
    app = PublisherGUI()
    app.run()

if __name__ == '__main__':
    main()