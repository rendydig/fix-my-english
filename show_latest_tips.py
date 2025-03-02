import tkinter as tk
from tkinter import Frame, Text, Label, messagebox, Canvas
from tkinter import ttk
import google.generativeai as genai

def show_latest_tips(main_app):
        """Show the latest tip on demand"""
        if main_app.latest_tip:
            # Close any existing tip window
            main_app.close_tip_window()
            
            # Create a new tip window
            main_app.tips_window = tk.Toplevel(main_app.root)
            main_app.tips_window.overrideredirect(True)  # Remove window border
            main_app.tips_window.attributes("-topmost", True)  # Always on top
            
            # Variables for mouse tracking
            main_app.mouse_over_tips = False
            main_app.close_timer_id = None
            
            # Position the window in the top right corner
            screen_width = main_app.root.winfo_screenwidth()
            screen_height = main_app.root.winfo_screenheight()
            window_width = 400
            window_height = 300  # Increased height for longer tips
            x_position = screen_width - window_width - 20
            y_position = 40
            main_app.tips_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
            
            # Create a canvas for rounded rectangle background
            canvas = tk.Canvas(main_app.tips_window, bg="#3498db", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Add the create_rounded_rectangle method to this canvas
            canvas.create_rounded_rectangle = lambda *args, **kwargs: main_app._create_rounded_rectangle(canvas, *args, **kwargs)
            
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
            title_label = Label(frame, text="Latest English Speaking Tip", font=("Segoe UI", 12, "bold"), 
                               bg="#ffffff", fg="#3498db")
            title_label.pack(pady=(10, 5), anchor="w")
            
            # Create a frame for the scrollable content
            content_frame = Frame(frame, bg="#ffffff")
            content_frame.pack(fill="both", expand=True, pady=5)
            
            # Add a scrollable text widget for the tip
            tip_text = Text(content_frame, font=("Segoe UI", 10), bg="#ffffff", fg="#34495e",
                           wrap="word", height=10, borderwidth=0, highlightthickness=0)
            tip_text.insert("1.0", main_app.latest_tip)
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
            close_button.bind("<Button-1>", lambda e: main_app.close_tip_window(force_close=True))
            
            # Bind mouse enter and leave events to track when mouse is over the window
            main_app.tips_window.bind("<Enter>", main_app.on_mouse_enter_tips)
            main_app.tips_window.bind("<Leave>", main_app.on_mouse_leave_tips)
            
            # Set a timer to close the window after 10 seconds if mouse is not over it
            main_app.reset_close_timer()
        else:
            # If no tip is available, generate a new one and show it
            tip = main_app.get_english_tip()
            if tip:
                main_app.latest_tip = tip
                main_app.show_latest_tips()
            else:
                # Show a message if no tip could be generated
                messagebox.showinfo("No Tip Available", "No tip is currently available. Please try again later.")
