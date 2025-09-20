"""
Interactive Update Dialog for Snake Game
Shows update prompts with progress tracking without disturbing gameplay
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import os
import subprocess
import json
import sys

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class UpdateDialog:
    """Non-blocking update dialog that runs in separate thread"""
    
    def __init__(self, update_checker=None):
        self.update_checker = update_checker
        self.dialog_root = None
        self.progress_window = None
        self.is_downloading = False
        
    def show_update_prompt(self, update_info):
        """Show update available prompt in separate thread"""
        def create_dialog():
            try:
                # Create dialog window
                self.dialog_root = tk.Tk()
                self.dialog_root.title("Snake Game - Update Available")
                self.dialog_root.geometry("450x400")
                self.dialog_root.resizable(False, False)
                
                # Center the window
                self.dialog_root.geometry("+%d+%d" % (
                    self.dialog_root.winfo_screenwidth()/2 - 225,
                    self.dialog_root.winfo_screenheight()/2 - 200
                ))
                
                # Make it stay on top but not always
                self.dialog_root.lift()
                self.dialog_root.attributes('-topmost', True)
                self.dialog_root.after_idle(lambda: self.dialog_root.attributes('-topmost', False))
                
                # Create main frame
                main_frame = ttk.Frame(self.dialog_root, padding="20")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Title
                title_label = ttk.Label(main_frame, text="Snake Game Update Available!", 
                                      font=('Arial', 14, 'bold'))
                title_label.pack(pady=(0, 15))
                
                # Version info
                version_frame = ttk.LabelFrame(main_frame, text="Version Information", padding="10")
                version_frame.pack(fill=tk.X, pady=(0, 15))
                
                current_version = update_info.get('client_version', 'Unknown')
                new_version = update_info.get('server_version', 'Unknown')
                
                ttk.Label(version_frame, text=f"Current Version: {current_version}").pack(anchor=tk.W)
                ttk.Label(version_frame, text=f"New Version: {new_version}", 
                         font=('Arial', 9, 'bold')).pack(anchor=tk.W)
                
                # Changelog
                changelog_frame = ttk.LabelFrame(main_frame, text="What's New", padding="10")
                changelog_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
                
                # Create scrollable text widget
                changelog_text = tk.Text(changelog_frame, height=5, wrap=tk.WORD, 
                                       font=('Arial', 9), state=tk.DISABLED)
                scrollbar = ttk.Scrollbar(changelog_frame, orient=tk.VERTICAL, command=changelog_text.yview)
                changelog_text.configure(yscrollcommand=scrollbar.set)
                
                # Add changelog content
                changelog_content = self._format_changelog(update_info.get('changelog', []))
                changelog_text.config(state=tk.NORMAL)
                changelog_text.insert(tk.END, changelog_content)
                changelog_text.config(state=tk.DISABLED)
                
                changelog_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Buttons
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill=tk.X, pady=(15, 0))
                
                # Create prominent Yes/No buttons
                yes_button = ttk.Button(button_frame, text="Yes, Download Update", 
                                      command=self._start_download)
                yes_button.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
                
                no_button = ttk.Button(button_frame, text="No, Maybe Later", 
                                     command=self._close_dialog)
                no_button.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
                
                # Add a skip option below
                skip_frame = ttk.Frame(main_frame)
                skip_frame.pack(fill=tk.X, pady=(10, 0))
                
                skip_button = ttk.Button(skip_frame, text="Skip this version", 
                                       command=self._skip_version)
                skip_button.pack(pady=(5, 0))
                
                # Handle window close
                self.dialog_root.protocol("WM_DELETE_WINDOW", self._close_dialog)
                
                # Start the dialog
                self.dialog_root.mainloop()
                
            except Exception as e:
                print(f"Error creating update dialog: {e}")
        
        # Run dialog in separate thread to not block game
        threading.Thread(target=create_dialog, daemon=True).start()
    
    def _format_changelog(self, changelog):
        """Format changelog for display"""
        if not changelog:
            return "No changelog available."
        
        formatted = ""
        for entry in changelog:
            if isinstance(entry, dict) and 'version' in entry:
                formatted += f"Version {entry['version']}:\n"
                changes = entry.get('changes', [])
                if isinstance(changes, list):
                    for change in changes:
                        formatted += f"  • {change}\n"
                formatted += "\n"
            elif isinstance(entry, str):
                formatted += f"  • {entry}\n"
        
        return formatted.strip() if formatted else "Bug fixes and improvements."
    
    def _start_download(self):
        """Start the download process"""
        self.is_downloading = True
        self.dialog_root.destroy()
        self.dialog_root = None
        
        # Show progress dialog
        self._show_progress_dialog()
        
        # Start download in background
        threading.Thread(target=self._download_update, daemon=True).start()
    
    def _show_progress_dialog(self):
        """Show download progress dialog"""
        def create_progress():
            try:
                self.progress_window = tk.Tk()
                self.progress_window.title("Snake Game - Downloading Update")
                self.progress_window.geometry("400x150")
                self.progress_window.resizable(False, False)
                
                # Center window
                self.progress_window.geometry("+%d+%d" % (
                    self.progress_window.winfo_screenwidth()/2 - 200,
                    self.progress_window.winfo_screenheight()/2 - 75
                ))
                
                # Make it stay on top
                self.progress_window.attributes('-topmost', True)
                
                # Create progress frame
                progress_frame = ttk.Frame(self.progress_window, padding="20")
                progress_frame.pack(fill=tk.BOTH, expand=True)
                
                # Progress label
                self.progress_label = ttk.Label(progress_frame, text="Preparing download...", 
                                              font=('Arial', 10))
                self.progress_label.pack(pady=(0, 15))
                
                # Progress bar
                self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', 
                                                  length=350)
                self.progress_bar.pack(pady=(0, 15))
                self.progress_bar.start(10)
                
                # Cancel button
                ttk.Button(progress_frame, text="Cancel", 
                          command=self._cancel_download).pack()
                
                # Handle window close
                self.progress_window.protocol("WM_DELETE_WINDOW", self._cancel_download)
                
                self.progress_window.mainloop()
                
            except Exception as e:
                print(f"Error creating progress dialog: {e}")
        
        threading.Thread(target=create_progress, daemon=True).start()
    
    def _download_update(self):
        """Download and install the update"""
        if not REQUESTS_AVAILABLE:
            self._update_progress("Error: requests library not available")
            return
            
        try:
            self._update_progress("Checking for updates...")
            time.sleep(1)
            
            # Get download URL from config
            config_url = self._get_server_url()
            download_url = f"{config_url}/api/download"
            
            self._update_progress(f"Downloading from {config_url}...")
            
            # Download the update
            response = requests.get(download_url, stream=True, timeout=30)
            if response.status_code == 200:
                # Save to temporary location
                temp_file = os.path.join(os.getcwd(), "SnakeGame_Update.exe")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk and self.is_downloading:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                self._update_progress(f"Downloaded {percent}% ({downloaded:,} bytes)")
                
                if self.is_downloading:
                    self._update_progress("Download complete! Preparing installation...")
                    time.sleep(1)
                    
                    # Replace current executable
                    current_exe = "SnakeGame.exe"
                    backup_exe = "SnakeGame_backup.exe"
                    
                    # Create backup
                    if os.path.exists(current_exe):
                        if os.path.exists(backup_exe):
                            os.remove(backup_exe)
                        os.rename(current_exe, backup_exe)
                    
                    # Install new version
                    os.rename(temp_file, current_exe)
                    
                    self._update_progress("Update installed successfully!")
                    time.sleep(2)
                    
                    # Close progress dialog
                    if self.progress_window:
                        self.progress_window.destroy()
                    
                    # Show completion message
                    self._show_completion_dialog()
                
            else:
                self._update_progress(f"Download failed: HTTP {response.status_code}")
                
        except Exception as e:
            self._update_progress(f"Error: {str(e)}")
            print(f"Download error: {e}")
    
    def _get_server_url(self):
        """Get server URL from config"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('update_server_url', 'http://localhost:5000')
        except:
            return 'http://localhost:5000'
    
    def _update_progress(self, message):
        """Update progress dialog text"""
        if self.progress_window and hasattr(self, 'progress_label'):
            try:
                self.progress_label.config(text=message)
                self.progress_window.update()
            except:
                pass
    
    def _show_completion_dialog(self):
        """Show update completion dialog"""
        def show_completion():
            try:
                messagebox.showinfo("Update Complete", 
                                  "Snake Game has been updated successfully!\n\n" +
                                  "The game will continue running with the current session.\n" +
                                  "Restart the game to use the new version.")
            except:
                print("Update completed successfully!")
        
        threading.Thread(target=show_completion, daemon=True).start()
    
    def _cancel_download(self):
        """Cancel the download"""
        self.is_downloading = False
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None
        print("Update download cancelled")
    
    def _close_dialog(self):
        """Close the update dialog"""
        if self.dialog_root:
            self.dialog_root.destroy()
            self.dialog_root = None
    
    def _skip_version(self):
        """Skip this version update"""
        self._close_dialog()
        print("Update skipped")

def show_manual_update_check(update_checker):
    """Show manual update check dialog"""
    if not update_checker:
        def show_error():
            try:
                messagebox.showwarning("Update System", 
                                     "Update system is not available.\n" +
                                     "Please check your internet connection and try again.")
            except:
                print("Update system not available")
        threading.Thread(target=show_error, daemon=True).start()
        return
    
    def check_updates():
        try:
            print("INFO: Manual update check requested (F5 pressed)")
            
            # Show "checking" message
            def show_checking():
                try:
                    # Create a simple checking dialog
                    check_window = tk.Tk()
                    check_window.title("Snake Game - Checking for Updates")
                    check_window.geometry("300x100")
                    check_window.resizable(False, False)
                    
                    # Center window
                    check_window.geometry("+%d+%d" % (
                        check_window.winfo_screenwidth()/2 - 150,
                        check_window.winfo_screenheight()/2 - 50
                    ))
                    
                    # Make it stay on top
                    check_window.attributes('-topmost', True)
                    
                    # Create frame
                    frame = ttk.Frame(check_window, padding="20")
                    frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Label
                    ttk.Label(frame, text="Checking for updates...", 
                             font=('Arial', 10)).pack(pady=(0, 10))
                    
                    # Progress bar
                    progress = ttk.Progressbar(frame, mode='indeterminate', length=250)
                    progress.pack()
                    progress.start(10)
                    
                    # Auto-close after 3 seconds
                    check_window.after(3000, check_window.destroy)
                    check_window.mainloop()
                    
                except:
                    pass
            
            # Show checking dialog in background
            threading.Thread(target=show_checking, daemon=True).start()
            
            # Wait a moment for visual feedback
            time.sleep(1)
            
            # Check for updates
            update_info = update_checker.check_for_updates_sync(force_check=True)
            
            if update_info and update_info.get('update_available'):
                print(f"INFO: Update available: {update_info.get('server_version')}")
                # Show update dialog
                dialog = UpdateDialog(update_checker)
                dialog.show_update_prompt(update_info)
            else:
                # Show "no updates" message
                def show_no_updates():
                    try:
                        messagebox.showinfo("No Updates", 
                                          "You're running the latest version of Snake Game!\n\n" +
                                          f"Current version: {update_info.get('client_version', 'Unknown') if update_info else 'Unknown'}")
                    except:
                        print("INFO: No updates available - you're running the latest version!")
                
                threading.Thread(target=show_no_updates, daemon=True).start()
                
        except Exception as e:
            print(f"ERROR: Update check failed: {e}")
            def show_error():
                try:
                    messagebox.showerror("Update Error", 
                                       f"Could not check for updates:\n\n{str(e)}\n\n" +
                                       "Please check your internet connection and try again.")
                except:
                    print(f"Update check failed: {e}")
            
            threading.Thread(target=show_error, daemon=True).start()
    
    # Run update check in background thread
    threading.Thread(target=check_updates, daemon=True).start()