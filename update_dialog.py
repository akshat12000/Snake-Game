"""
Update Dialog for Snake Game
Provides user interface for update notifications and downloads
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import sys
import os

try:
    from update_checker import UpdateChecker
except ImportError:
    # Fallback if update_checker not available
    UpdateChecker = None

class UpdateDialog:
    def __init__(self, parent=None):
        self.parent = parent
        self.update_checker = UpdateChecker() if UpdateChecker else None
        self.dialog = None
        self.progress_var = None
        
    def show_update_available(self, update_info):
        """Show dialog when update is available"""
        self.dialog = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.dialog.title("Snake Game - Update Available")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎮 Snake Game Update Available!", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Version info
        current_version = "1.0.0"  # Default fallback
        if self.update_checker:
            current_version = self.update_checker.version_manager.get_current_version()
        new_version = update_info.get('latest_version', 'Unknown')
        
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Current Version: {current_version}").pack(anchor="w")
        ttk.Label(
            version_frame, 
            text=f"New Version: {new_version}", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w")
        
        # Release date
        release_date = update_info.get('release_date', 'Unknown')
        ttk.Label(version_frame, text=f"Release Date: {release_date}").pack(anchor="w")
        
        # Changes/Features
        changes_frame = ttk.LabelFrame(main_frame, text="What's New", padding="10")
        changes_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create scrollable text widget
        text_frame = ttk.Frame(changes_frame)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        changes_text = tk.Text(
            text_frame, 
            wrap="word", 
            yscrollcommand=scrollbar.set,
            height=8,
            font=("Arial", 9)
        )
        changes_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=changes_text.yview)
        
        # Populate changes
        changes = update_info.get('changes', [])
        features = update_info.get('features', [])
        
        if changes:
            changes_text.insert("end", "🆕 New in this version:\n")
            for change in changes:
                changes_text.insert("end", f"  • {change}\n")
            changes_text.insert("end", "\n")
        
        if features:
            changes_text.insert("end", "✨ All features:\n")
            for feature in features:
                changes_text.insert("end", f"  • {feature}\n")
        
        changes_text.config(state="disabled")
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100
        )
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Later", 
            command=self.close_dialog
        ).pack(side="right", padx=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Download & Install", 
            command=lambda: self.start_download(update_info)
        ).pack(side="right")
        
        # File size info
        file_size = update_info.get('file_size', 0)
        if file_size > 0:
            size_mb = file_size / (1024 * 1024)
            ttk.Label(
                button_frame, 
                text=f"Download size: {size_mb:.1f} MB"
            ).pack(side="left")
    
    def start_download(self, update_info):
        """Start downloading update in background thread"""
        # Show progress bar
        self.progress_bar.pack(fill="x", pady=(10, 0))
        
        # Disable download button
        for widget in self.dialog.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child['text'] == "Download & Install":
                        child.config(state="disabled")
        
        # Start download thread
        download_thread = threading.Thread(
            target=self.download_update,
            args=(update_info,)
        )
        download_thread.daemon = True
        download_thread.start()
    
    def download_update(self, update_info):
        """Download update with progress callback"""
        def progress_callback(progress):
            self.dialog.after(0, lambda: self.progress_var.set(progress))
        
        if not self.update_checker:
            self.dialog.after(0, lambda: self.download_failed("Update system not available"))
            return
            
        success, result = self.update_checker.download_update(update_info, progress_callback)
        
        if success:
            self.dialog.after(0, lambda: self.download_completed(result))
        else:
            self.dialog.after(0, lambda: self.download_failed(result))
    
    def download_completed(self, filename):
        """Handle successful download"""
        messagebox.showinfo(
            "Download Complete",
            f"Update downloaded successfully!\n\n"
            f"File: {filename}\n\n"
            f"The game will now close and the update will install automatically."
        )
        
        # Here you would typically:
        # 1. Close the current game
        # 2. Launch the installer
        # 3. Exit the current process
        
        try:
            # Launch the downloaded installer
            if os.path.exists(filename):
                subprocess.Popen([filename])
                # Close current application
                sys.exit(0)
            else:
                raise FileNotFoundError(f"Downloaded file {filename} not found")
        except Exception as e:
            messagebox.showerror("Update Error", f"Could not launch installer: {e}")
        
        self.close_dialog()
    
    def download_failed(self, error_message):
        """Handle download failure"""
        messagebox.showerror(
            "Download Failed",
            f"Could not download update:\n{error_message}\n\n"
            f"Please try again later or download manually from our website."
        )
        self.close_dialog()
    
    def close_dialog(self):
        """Close the update dialog"""
        if self.dialog:
            self.dialog.destroy()
    
    def check_and_notify(self, force_check=False):
        """Check for updates and show dialog if available"""
        if not self.update_checker:
            if force_check:
                messagebox.showinfo("Update Check", "Update system not available")
            return False
            
        if not self.update_checker.should_check_for_updates(force_check):
            return False
        
        try:
            is_available, update_info = self.update_checker.is_update_available()
            if is_available and update_info:
                self.show_update_available(update_info)
                return True
            return False
        except Exception as e:
            if force_check:  # Only show error if user explicitly checked
                messagebox.showerror("Update Check Failed", f"Could not check for updates: {e}")
            return False

# Standalone test
if __name__ == "__main__":
    # Test the update dialog
    test_update_info = {
        "latest_version": "1.1.0",
        "release_date": "2024-12-20",
        "changes": [
            "Added auto-update functionality",
            "Custom window icon support",
            "Improved error handling"
        ],
        "features": [
            "Classic Snake gameplay",
            "Professional audio system",
            "Auto-update system"
        ],
        "file_size": 25600000
    }
    
    dialog = UpdateDialog()
    dialog.show_update_available(test_update_info)
    
    if dialog.dialog:
        dialog.dialog.mainloop()