"""
Simple Update Checker - Separate from core game
Handles version checking and update prompts
"""
import json
import os
import sys
import subprocess
import time
import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.error

class UpdateChecker:
    def __init__(self):
        # Use Railway server URL for production, fallback to localhost for development
        self.SERVER_URL = "https://web-production-7380.up.railway.app"
        self.VERSION_FILE = "version.json"
        
    def get_current_version(self):
        """Get current game version from local version.json (works in exe and dev)"""
        try:
            # Try multiple locations for version.json
            possible_paths = [
                self.VERSION_FILE,  # Current directory (development)
                os.path.join(os.path.dirname(sys.executable), self.VERSION_FILE),  # Next to exe
                os.path.join(sys._MEIPASS, self.VERSION_FILE) if hasattr(sys, '_MEIPASS') else None,  # Inside PyInstaller bundle
            ]
            
            # Filter out None values
            possible_paths = [path for path in possible_paths if path is not None]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        data = json.load(f)
                        version = data.get('version', '1.0.0')
                        print(f"[UPDATE] Found version {version} in {path}")
                        return version
            
            # If no version file found, return default
            print("[UPDATE] No version.json found, using default version 1.0.0")
            return '1.0.0'
            
        except Exception as e:
            print(f"[UPDATE] Error reading version: {e}")
            return '1.0.0'
    
    def check_for_updates(self):
        """Check server for newer version with detailed error reporting"""
        current_version = self.get_current_version()
        
        try:
            # Simple HTTP request to server
            url = f"{self.SERVER_URL}/version"
            print(f"[UPDATE] Checking for updates at: {url}")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status != 200:
                    return {'update_available': False, 'error': f'Server returned status {response.status}'}
                
                server_data = json.loads(response.read())
                server_version = server_data.get('version', '1.0.0')
                
                print(f"[UPDATE] Current version: {current_version}, Server version: {server_version}")
                
                if self.is_newer_version(server_version, current_version):
                    return {
                        'update_available': True,
                        'current_version': current_version,
                        'new_version': server_version,
                        'changelog': server_data.get('changelog', [])
                    }
                else:
                    return {'update_available': False}
                    
        except urllib.error.URLError as e:
            error_msg = f"Network error: {str(e)}"
            print(f"[UPDATE] {error_msg}")
            return {'update_available': False, 'error': error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid server response: {str(e)}"
            print(f"[UPDATE] {error_msg}")
            return {'update_available': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[UPDATE] {error_msg}")
            return {'update_available': False, 'error': error_msg}
    
    def is_newer_version(self, server_version, current_version):
        """Simple version comparison (assumes semantic versioning)"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        return version_tuple(server_version) > version_tuple(current_version)
    
    def prompt_update(self, update_info):
        """Show update prompt to user"""
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Extract changelog information properly
        changelog_entries = update_info.get('changelog', [])
        changelog_text = ""
        
        if isinstance(changelog_entries, list) and changelog_entries:
            # Get the latest version's changes
            latest_entry = changelog_entries[0] if changelog_entries else {}
            if isinstance(latest_entry, dict) and 'changes' in latest_entry:
                changes = latest_entry.get('changes', [])
                if isinstance(changes, list):
                    changelog_text = '\n'.join('• ' + str(change) for change in changes)
                else:
                    changelog_text = '• ' + str(changes)
            else:
                # Fallback: try to use the entry directly as a string
                changelog_text = '• ' + str(latest_entry)
        
        if not changelog_text:
            changelog_text = '• Bug fixes and improvements'
        
        message = f"""Update Available!
        
Current Version: {update_info['current_version']}
New Version: {update_info['new_version']}

What's New:
{changelog_text}

Would you like to update now?
The game will close and restart with the new version."""
        
        result = messagebox.askyesno("Update Available", message)
        root.destroy()
        return result
    
    def download_and_install(self):
        """Download new version and restart game with progress indication"""
        import threading
        from tkinter import ttk
        
        # Create progress window
        progress_window = tk.Tk()
        progress_window.title("Updating Game")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.eval('tk::PlaceWindow . center')
        
        # Progress elements
        status_label = tk.Label(progress_window, text="Preparing download...", font=("Arial", 10))
        status_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, length=350, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        def update_progress(text):
            status_label.config(text=text)
            progress_window.update()
        
        def download_thread():
            try:
                update_progress("Connecting to server...")
                
                # Download new executable
                download_url = f"{self.SERVER_URL}/download"
                print(f"[UPDATE] Attempting download from: {download_url}")
                
                # Check if server has actual download available
                response = urllib.request.urlopen(download_url, timeout=30)
                content_type = response.headers.get('content-type', '')
                print(f"[UPDATE] Server response content-type: {content_type}")
                
                if 'application/json' in content_type:
                    # Server returned JSON error message instead of file
                    error_data = json.loads(response.read())
                    progress_window.destroy()
                    
                    root = tk.Tk()
                    root.withdraw()
                    message = f"Download not available:\n\n{error_data.get('message', 'Server error')}"
                    if 'instructions' in error_data:
                        message += "\n\n" + "\n".join(error_data['instructions'])
                    messagebox.showwarning("Download Not Available", message)
                    root.destroy()
                    return
                
                # Close the initial response and reopen for streaming download
                response.close()
                
                update_progress("Downloading update...")
                
                # Actual file download with proper streaming and timeout
                with urllib.request.urlopen(download_url, timeout=300) as response:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    print(f"[UPDATE] Download started, total size: {total_size} bytes")
                    
                    with open("SnakeGame_new.exe", "wb") as f:
                        while True:
                            chunk = response.read(8192)  # 8KB chunks
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Update progress text with download info
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_downloaded = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                update_progress(f"Downloading update... {percent:.1f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)")
                            else:
                                mb_downloaded = downloaded / (1024 * 1024)
                                update_progress(f"Downloading update... {mb_downloaded:.1f}MB downloaded")
                
                print(f"[UPDATE] Download completed, {downloaded} bytes downloaded")
                
                update_progress("Preparing installation...")
                
                # Create update script that will replace the current exe
                update_script = f"""
import time
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

try:
    time.sleep(2)  # Wait for game to close
    
    # Show installation progress
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Installing Update", "Installing update... Please wait.")
    root.destroy()
    
    # Replace the executable
    if os.path.exists("SnakeGame.exe"):
        os.remove("SnakeGame.exe")
    os.rename("SnakeGame_new.exe", "SnakeGame.exe")
    
    # Show success message
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Update Complete", "Update installed successfully!\\nStarting updated game...")
    root.destroy()
    
    # Start the updated game
    subprocess.Popen(["SnakeGame.exe"])
    
except Exception as e:
    # Show error message
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Update Error", f"Failed to install update:\\n{{str(e)}}")
    root.destroy()
finally:
    # Clean up
    try:
        os.remove(__file__)
    except:
        pass
"""
                
                with open("update_installer.py", "w") as f:
                    f.write(update_script)
                
                update_progress("Update ready! Restarting game...")
                time.sleep(1)
                
                progress_window.destroy()
                
                # Show final message before restart
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("Update Downloaded", "Update downloaded successfully!\\nThe game will now restart with the new version.")
                root.destroy()
                
                # Run update script and exit current game
                subprocess.Popen([sys.executable, "update_installer.py"])
                sys.exit(0)
                
            except Exception as e:
                progress_window.destroy()
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Update Error", f"Failed to download update:\\n{str(e)}")
                root.destroy()
        
        # Start download in background thread
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        # Show progress window
        progress_window.mainloop()
    
    def check_and_prompt_for_updates(self):
        """Main update flow - check and prompt user with better error handling"""
        try:
            # Show checking message first
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("Checking Updates", "Checking for updates... Please wait.")
            root.destroy()
            
            update_info = self.check_for_updates()
            
            if update_info.get('update_available'):
                if self.prompt_update(update_info):
                    self.download_and_install()
            elif 'error' in update_info:
                # Show error to user
                root = tk.Tk()
                root.withdraw()
                error_msg = f"Unable to check for updates:\n\n{update_info['error']}\n\nPlease check your internet connection and try again."
                messagebox.showwarning("Update Check Failed", error_msg)
                root.destroy()
            else:
                # No update available
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("No Updates", "You're already running the latest version!")
                root.destroy()
                
        except Exception as e:
            # Catch any unexpected errors
            root = tk.Tk()
            root.withdraw()
            
            # Safely convert error to string
            if hasattr(e, 'args') and e.args:
                error_str = str(e.args[0])
            else:
                error_str = str(e)
                
            error_msg = f"Update check failed with an unexpected error:\n\n{error_str}\n\nPlease try again later."
            messagebox.showerror("Update Error", error_msg)
            root.destroy()