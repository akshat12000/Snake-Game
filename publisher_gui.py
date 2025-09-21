#!/usr/bin/env python3
"""
Developer Publishing GUI - One-Click Release Tool
Simple interface for version management and deployment
"""

import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import threading
import subprocess
import sys
import json
import os
from pathlib import Path

class PublisherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game Publisher")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        self.root.minsize(600, 700)
        
        self.setup_ui()
        self.load_current_version()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Snake Game Publisher", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Current version frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Version", padding="10")
        current_frame.pack(fill="x", pady=(0, 20))
        
        self.current_version_label = ttk.Label(current_frame, text="Loading...", font=("Arial", 12))
        self.current_version_label.pack()
        
        # Release type frame
        release_frame = ttk.LabelFrame(main_frame, text="Release Type", padding="10")
        release_frame.pack(fill="x", pady=(0, 20))
        
        self.version_type = tk.StringVar(value="patch")
        release_types = [
            ("Patch (1.0.0 → 1.0.1) - Bug fixes", "patch"),
            ("Minor (1.0.0 → 1.1.0) - New features", "minor"),
            ("Major (1.0.0 → 2.0.0) - Breaking changes", "major")
        ]
        
        for text, value in release_types:
            ttk.Radiobutton(
                release_frame, 
                text=text, 
                variable=self.version_type, 
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Changelog frame
        changelog_frame = ttk.LabelFrame(main_frame, text="Release Notes", padding="10")
        changelog_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ttk.Label(changelog_frame, text="What's new in this release:").pack(anchor=tk.W, pady=(0, 5))
        self.changelog_text = tk.Text(changelog_frame, height=6, wrap=tk.WORD)
        self.changelog_text.pack(fill="both", expand=True, pady=(0, 10))
        self.changelog_text.insert("1.0", "Bug fixes and improvements")
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 20))
        
        # Row 1: Main actions
        row1 = ttk.Frame(button_frame)
        row1.pack(fill="x", pady=(0, 10))
        
        self.publish_btn = ttk.Button(
            row1, 
            text="Publish Release", 
            command=self.publish_release,
            width=20
        )
        self.publish_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = ttk.Button(
            row1, 
            text="Refresh Version", 
            command=self.load_current_version,
            width=20
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Row 2: Server actions
        row2 = ttk.Frame(button_frame)
        row2.pack(fill="x", pady=(0, 10))
        
        self.test_btn = ttk.Button(
            row2, 
            text="Test Local Server", 
            command=self.test_server,
            width=20
        )
        self.test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=(0, 10))
        
        # Output console frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Console", padding="10")
        output_frame.pack(fill="both", expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.output_text.pack(fill="both", expand=True)
        
    def load_current_version(self):
        """Load and display current version"""
        try:
            if os.path.exists("version.json"):
                with open("version.json", "r") as f:
                    version_data = json.load(f)
                version = version_data.get("version", "1.0.0")
                release_date = version_data.get("release_date", "Unknown")
                self.current_version_label.config(
                    text=f"Version: {version} (Released: {release_date})"
                )
            else:
                self.current_version_label.config(text="Version: 1.0.0 (No version file found)")
        except Exception as e:
            self.current_version_label.config(text=f"Error loading version: {str(e)}")
        
    def log(self, message):
        """Add message to output console"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_progress(self):
        """Start progress bar and disable buttons"""
        self.progress.start()
        self.publish_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        
    def stop_progress(self):
        """Stop progress bar and enable buttons"""
        self.progress.stop()
        self.publish_btn.config(state="normal")
        self.test_btn.config(state="normal")
        
    def publish_release(self):
        """Publish a new release"""
        changelog = self.changelog_text.get("1.0", tk.END).strip()
        if not changelog:
            messagebox.showerror("Error", "Please enter release notes")
            return
            
        def publish_worker():
            try:
                self.start_progress()
                self.log("Starting release publishing...")
                self.log(f"Version type: {self.version_type.get()}")
                self.log(f"Release notes: {changelog}")
                
                # Run the publisher
                version_type = self.version_type.get()
                result = subprocess.run([
                    sys.executable, "developer_publisher.py", 
                    "--type", version_type, 
                    "--message", changelog
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                self.log(result.stdout)
                if result.stderr:
                    self.log(f"Errors: {result.stderr}")
                
                if result.returncode == 0:
                    self.log("Publishing completed successfully!")
                    self.load_current_version()  # Refresh version display
                    messagebox.showinfo("Success", "Release published successfully!")
                else:
                    self.log("Publishing failed!")
                    messagebox.showerror("Error", "Publishing failed. Check the output for details.")
                    
            except Exception as e:
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Publishing failed: {str(e)}")
            finally:
                self.stop_progress()
                
        # Run in background thread
        thread = threading.Thread(target=publish_worker, daemon=True)
        thread.start()
        
    def test_server(self):
        """Test the update server"""
        def test_worker():
            try:
                self.start_progress()
                self.log("Starting local update server...")
                
                # Start local server for testing
                result = subprocess.Popen([
                    sys.executable, "update_server.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                self.log("Local update server started on http://localhost:8080")
                self.log("Server is running in background. You can test it now.")
                self.log("Try: http://localhost:8080/version")
                self.log("Try: http://localhost:8080/health")
                
                messagebox.showinfo(
                    "Server Started", 
                    "Local update server is running on:\nhttp://localhost:8080\n\nCheck the output console for details."
                )
                
            except Exception as e:
                self.log(f"Server test error: {str(e)}")
                messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            finally:
                self.stop_progress()
                
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
        
    def run(self):
        """Run the GUI"""
        self.log("Snake Game Publisher Ready!")
        self.log("Select release type, enter notes, then click 'Publish Release'")
        self.log("Server will auto-deploy via GitHub → Railway integration")
        self.root.mainloop()

def main():
    """Main entry point"""
    app = PublisherGUI()
    app.run()

if __name__ == "__main__":
    main()