
import tkinter as tk
from tkinter import Label
from tkinter import ttk

from tray_icon import create_tray_icon_image

class LoadingWindow:
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Loading")
        self.root.overrideredirect(True)  # Remove window border
        self.root.attributes("-topmost", True)  # Always on top
        
        # Set window size and position
        window_width = 300
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Create a canvas for rounded rectangle background
        self.canvas = tk.Canvas(self.root, bg="#3498db", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create rounded rectangle method
        self.canvas.create_rounded_rectangle = lambda *args, **kwargs: self._create_rounded_rectangle(self.canvas, *args, **kwargs)
        
        # Draw rounded rectangle
        radius = 15
        self.canvas.create_rounded_rectangle(
            3, 3, window_width-3, window_height-3, radius, 
            fill="#ffffff", outline="#3498db", width=2
        )
        
        # Add loading label
        self.loading_label = Label(self.canvas, text="Loading...", font=("Segoe UI", 14, "bold"), 
                                  bg="#ffffff", fg="#3498db")
        self.loading_label.place(relx=0.5, rely=0.3, anchor="center")
        
        # Add progress bar
        self.progress = ttk.Progressbar(self.canvas, orient="horizontal", 
                                      length=200, mode="indeterminate")
        self.progress.place(relx=0.5, rely=0.5, anchor="center")
        self.progress.start(15)  # Start the progress animation
        
        # Add status label
        self.status_label = Label(self.canvas, text="Initializing application...", 
                                 font=("Segoe UI", 9), bg="#ffffff", fg="#555555")
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")
    
    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Helper function to create a rounded rectangle on a canvas"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def update_status(self, text):
        """Update the status text"""
        self.status_label.config(text=text)
        self.root.update()
    
    def close(self):
        """Close the loading window"""
        self.progress.stop()
        self.root.destroy()
