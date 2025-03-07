import keyboard
import tkinter as tk
from tkinter import Frame, Text, Label, messagebox, Canvas
from tkinter import ttk
import threading
import pyautogui
import pystray
import os
import sys
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import re

class QuickInputApp:
    def __init__(self):
        # Initialize main variables
        self.input_visible = False
        self.input_value = ""
        self.service_running = True
        
        # Tips feature variables
        self.tips_enabled = False  # Disabled by default
        self.tips_timer = None
        self.tips_window = None
        self.tips_interval = 15 * 60 * 1000  # 5 minutes in milliseconds
        
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
        if "GOOGLE_API_KEY" not in os.environ:
            try:
                if not os.path.exists('api.key'):
                    messagebox.showerror('Error', 'api.key file not found! Please create the file with your Google API key.')
                    return
                
                with open('api.key', 'r') as f:
                    api_key = f.read().strip()
                    if not api_key:
                        messagebox.showerror('Error', 'api.key file is empty! Please add your Google API key to the file.')
                        return
                    
                os.environ["GOOGLE_API_KEY"] = api_key
            except Exception as e:
                messagebox.showerror('Error', f'Failed to read api.key: {str(e)}')
                return
        
        # Initialize the model
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Initialize the tips feature
        self.setup_tips_feature()
    
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
        icon_image = self.create_tray_icon_image()
        
        # Create the menu items
        menu = (
            pystray.MenuItem('Quick Input App', None, enabled=False),
            pystray.MenuItem('Service Status', None, enabled=False),
            pystray.MenuItem('Running', lambda: None, checked=lambda item: self.service_running),
            pystray.MenuItem('Start Service', self.start_service, enabled=lambda item: not self.service_running),
            pystray.MenuItem('Stop Service', self.stop_service, enabled=lambda item: self.service_running),
            pystray.MenuItem('Show Input', self.show_input, enabled=lambda item: self.service_running),
            pystray.MenuItem('Tips Options', pystray.Menu(
                pystray.MenuItem('Enable Tips (Every 15 min)', self.enable_tips, enabled=lambda item: not self.tips_enabled),
                pystray.MenuItem('Disable Tips', self.disable_tips, enabled=lambda item: self.tips_enabled)
            )),
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
        self.root.after(300, self.auto_type_text)
    
    def auto_type_text(self):
        """Auto-type the corrected text"""
        if not self.input_value.strip():
            return  # Don't type anything if the input was empty
        
        try:
            # Use a direct prompt approach instead of message chaining
            prompt = f"Improve this text to make it more suitable for casual business English. Correct any grammar or spelling errors, and make it sound natural but still professional. Respond ONLY with the improved version, without explanations or additional content. The text is: {self.input_value}"
            
            # Generate response with direct prompt
            response = self.model.generate_content(prompt)
            
            # Extract the content from the response
            corrected_text = response.text.strip().replace('"', '').replace('\n', ' ')
            
            # Use pyautogui to type the text
            # We use write instead of typewrite to handle special characters better
            pyautogui.write(corrected_text)
        except Exception as e:
            print(f"Error auto-typing text: {e}")
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
            self.root.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.running = False
            keyboard.unhook_all()  # Clean up keyboard hooks
    
    def create_tray_icon_image(self):
        """Create a modern icon for the system tray"""
        # Create a rounded square icon with gradient
        width = 64
        height = 64
        
        # Create base image with transparency
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a rounded rectangle
        radius = 15
        color1 = "#3498db"  # Start color - light blue
        color2 = "#2980b9"  # End color - darker blue
        
        # Draw the rounded rectangle (simulated with multiple rectangles and ellipses)
        dc.rectangle([radius, 0, width-radius, height], fill=color1)
        dc.rectangle([0, radius, width, height-radius], fill=color1)
        
        # Draw the four corners
        dc.ellipse([0, 0, radius*2, radius*2], fill=color1)
        dc.ellipse([width-radius*2, 0, width, radius*2], fill=color1)
        dc.ellipse([0, height-radius*2, radius*2, height], fill=color1)
        dc.ellipse([width-radius*2, height-radius*2, width, height], fill=color1)
        
        # Add a "F" letter in the center
        try:
            # Try to use a font if available
            font = ImageFont.truetype("arial.ttf", 32)
            text_width, text_height = dc.textsize("F", font=font)
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            dc.text((text_x, text_y), "F", fill="white", font=font)
        except:
            # Fallback to drawing a simple F shape
            margin = width // 4
            dc.line([margin, margin, margin, height-margin], fill="white", width=3)
            dc.line([margin, margin, width-margin, margin], fill="white", width=3)
            dc.line([margin, height//2, width-margin, height//2], fill="white", width=3)
        
        return image
    
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
            
        # Close any existing tip window
        self.close_tip_window()
        
        # Create a new tip window
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
        tip_text.insert("1.0", tip)
        tip_text.config(state="disabled")  # Make it read-only
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=tip_text.yview)
        tip_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and text widget
        scrollbar.pack(side="right", fill="y")
        tip_text.pack(side="left", fill="both", expand=True)
        
        # Add a close button
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
                try:
                    self.tips_window.destroy()
                    self.tips_window = None
                    self.close_timer_id = None
                except:
                    pass
            else:
                # If mouse is still over window, reset the timer
                self.reset_close_timer()
    
    def get_english_tip(self):
        """Get an English speaking tip from Gemini AI"""
        try:
            prompt = """
            create me single tips (but not too short), about how to be speak as professional in english, 
            give me an explanantion In indonesia Language , and show me the example.
            
            your response should be not more than 300 characters.
            """
            
            response = self.model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                # Convert markdown to plain text
                return self.markdown_to_plain_text(response.text.strip())
            return "Failed to generate tip. Please try again later."
        except Exception as e:
            print(f"Error generating tip: {e}")
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
        self.setup_tips_feature()
        self.icon.update_menu()
    
    def disable_tips(self):
        """Disable the tips feature"""
        self.tips_enabled = False
        self.setup_tips_feature()
        if self.tips_window:
            self.close_tip_window()
        self.icon.update_menu()

if __name__ == "__main__":
    app = QuickInputApp()
    app.run()