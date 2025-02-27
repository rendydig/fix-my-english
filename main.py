import keyboard
import tkinter as tk
from tkinter import Entry, Frame, Text, Scrollbar, Label
import threading
import pyautogui
import pystray
from PIL import Image, ImageDraw
import os
import sys

class QuickInputApp:
    def __init__(self):
        # Initialize main variables
        self.input_visible = False
        self.input_value = ""
        self.service_running = True
        
        # Set up the main window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        
        # Create the input window
        self.setup_input_window()
        
        # Register the global hotkey
        self.register_hotkey()
        
        # Start a thread to handle keyboard events
        self.running = True
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
        # Create and show the system tray icon
        self.setup_tray_icon()
    
    def setup_input_window(self):
        """Set up the floating input window"""
        self.input_window = tk.Toplevel(self.root)
        self.input_window.overrideredirect(True)  # Remove window border
        self.input_window.attributes("-topmost", True)  # Always on top
        self.input_window.attributes("-alpha", 0.9)  # Slight transparency
        
        # Calculate screen dimensions to center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size and position - increased height for multi-line text
        window_width = 400
        window_height = 150  # Increased height for multi-line text
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.input_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Create a frame with a border effect
        self.frame = Frame(self.input_window, bg="#2c3e50", padx=2, pady=2)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the multi-line text input field
        self.input_field = Text(self.frame, font=("Arial", 12), bg="#ecf0f1", 
                                fg="#2c3e50", insertbackground="#2c3e50",
                                relief=tk.FLAT, wrap=tk.WORD, height=5)
        self.input_field.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a scrollbar
        scrollbar = Scrollbar(self.input_field)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_field.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.input_field.yview)
        
        # Bind keyboard events
        self.input_field.bind("<Control-Return>", self.on_ctrl_enter_pressed)
        self.input_field.bind("<Escape>", self.hide_input)
        
        # Add a small label to indicate how to submit
        self.hint_label = Label(self.frame, text="Press Ctrl+Enter to submit", 
                                  font=("Arial", 8), fg="#7f8c8d", bg="#ecf0f1")
        self.hint_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        # Hide the window initially
        self.input_window.withdraw()
    
    def create_tray_icon_image(self):
        """Create a simple icon for the system tray"""
        # Create a simple colored square icon
        width = 64
        height = 64
        color = "#2c3e50"  # Dark blue
        
        image = Image.new('RGB', (width, height), color)
        dc = ImageDraw.Draw(image)
        
        # Draw a white 'Q' in the center
        # Use a simple method that doesn't require a font
        dc.rectangle([width//4, height//4, width*3//4, height*3//4], outline="white", width=2)
        dc.line([width//4, height//4, width*3//4, height*3//4], fill="white", width=2)
        dc.line([width*3//4, height//4, width//4, height*3//4], fill="white", width=2)
        
        return image
    
    def setup_tray_icon(self):
        """Set up the system tray icon with a menu"""
        icon_image = self.create_tray_icon_image()
        
        # Create the menu items
        menu = (
            pystray.MenuItem('Quick Input App', None, enabled=False),
            pystray.MenuItem('Service Status', None, enabled=False),
            pystray.MenuItem('Running', lambda: None, checked=lambda item: self.service_running),
            pystray.MenuItem('Start Service', self.start_service, enabled=lambda item: not self.service_running),
            pystray.MenuItem('Stop Service', self.stop_service, enabled=lambda item: self.service_running),
            pystray.MenuItem('Show Input', self.show_input, enabled=lambda item: self.service_running),
            pystray.MenuItem('Quit', self.quit_app)
        )
        
        # Create the icon
        self.icon = pystray.Icon("quick_input", icon_image, "Quick Input", menu)
        
        # Run the icon in a separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
        print("System tray icon created")
    
    def register_hotkey(self):
        """Register the global hotkey based on service status"""
        if self.service_running:
            try:
                keyboard.add_hotkey('ctrl+alt+space', self.toggle_input_field)
                print("Hotkey registered: CTRL+ALT+SPACE")
            except Exception as e:
                print(f"Error registering hotkey: {e}")
        else:
            try:
                keyboard.unhook_all_hotkeys()
                print("Hotkeys unregistered")
            except Exception as e:
                print(f"Error unregistering hotkeys: {e}")
    
    def start_service(self):
        """Start the service to enable hotkey functionality"""
        if not self.service_running:
            self.service_running = True
            self.register_hotkey()
            # Update the icon menu to reflect the new state
            self.icon.update_menu()
            print("Service started")
    
    def stop_service(self):
        """Stop the service to disable hotkey functionality"""
        if self.service_running:
            self.service_running = False
            self.register_hotkey()  # This will unhook all hotkeys
            # Hide the input field if it's visible
            if self.input_visible:
                self.hide_input()
            # Update the icon menu to reflect the new state
            self.icon.update_menu()
            print("Service stopped")
    
    def toggle_input_field(self):
        """Show or hide the input field based on current state"""
        if not self.service_running:
            return  # Do nothing if service is stopped
            
        if self.input_visible:
            self.hide_input()
        else:
            self.show_input()
    
    def show_input(self):
        """Show the input field in the middle of the screen"""
        if not self.service_running:
            return  # Do nothing if service is stopped
            
        # Update position to ensure it's centered on the current screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 150  # Match the new height
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.input_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Clear previous input and show the window
        self.input_field.delete("1.0", tk.END)  # Clear text from line 1, character 0 to end
        self.input_window.deiconify()
        self.input_field.focus_set()
        self.input_visible = True
        print("Input field shown")
    
    def hide_input(self, event=None):
        """Hide the input field"""
        self.input_window.withdraw()
        self.input_visible = False
        print("Input field hidden")
    
    def on_ctrl_enter_pressed(self, event):
        """Handle when Ctrl+Enter is pressed in the input field"""
        self.input_value = self.input_field.get("1.0", tk.END).strip()  # Get all text from line 1, character 0 to end
        print(f"Input received: {self.input_value}")
        # Here you can add any action you want to perform with the input
        self.hide_input()
    
    def keyboard_listener(self):
        """Thread function to listen for keyboard events"""
        while self.running:
            # This thread keeps running to ensure keyboard events are processed
            # The actual hotkey handling is done by the keyboard library
            threading.Event().wait(0.1)
    
    def quit_app(self):
        """Quit the application completely"""
        print("Quitting application...")
        self.running = False
        # Stop the icon
        self.icon.stop()
        # Clean up keyboard hooks
        keyboard.unhook_all()
        # Destroy Tkinter windows
        if self.root:
            self.root.quit()
            self.root.destroy()
        # Exit the application
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        try:
            print("Application running. Press CTRL+ALT+SPACE to show the input field.")
            print("Check the system tray for the application icon.")
            self.root.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.running = False
            keyboard.unhook_all()  # Clean up keyboard hooks

if __name__ == "__main__":
    app = QuickInputApp()
    app.run()