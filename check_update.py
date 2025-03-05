import requests
import re
import logging
import webbrowser
from tkinter import Toplevel, Label, Button, Frame, PhotoImage
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

class UpdateChecker:
    def __init__(self, current_version, current_os):
        self.current_version = current_version
        self.current_os = current_os
        self.version_url = "https://fixitai.hashnode.dev/version"
        self.download_url = "https://fixitai.hashnode.dev/download"
        self.latest_version = None
        self.download_link = None
        
    def check_for_updates(self):
        """Check if there's a newer version available"""
        try:
            # Get version information
            version_info = self._fetch_meta_content(self.version_url)
            if not version_info:
                logging.warning("Could not fetch version information")
                return False
                
            # Parse version information
            self.latest_version = self._parse_version_info(version_info)
            if not self.latest_version:
                logging.warning("Could not parse version information")
                return False
                
            # Get download link
            download_info = self._fetch_meta_content(self.download_url)
            if download_info:
                self.download_link = download_info.strip()
            
            # Compare versions
            if self._is_newer_version_available():
                logging.info(f"New version available: {self.latest_version}")
                return True
            else:
                logging.info("Application is up to date")
                return False
                
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")
            return False
    
    def _fetch_meta_content(self, url):
        """Fetch meta content from the specified URL"""
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(f"Failed to fetch data from {url}, status code: {response.status_code}")
                return None
                
            # Extract meta content using regex
            pattern = r'<meta property="og:description" content="([^"]*)"'
            match = re.search(pattern, response.text)
            
            if match:
                return match.group(1)
            else:
                logging.warning(f"Meta description not found in {url}")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching meta content: {str(e)}")
            return None
    
    def _parse_version_info(self, version_info):
        """Parse version information for the current OS"""
        try:
            # Expected format: "windows-1.0.0 - 2025/03/05 | macos-1.0.0 - 2025/03/05 | linux-1.0.0 - 2025/03/05"
            parts = version_info.split('|')
            
            # Map sys.platform to the expected OS prefix in the version info
            os_prefix_map = {
                'win32': 'windows',
                'darwin': 'macos',
                'linux': 'linux'
            }
            
            # Get the OS prefix based on the current OS
            os_prefix = os_prefix_map.get(self.current_os, self.current_os)
            
            for part in parts:
                part = part.strip()
                if part.startswith(os_prefix):
                    # Extract version number
                    version_match = re.search(r'(\d+\.\d+\.\d+)', part)
                    if version_match:
                        return version_match.group(1)
            
            # If no matching OS found, log a warning and return None
            logging.warning(f"No version information found for OS: {self.current_os} (mapped to {os_prefix})")
            return None
        except Exception as e:
            logging.error(f"Error parsing version info: {str(e)}")
            return None
    
    def _is_newer_version_available(self):
        """Check if the latest version is newer than the current version"""
        if not self.latest_version:
            return False
            
        # Parse version strings into tuples of integers
        current_parts = [int(x) for x in self.current_version.split('.')]
        latest_parts = [int(x) for x in self.latest_version.split('.')]
        
        # Compare version components
        for i in range(min(len(current_parts), len(latest_parts))):
            if latest_parts[i] > current_parts[i]:
                return True
            elif latest_parts[i] < current_parts[i]:
                return False
                
        # If we get here and latest version has more components, it's newer
        return len(latest_parts) > len(current_parts)

def show_update_window(parent, latest_version, download_link):
    """Show a window notifying the user about the update"""
    update_window = Toplevel(parent)
    update_window.title("Update Available")
    update_window.geometry("400x300")
    update_window.resizable(False, False)
    update_window.attributes("-topmost", True)
    
    # Set window icon
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            update_window.iconbitmap(icon_path)
    except Exception as e:
        logging.error(f"Error setting window icon: {str(e)}")
    
    # Create a frame with padding
    main_frame = Frame(update_window, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title label
    title_label = Label(main_frame, text="New Update Available!", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 15))
    
    # Version info
    version_label = Label(main_frame, text=f"Version {latest_version} is now available", 
                         font=("Segoe UI", 11),
                         wraplength=350)
    version_label.pack(pady=(0, 5))
    
    # Description
    desc_label = Label(main_frame, 
                      text="We recommend updating to the latest version\nto get the newest features and bug fixes.", 
                      font=("Segoe UI", 10), 
                      justify="center",
                      wraplength=350)
    desc_label.pack(pady=(0, 20))
    
    # Buttons frame
    button_frame = Frame(main_frame)
    button_frame.pack(pady=(10, 0))
    
    # Download button
    download_button = Button(button_frame, text="Download Update", font=("Segoe UI", 10),
                           command=lambda: open_download_link(download_link, update_window),
                           width=15, bg="#4CAF50", fg="white", relief="flat")
    download_button.pack(side="left", padx=5)
    
    # Remind later button
    remind_button = Button(button_frame, text="Remind Me Later", font=("Segoe UI", 10),
                         command=update_window.destroy,
                         width=15, relief="flat")
    remind_button.pack(side="left", padx=5)
    
    # Center the window on the screen
    update_window.update_idletasks()
    width = update_window.winfo_width()
    height = update_window.winfo_height()
    x = (update_window.winfo_screenwidth() // 2) - (width // 2)
    y = (update_window.winfo_screenheight() // 2) - (height // 2)
    update_window.geometry(f"{width}x{height}+{x}+{y}")
    
    return update_window

def show_up_to_date_window(parent):
    """Show a window notifying the user that the application is up-to-date"""
    up_to_date_window = Toplevel(parent)
    up_to_date_window.title("Up to Date")
    up_to_date_window.geometry("350x200")
    up_to_date_window.resizable(False, False)
    up_to_date_window.attributes("-topmost", True)
    
    # Set window icon
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            up_to_date_window.iconbitmap(icon_path)
    except Exception as e:
        logging.error(f"Error setting window icon: {str(e)}")
    
    # Create a frame with padding
    main_frame = Frame(up_to_date_window, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title label
    title_label = Label(main_frame, text="Application Up to Date", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 15))
    
    # Description - Add wrapping by setting width and wrap option
    desc_label = Label(main_frame, 
                      text="You are using the latest version of the application.", 
                      font=("Segoe UI", 11), 
                      justify="center",
                      wraplength=300)  # Set wrap length to ensure text wraps properly
    desc_label.pack(pady=(0, 20))
    
    # OK button
    ok_button = Button(main_frame, text="OK", font=("Segoe UI", 10),
                     command=up_to_date_window.destroy,
                     width=10, bg="#4CAF50", fg="white", relief="flat")
    ok_button.pack(pady=(10, 0))
    
    # Center the window on the screen
    up_to_date_window.update_idletasks()
    width = up_to_date_window.winfo_width()
    height = up_to_date_window.winfo_height()
    x = (up_to_date_window.winfo_screenwidth() // 2) - (width // 2)
    y = (up_to_date_window.winfo_screenheight() // 2) - (height // 2)
    up_to_date_window.geometry(f"{width}x{height}+{x}+{y}")
    
    return up_to_date_window

def open_download_link(url, window=None):
    """Open the download link in the default browser"""
    if url:
        try:
            webbrowser.open(url)
            if window:
                window.destroy()
        except Exception as e:
            logging.error(f"Error opening download link: {str(e)}")
    else:
        logging.error("No download link available")

def check_for_updates(app, show_up_to_date_notification=True):
    """Check for updates and show notification if available
    
    Args:
        app: The application instance
        show_up_to_date_notification: Whether to show a notification when the app is up-to-date
    """
    checker = UpdateChecker(app.version, app.current_os)
    if checker.check_for_updates():
        show_update_window(app.root, checker.latest_version, checker.download_link)
    elif show_up_to_date_notification:
        # Show notification that the application is up-to-date
        show_up_to_date_window(app.root)
