import keyboard
import tkinter as tk
from tkinter import Frame, Text, Label, messagebox,ttk
import threading
import pyautogui
import pystray
import os
import sys
import google.generativeai as genai
import re
from show_explanation_window import show_explanation_window
import show_latest_tips
from tray_icon import create_tray_icon_image
import time
from loading_window import LoadingWindow
from notification_window import NotificationWindow
import logging
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from donate_window import show_donate_window

class QuickInputApp:
    def __init__(self):
        # Initialize main variables
        self.input_visible = False
        self.input_value = ""
        self.service_running = True
        self.last_position = None  # Initialize last_position to avoid AttributeError
        
        # Tips feature variables
        self.tips_enabled = False  # Disabled by default
        self.tips_timer = None
        self.tips_window = None
        self.latest_tip = None  # Store the latest tip
        
        # Tips intervals in milliseconds
        self.tips_intervals = {
            "1min": 1 * 60 * 1000,
            "3min": 3 * 60 * 1000,
            "5min": 5 * 60 * 1000,
            "10min": 10 * 60 * 1000
        }
        self.current_interval_key = "5min"  # Default interval key
        self.tips_interval = self.tips_intervals[self.current_interval_key]  # Default to 5 minutes
        
        # Set up logging
        self.setup_logging()
        
        # Set up the main window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        
        # Configure custom scrollbar style
        self.configure_scrollbar_style()
        
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
        
        # Set up Google Generative AI
        if not self.setup_api_key():
            return
        
        # Initialize the tips feature
        self.setup_tips_feature()
        
        # Initialize correction count
        self.correction_count = self._load_correction_count()

    def setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a timestamp for the log filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"gemini_api_{timestamp}.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logging.info("Logging system initialized")
    
    def setup_input_window(self):
        """Set up the floating input window"""
        self.input_window = tk.Toplevel(self.root)
        self.input_window.overrideredirect(True)  # Remove window border
        self.input_window.attributes("-topmost", True)  # Always on top
        self.input_window.attributes("-alpha", 0.95)  # Slight transparency (increased for better readability)
        
        # Set transparent background for the window to create rounded corners effect
        self.input_window.attributes("-transparentcolor", "")
        
        # Calculate screen dimensions to center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size and position - increased height for multi-line text
        window_width = 400
        window_height = 250  # Increased height for multi-line text
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.input_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Create a canvas for the background with rounded corners
        self.canvas = tk.Canvas(self.input_window, bg="#3498db", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add the create_rounded_rectangle method to this canvas
        self.canvas.create_rounded_rectangle = lambda *args, **kwargs: self._create_rounded_rectangle(self.canvas, *args, **kwargs)
        
        # Draw rounded rectangle on canvas
        radius = 15
        self.rounded_rect = self.canvas.create_rounded_rectangle(
            3, 3, window_width-3, window_height-3, radius, 
            fill="#ffffff", outline="#3498db", width=2
        )
        
        # Create a frame inside the rounded rectangle
        frame_margin = 20  # Margin from the edges
        self.frame = Frame(self.canvas, bg="#ffffff", bd=0, highlightthickness=0)
        self.frame.place(x=frame_margin, y=frame_margin, 
                        width=window_width-2*frame_margin, 
                        height=window_height-2*frame_margin)
        
        # Create a title label
        self.title_label = Label(self.frame, text="Fix my english", 
                               font=("Segoe UI", 12, "bold"), fg="#3498db", bg="#ffffff")
        self.title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add instruction label for CTRL+ENTER shortcut
        self.shortcut_label = Label(self.frame, text="Press CTRL+ENTER to submit", 
                                  font=("Segoe UI", 8), fg="#7f8c8d", bg="#ffffff")
        self.shortcut_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add explain toggle checkbox
        self.explain_var = tk.BooleanVar()
        
        # Add custom prompt toggle checkbox
        self.custom_prompt_var = tk.BooleanVar()
        
        # Create a frame to hold the toggles side by side
        toggle_frame = Frame(self.frame, bg="#ffffff")
        toggle_frame.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)
        
        # Add explain toggle to the toggle frame
        self.explain_toggle = tk.Checkbutton(toggle_frame, text="Explain to me", 
                                           variable=self.explain_var, 
                                           font=("Segoe UI", 9), fg="#34495e", bg="#ffffff",
                                           activebackground="#ffffff", activeforeground="#3498db")
        self.explain_toggle.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add custom prompt toggle to the toggle frame
        self.custom_prompt_toggle = tk.Checkbutton(toggle_frame, text="Custom Prompt", 
                                           variable=self.custom_prompt_var, 
                                           font=("Segoe UI", 9), fg="#34495e", bg="#ffffff",
                                           activebackground="#ffffff", activeforeground="#3498db")
        self.custom_prompt_toggle.pack(side=tk.LEFT)
        
        # Create a container for the text field with a border
        self.text_container = Frame(self.frame, bg="#e0e0e0", padx=2, pady=2, 
                                   highlightbackground="#3498db", highlightthickness=1)
        self.text_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame to hold the text field and scrollbar side by side
        self.text_scroll_frame = Frame(self.text_container, bg="#ffffff")
        self.text_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the multi-line text input field with padding on the right for scrollbar
        self.input_field = Text(self.text_scroll_frame, font=("Segoe UI", 11), bg="#ffffff", 
                               fg="#34495e", insertbackground="#3498db",
                               relief=tk.FLAT, wrap=tk.WORD, height=10,  # Increase text field height
                               padx=8, pady=8)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame for the custom scrollbar with padding
        self.scrollbar_frame = Frame(self.text_scroll_frame, bg="#ffffff", width=16)
        self.scrollbar_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4))
        
        # Add a modern scrollbar with rounded style
        scrollbar = ttk.Scrollbar(self.scrollbar_frame, 
                             style="rounded.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_field.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.input_field.yview)
        
        # Bind keyboard events
        self.input_field.bind("<Control-Return>", self.on_ctrl_enter_pressed)
        self.input_field.bind("<Escape>", self.hide_input)
        
        # Add a small label to indicate how to submit with improved styling
        self.hint_label = Label(self.frame, text="Press Ctrl+Enter to submit or Esc to cancel", 
                              font=("Segoe UI", 9), fg="#7f8c8d", bg="#ffffff")
        self.hint_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Make the window draggable
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        
        # Hide the window initially
        self.input_window.withdraw()
        self.last_position = None  # Add variable to store last position
    
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
        
        # Use the canvas that was passed as 'self'
        if hasattr(self, 'create_polygon'):
            # When called directly on a canvas
            return self.create_polygon(points, **kwargs, smooth=True)
        else:
            # When called from the QuickInputApp instance
            return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def start_move(self, event):
        """Start window dragging"""
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        """Stop window dragging"""
        self.x = None
        self.y = None
    
    def do_move(self, event):
        """Move the window while dragging"""
        if self.x is None or self.y is None:
            return
            
        deltax = event.x - self.x
        deltay = event.y - self.y
        
        x = self.input_window.winfo_x() + deltax
        y = self.input_window.winfo_y() + deltay
        
        self.input_window.geometry(f"+{x}+{y}")
    
    def setup_tray_icon(self):
        """Set up the system tray icon with a menu"""
        icon_image = create_tray_icon_image()
        
        # Create the menu items
        menu = (
            pystray.MenuItem('Quick Input App', None, enabled=False),
            pystray.MenuItem('Service Status', None, enabled=False),
            pystray.MenuItem('Running', lambda: None, checked=lambda item: self.service_running),
            pystray.MenuItem('Start Service', self.start_service, enabled=lambda item: not self.service_running),
            pystray.MenuItem('Stop Service', self.stop_service, enabled=lambda item: self.service_running),
            pystray.MenuItem('Show Input', self.show_input, enabled=lambda item: self.service_running),
            pystray.MenuItem('Tips Options', pystray.Menu(
                pystray.MenuItem('Enable Tips', self.enable_tips, enabled=lambda item: not self.tips_enabled),
                pystray.MenuItem('Disable Tips', self.disable_tips, enabled=lambda item: self.tips_enabled),
                pystray.MenuItem('Set Interval', pystray.Menu(
                    pystray.MenuItem('1 minute', self.set_interval_1min, checked=lambda item: self.current_interval_key == "1min"),
                    pystray.MenuItem('3 minutes', self.set_interval_3min, checked=lambda item: self.current_interval_key == "3min"),
                    pystray.MenuItem('5 minutes', self.set_interval_5min, checked=lambda item: self.current_interval_key == "5min"),
                    pystray.MenuItem('10 minutes', self.set_interval_10min, checked=lambda item: self.current_interval_key == "10min")
                )),
                pystray.MenuItem('Show Latest Tip', lambda: show_latest_tips.show_latest_tips(self))
            )),
            pystray.MenuItem('Donate', self.show_donate_window),
            pystray.MenuItem('Quit', self.quit_app)
        )
        
        # Create the icon
        self.icon = pystray.Icon("quick_input", icon_image, "Fix My Eng", menu)
        
        # Run the icon in a separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def register_hotkey(self):
        """Register the global hotkey based on service status"""
        if self.service_running:
            try:
                keyboard.add_hotkey('ctrl+alt+space', self.toggle_input_field)
            except Exception as e:
                print(f"Error registering hotkey: {e}")
        else:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception as e:
                print(f"Error unregistering hotkeys: {e}")
    
    def start_service(self):
        """Start the service to enable hotkey functionality"""
        if not self.service_running:
            self.service_running = True
            self.register_hotkey()
            # Update the icon menu to reflect the new state
            self.icon.update_menu()
    
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
        window_height = 250  # Match the new height
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        if self.last_position:
            self.input_window.geometry(f"+{self.last_position[0]}+{self.last_position[1]}")  # Restore last position
        else:
            self.input_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Clear previous input and show the window
        self.input_field.delete("1.0", tk.END)  # Clear text from line 1, character 0 to end
        self.input_window.deiconify()
        
        # Apply a fade-in effect
        for alpha in range(0, 96, 5):  # 0 to 95% in steps of 5%
            self.input_window.attributes("-alpha", alpha/100)
            self.input_window.update()
            self.input_window.after(10)  # Short delay for animation
        
        # Enhanced focus handling
        self.input_window.update_idletasks()  # Process all pending events
        self.input_field.focus_force()  # Force focus to the text field
        self.input_window.lift()  # Ensure window is on top
        
        # Place cursor at the beginning of the text field
        self.input_field.mark_set("insert", "1.0")
        
        self.input_visible = True
    
    def hide_input(self, event=None):
        """Hide the input field"""
        # Store position before hiding
        self.last_position = (self.input_window.winfo_x(), self.input_window.winfo_y())
        
        # Apply a fade-out effect
        for alpha in range(95, -1, -5):  # 95% to 0% in steps of 5%
            self.input_window.attributes("-alpha", alpha/100)
            self.input_window.update()
            self.input_window.after(10)  # Short delay for animation
            
        self.input_window.withdraw()
        self.input_visible = False
    
    def on_ctrl_enter_pressed(self, event):
        """Handle when Ctrl+Enter is pressed in the input field"""
        self.input_value = self.input_field.get("1.0", tk.END).strip()  # Get all text from line 1, character 0 to end
        
        # Hide the input window first
        self.hide_input()
        
        # Give a small delay to allow the window to close and focus to return to the previous application
        if self.custom_prompt_var.get():
            # If custom prompt toggle is active, execute the custom prompt
            self.root.after(300, self.execute_custom_prompt)
        elif self.explain_var.get():
            # If explain toggle is active, show explanation
            self.root.after(300, self.explain_text)
        else:
            # Otherwise, auto-type the corrected text
            self.root.after(300, self.auto_type_text)
    
    def auto_type_text(self):
        """Auto-type the corrected text"""
        if not self.input_value.strip():
            return  # Don't type anything if the input was empty
        
        try:
            # Use a more explicit prompt structure to avoid confusion with user input
            prompt = f"""TASK: Fix the English text below.
INSTRUCTIONS: 
- Improve grammar and spelling
- Make it sound natural for casual business communication
- Maintain the original meaning
- Only return the corrected text with no explanations

TEXT TO FIX:
{self.input_value}

Remember to ONLY return the corrected version of the text above, nothing else."""
            
            # Log the prompt being sent
            logging.info(f"Sending correction prompt to Gemini API: {self.input_value[:100]}...")
            
            # Generate response with direct prompt
            response = self.model.generate_content(prompt)
            
            # Log the response received
            logging.info(f"Received correction response from Gemini API: {response.text[:100]}...")
            
            # Extract the content from the response
            corrected_text = response.text.strip().replace('"', '').replace('\n', ' ')
            
            # Use pyautogui to type the text
            # We use write instead of typewrite to handle special characters better
            pyautogui.write(corrected_text)
            
            # Increment correction count
            self.increment_correction_count()
        except Exception as e:
            logging.error(f"Error auto-typing text: {str(e)}")
            messagebox.showerror('Error', f'Failed to generate text: {str(e)}')
    
    def keyboard_listener(self):
        """Thread function to listen for keyboard events"""
        while self.running:
            # This thread keeps running to ensure keyboard events are processed
            # The actual hotkey handling is done by the keyboard library
            threading.Event().wait(0.1)
    
    def quit_app(self):
        """Quit the application completely"""
        self.running = False
        
        # Clean up tips timer
        if self.tips_timer:
            self.root.after_cancel(self.tips_timer)
            self.tips_timer = None
        
        # Close any open tip window
        self.close_tip_window()
        
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
            # Show loading window
            loading_window = LoadingWindow(self.root)
            loading_window.update_status("Initializing application...")
            self.root.update()
            
            # Simulate loading tasks
            loading_window.update_status("Loading configuration...")
            time.sleep(0.5)
            self.root.update()
            
            loading_window.update_status("Setting up API connection...")
            time.sleep(0.5)
            self.root.update()
            
            loading_window.update_status("Preparing user interface...")
            time.sleep(0.5)
            self.root.update()
            
            # Close loading window
            loading_window.close()
            
            # Show notification window with instructions
            NotificationWindow(self.root)
        
            # Start the main application
            self.root.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.running = False
            keyboard.unhook_all()  # Clean up keyboard hooks
    
    def configure_scrollbar_style(self):
        """Configure custom scrollbar style to match the modern look"""
        style = ttk.Style()
        
        # Configure the scrollbar style
        style.configure("rounded.Vertical.TScrollbar", 
                      background="#3498db",  # Scrollbar color - bright blue
                      troughcolor="#f0f0f0",  # Background color - light gray
                      borderwidth=0, 
                      arrowsize=0,  # No arrows
                      relief="flat")
        
        # Define element layouts - remove default arrows
        style.layout("rounded.Vertical.TScrollbar", 
                   [('Vertical.Scrollbar.trough',
                     {'sticky': 'ns', 'children':
                      [('Vertical.Scrollbar.thumb', 
                        {'expand': '1', 'sticky': 'nswe'})
                      ]})])
        
        # Make the scrollbar rounded and thinner
        style.configure("rounded.Vertical.TScrollbar", 
                      gripcount=0,
                      width=6,  # Make it thinner to match image
                      background="#3498db",
                      troughcolor="#f0f0f0",
                      bordercolor="#f0f0f0",
                      lightcolor="#3498db",
                      darkcolor="#2980b9",
                      borderwidth=0)
    
    def setup_tips_feature(self):
        """Initialize the tips feature timer"""
        if self.tips_enabled and self.tips_timer is None:
            # Start the timer to show tips every 5 minutes
            self.show_tip()  # Show first tip immediately
            self.schedule_next_tip()
        elif not self.tips_enabled and self.tips_timer is not None:
            # Cancel the timer if tips are disabled
            self.root.after_cancel(self.tips_timer)
            self.tips_timer = None
    
    def schedule_next_tip(self):
        """Schedule the next tip to be shown"""
        if self.tips_timer is not None:
            self.root.after_cancel(self.tips_timer)
        self.tips_timer = self.root.after(self.tips_interval, self.show_tip)
    
    def show_tip(self):
        """Show a tip in a popup window"""
        if not self.tips_enabled:
            return
            
        # Get a tip from Gemini AI
        tip = self.get_english_tip()
        if not tip:
            # If we couldn't get a tip, try again later
            self.schedule_next_tip()
            return
            
        # Store the latest tip
        self.latest_tip = tip
            
        # Close existing tips window if it exists
        self.close_tip_window(force_close=True)

        # Create new tips window
        self.tips_window = tk.Toplevel(self.root)
        self.tips_window.overrideredirect(True)  # Remove window border
        self.tips_window.attributes("-topmost", True)  # Always on top
        
        # Variables for mouse tracking
        self.mouse_over_tips = False
        self.close_timer_id = None
        
        # Position the window in the top right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 300  # Increased height for longer tips
        x_position = screen_width - window_width - 20
        y_position = 40
        self.tips_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Create a canvas for rounded rectangle background
        canvas = tk.Canvas(self.tips_window, bg="#3498db", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add the create_rounded_rectangle method to this canvas
        canvas.create_rounded_rectangle = lambda *args, **kwargs: self._create_rounded_rectangle(canvas, *args, **kwargs)
        
        # Draw rounded rectangle on canvas
        radius = 15
        canvas.create_rounded_rectangle(
            3, 3, window_width-3, window_height-3, radius, 
            fill="#ffffff", outline="#3498db", width=2
        )
        
        # Create a frame inside the rounded rectangle
        frame = Frame(canvas, bg="#ffffff")
        frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Add a title
        title_label = Label(frame, text="English Speaking Tip", font=("Segoe UI", 12, "bold"), 
                           bg="#ffffff", fg="#3498db")
        title_label.pack(pady=(10, 5), anchor="w")
        
        # Create a frame for the scrollable content
        content_frame = Frame(frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, pady=5)
        
        # Add a scrollable text widget for the tip
        tip_text = Text(content_frame, font=("Segoe UI", 10), bg="#ffffff", fg="#34495e",
                       wrap="word", height=10, borderwidth=0, highlightthickness=0)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", style="rounded.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tip_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tip_text.yview)
        
        # Pack the text widget
        tip_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Insert the tip text and make it read-only
        tip_text.insert("1.0", tip)
        tip_text.config(state="disabled")  # Make it read-only
        
        # Add close button
        close_button = Label(frame, text="×", font=("Segoe UI", 16, "bold"), 
                            bg="#ffffff", fg="#e74c3c", cursor="hand2")
        close_button.place(relx=1.0, rely=0.0, anchor="ne")
        close_button.bind("<Button-1>", lambda e: self.close_tip_window(force_close=True))
        
        # Bind mouse enter and leave events to track when mouse is over the window
        self.tips_window.bind("<Enter>", self.on_mouse_enter_tips)
        self.tips_window.bind("<Leave>", self.on_mouse_leave_tips)
        
        # Start the auto-close timer
        self.reset_close_timer()
        
        # Schedule the next tip
        self.schedule_next_tip()
    
    def on_mouse_enter_tips(self, event):
        """Called when mouse enters the tips window"""
        self.mouse_over_tips = True
        # Cancel the close timer if it's running
        if self.close_timer_id:
            self.tips_window.after_cancel(self.close_timer_id)
            self.close_timer_id = None
    
    def on_mouse_leave_tips(self, event):
        """Called when mouse leaves the tips window"""
        self.mouse_over_tips = False
        # Start the close timer
        self.reset_close_timer()
    
    def reset_close_timer(self):
        """Reset the timer that closes the tips window"""
        if self.close_timer_id:
            self.tips_window.after_cancel(self.close_timer_id)
        
        # Set a new timer to close the window after 10 seconds
        self.close_timer_id = self.tips_window.after(10000, self.close_tip_window)
    
    def close_tip_window(self, force_close=False):
        """Close the tip window if it exists and mouse is not over it"""
        if self.tips_window:
            # Force close or only close if mouse is not over the window
            if force_close or not self.mouse_over_tips:
                # Cancel any pending close timer
                if self.close_timer_id:
                    self.tips_window.after_cancel(self.close_timer_id)
                    self.close_timer_id = None
                
                # Destroy the window and reset the reference
                self.tips_window.destroy()
                self.tips_window = None
            else:
                # If mouse is still over window, reset the timer
                self.reset_close_timer()
    
    def get_english_tip(self):
        """Get an English speaking tip from Gemini AI"""
        try:
            prompt = """
Provide a brief tip (but not too short) on writing and speaking professionally in English. Explain in Indonesian, and show examples of incorrect (in English) and correct (in professional English) usage. Keep the number of characters of your response maximum in 400 characters. And also, Use the response template as below: 

Incorrect Example: 
\"incorrect profesional English example\" (meaning in Indonesian here)

Correct Example: 
\"correct profesional English example\" (meaning in Indonesian here)

Explanation: 
\"explanation in Indonesian language why the correct profesional English example is suitable for professional communication\".
"""            
            # Log the prompt being sent
            logging.info("Sending tip generation prompt to Gemini API")
            
            response = self.model.generate_content(prompt)
            
            # Log the response received
            logging.info(f"Received tip response from Gemini API: {response.text[:100]}...")
            
            # Extract the content from the response
            if response and hasattr(response, 'text'):
                # Convert markdown to plain text
                return self.markdown_to_plain_text(response.text.strip())
            return "Failed to generate tip. Please try again later."
        except Exception as e:
            logging.error(f"Error generating tip: {str(e)}")
            return None
    
    def markdown_to_plain_text(self, markdown_text):
        """Convert markdown text to plain text"""
        # Remove headers (# Header)
        text = re.sub(r'#+\s+(.*)', r'\1', markdown_text)
        
        # Remove bold (**text**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove italic (*text*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove code blocks (```code```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # Remove inline code (`code`)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove bullet points (- item)
        text = re.sub(r'^\s*[-*+]\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
        
        # Remove numbered lists (1. item)
        text = re.sub(r'^\s*\d+\.\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
        
        # Remove horizontal rules (---, ___, ***)
        text = re.sub(r'^\s*[-_*]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # Remove links ([text](url))
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def enable_tips(self):
        """Enable the tips feature"""
        self.tips_enabled = True
        # Use the current interval
        self.tips_interval = self.tips_intervals[self.current_interval_key]
        self.setup_tips_feature()
        self.icon.update_menu()
    
    def disable_tips(self):
        """Disable the tips feature"""
        self.tips_enabled = False
        self.setup_tips_feature()
        if self.tips_window:
            self.close_tip_window()
        self.icon.update_menu()
        
    def set_tips_interval(self, interval_key):
        """Set the tips interval to the specified key"""
        if interval_key in self.tips_intervals:
            self.current_interval_key = interval_key
            self.tips_interval = self.tips_intervals[interval_key]
            # If tips are enabled, restart the timer with the new interval
            if self.tips_enabled:
                self.schedule_next_tip()
            self.icon.update_menu()
    
    def set_interval_1min(self):
        """Set tips interval to 1 minute"""
        self.set_tips_interval("1min")
        
    def set_interval_3min(self):
        """Set tips interval to 3 minutes"""
        self.set_tips_interval("3min")
        
    def set_interval_5min(self):
        """Set tips interval to 5 minutes"""
        self.set_tips_interval("5min")
        
    def set_interval_10min(self):
        """Set tips interval to 10 minutes"""
        self.set_tips_interval("10min")
    
    def encrypt_api_key(self, api_key):
        """Encrypt the API key using AES encryption"""
        try:
            # Convert the encryption key to bytes
            encryption_key = "FixMyEnglish$$".encode('utf-8')
            # Pad the encryption key to be 16, 24, or 32 bytes long (AES requirement)
            encryption_key = encryption_key.ljust(32)[:32]
            
            # Create a new AES cipher
            cipher = AES.new(encryption_key, AES.MODE_CBC)
            
            # Pad the data and encrypt it
            ct_bytes = cipher.encrypt(pad(api_key.encode('utf-8'), AES.block_size))
            
            # Get the initialization vector
            iv = cipher.iv
            
            # Combine IV and ciphertext and encode as base64
            encrypted_data = base64.b64encode(iv + ct_bytes).decode('utf-8')
            
            return encrypted_data
        except Exception as e:
            logging.error(f"Error encrypting API key: {str(e)}")
            return None

    def decrypt_api_key(self, encrypted_data):
        """Decrypt the API key using AES encryption"""
        try:
            # Convert the encryption key to bytes
            encryption_key = "FixMyEnglish$$".encode('utf-8')
            # Pad the encryption key to be 16, 24, or 32 bytes long (AES requirement)
            encryption_key = encryption_key.ljust(32)[:32]
            
            # Decode the base64 data
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract the IV (first 16 bytes)
            iv = encrypted_bytes[:16]
            ct = encrypted_bytes[16:]
            
            # Create a new AES cipher with the extracted IV
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            
            # Decrypt and unpad the data
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            
            return pt.decode('utf-8')
        except Exception as e:
            logging.error(f"Error decrypting API key: {str(e)}")
            return None

   
    def setup_api_key(self):
        """Set up the Google Gemini API key"""
        if "GOOGLE_API_KEY" not in os.environ:
            # Check if api.key file exists
            if not os.path.exists('api.key'):
                # If file doesn't exist, show the API key input dialog
                if not self.show_api_key_dialog():
                    # If the user didn't provide a key, exit the application
                    return False
                return self.api_key_saved
            
            try:
                # Read the encrypted API key from the file
                with open('api.key', 'r') as f:
                    encrypted_key = f.read().strip()
                    if not encrypted_key:
                        # If file is empty, show the API key input dialog
                        if not self.show_api_key_dialog():
                            # If the user didn't provide a key, exit the application
                            return False
                        return self.api_key_saved
                    
                    # Decrypt the API key
                    api_key = self.decrypt_api_key(encrypted_key)
                    if not api_key:
                        # If decryption fails, show the API key input dialog
                        messagebox.showerror('Error', 'Failed to decrypt API key! Please enter a new one.')
                        if not self.show_api_key_dialog():
                            # If the user didn't provide a key, exit the application
                            return False
                        return self.api_key_saved
                    
                    # Set the API key in the environment
                    os.environ["GOOGLE_API_KEY"] = api_key
            except Exception as e:
                logging.error(f"Failed to read api.key: {str(e)}")
                messagebox.showerror('Error', f'Failed to read api.key: {str(e)}')
                if not self.show_api_key_dialog():
                    # If the user didn't provide a key, exit the application
                    return False
                return self.api_key_saved
        
        # Initialize the model
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        return True

    def exit_application(self):
        """Exit the application gracefully"""
        logging.info("Exiting application")
        try:
            # Clean up resources
            if hasattr(self, 'icon') and self.icon:
                self.icon.stop()
            
            # Destroy the root window
            if hasattr(self, 'root') and self.root:
                self.root.destroy()
            
            # Exit the application
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error during exit: {str(e)}")
            sys.exit(1)

    def execute_custom_prompt(self):
        """Execute a custom prompt directly with Gemini"""
        if not self.input_value.strip():
            return  # Don't do anything if the input was empty
        
        try:
            # Add a brief instruction to keep the response concise
            prompt = f"""TASK: Execute the following prompt and keep your response brief with no further explanation and only have single option as output.

PROMPT:
{self.input_value}

Remember to be concise and direct in your response."""
            
            # Log the custom prompt being sent
            logging.info(f"Sending custom prompt to Gemini API: {self.input_value[:100]}...")
            
            # Generate response with direct prompt
            response = self.model.generate_content(prompt)
            
            # Log the response received
            logging.info(f"Received custom prompt response from Gemini API: {response.text[:100]}...")
            
            # Extract the content from the response
            result = response.text.strip()
            
            if self.explain_var.get():
                # If explain is also toggled, show the result in a notification window
                show_explanation_window(self, result)
            else:
                # Otherwise, auto-type the result
                pyautogui.write(result)
                
        except Exception as e:
            logging.error(f"Error executing custom prompt: {str(e)}")
            messagebox.showerror('Error', f'Failed to execute custom prompt: {str(e)}')
    
    def explain_text(self):
        """Show explanation of text in Indonesian"""
        if not self.input_value.strip():
            return  # Don't explain anything if the input was empty
        
        try:
            # Use a specific prompt for Indonesian explanation
            prompt = f"""TASK: Transform the English text below into Indonesian and provide an explanation in Indonesian based on the instructions below.
INSTRUCTIONS: 
- Analyze the English text provided
- Please ensure that the explanation is entirely in Indonesian.
- Provide helpful context or clarification while keeping it brief
- Make sure the Indonesian explanation is natural and easy to understand

TEXT TO transform and explain:
{self.input_value}

Remember to only provide the explanation in Indonesian without any extra text afterwards."""
            
            # Log the explanation prompt being sent
            logging.info(f"Sending explanation prompt to Gemini API: {self.input_value[:100]}...")
            
            # Generate response with direct prompt
            response = self.model.generate_content(prompt)
            
            # Log the response received
            logging.info(f"Received explanation response from Gemini API: {response.text[:100]}...")
            
            # Extract the content from the response
            explanation = response.text.strip()
            
            # Create notification window with explanation
            show_explanation_window(self, explanation)
            
        except Exception as e:
            logging.error(f"Error explaining text: {str(e)}")
            print(f"Error explaining text: {e}")
    
      
    def _start_dragging(self, event, window):
        """Start dragging a window"""
        self._drag_x = event.x
        self._drag_y = event.y
        
    def _stop_dragging(self, event):
        """Stop dragging a window"""
        self._drag_x = None
        self._drag_y = None
        
    def _do_dragging(self, event, window):
        """Move the window while dragging"""
        if self._drag_x is None or self._drag_y is None:
            return
            
        deltax = event.x - self._drag_x
        deltay = event.y - self._drag_y
        
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        
        window.geometry(f"+{x}+{y}")
    
    def show_donate_window(self):
        """Show the donation window"""
        from donate_window import show_donate_window
        self.donate_window, _ = show_donate_window()
    
    def _load_correction_count(self):
        """Load the correction count from encrypted storage"""
        if os.path.exists('ctx.dll'):
            try:
                with open('ctx.dll', 'r') as f:
                    encrypted_count_b64 = f.read()
                decrypted = self.decrypt_api_key(encrypted_count_b64)
                if decrypted:
                    return int(decrypted)
                return 0
            except Exception as e:
                logging.error(f"Error loading correction count: {str(e)}")
                return 0
        return 0

    def _save_correction_count(self):
        """Save the correction count to encrypted storage"""
        try:
            count_str = str(self.correction_count)
            encrypted = self.encrypt_api_key(count_str)
            if encrypted:
                with open('ctx.dll', 'w') as f:
                    f.write(encrypted)
        except Exception as e:
            logging.error(f"Error saving correction count: {str(e)}")
    
    def increment_correction_count(self):
        """Increment correction count and show donation window if needed"""
        self.correction_count += 1
        self._save_correction_count()
        if self.correction_count % 2 == 0:
            self.show_donate_window()
    
    def correct_text(self, text):
        # Add your text correction logic here
        corrected_text = text  # Replace with actual correction logic
        if corrected_text and corrected_text != text:
            self.increment_correction_count()
        return corrected_text
    
    def replace_text(self, text):
        # Add your text replacement logic here
        success = True  # Replace with actual replacement logic
        if success:
            self.increment_correction_count()
        return success
    
    def auto_replace_text(self, text):
        # Add your auto text replacement logic here
        success = True  # Replace with actual replacement logic
        if success:
            self.increment_correction_count()
        return success
    
if __name__ == "__main__":
    app = QuickInputApp()
    app.run()