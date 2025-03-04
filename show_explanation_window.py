
import tkinter as tk
from tkinter import Frame, Text, Label,ttk

def show_explanation_window(main_app, explanation_text):
        """Show a notification window with the explanation"""
        # Create a new window
        explanation_window = tk.Toplevel(main_app.root)
        explanation_window.title("Explanation")
        explanation_window.overrideredirect(True)  # Remove window border
        explanation_window.attributes("-topmost", True)  # Always on top
        
        # Set window size and position
        window_width = 450
        window_height = 350
        screen_width = main_app.root.winfo_screenwidth()
        screen_height = main_app.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        explanation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Create a canvas for rounded rectangle background
        canvas = tk.Canvas(explanation_window, bg="#3498db", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add the create_rounded_rectangle method to this canvas
        canvas.create_rounded_rectangle = lambda *args, **kwargs: main_app._create_rounded_rectangle(canvas, *args, **kwargs)
        
        # Draw rounded rectangle
        radius = 15
        canvas.create_rounded_rectangle(
            3, 3, window_width-3, window_height-3, radius, 
            fill="#ffffff", outline="#3498db", width=2
        )
        
        # Add title
        title_label = Label(canvas, text="Explanation", font=("Segoe UI", 14, "bold"), 
                          bg="#ffffff", fg="#3498db")
        title_label.place(relx=0.5, rely=0.12, anchor="center")
        
        # Create a frame for the scrollable content
        content_frame = Frame(canvas, bg="#ffffff")
        content_frame.place(relx=0.5, rely=0.45, anchor="center", width=window_width-40, height=window_height-160)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", style="rounded.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add text widget for the explanation
        explanation_text_widget = Text(content_frame, font=("Segoe UI", 10), 
                                     bg="#ffffff", fg="#34495e", wrap=tk.WORD,
                                     yscrollcommand=scrollbar.set)
        explanation_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=explanation_text_widget.yview)
        
        # Insert the explanation
        explanation_text_widget.insert(tk.END, explanation_text)
        explanation_text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Add close button
        close_button = Label(canvas, text="×", font=("Segoe UI", 16, "bold"), 
                           bg="#ffffff", fg="#e74c3c", cursor="hand2")
        close_button.place(relx=0.95, rely=0.05, anchor="ne")
        close_button.bind("<Button-1>", lambda e: explanation_window.destroy())
        
        # Add "OK" button
        ok_button = tk.Button(canvas, text="OK", font=("Segoe UI", 10, "bold"),
                            bg="#3498db", fg="white", relief="flat", padx=15, pady=5,
                            command=explanation_window.destroy, cursor="hand2")
        ok_button.place(relx=0.5, rely=0.85, anchor="center")
        
        # Make window draggable
        canvas.bind("<ButtonPress-1>", lambda event: main_app._start_dragging(event, explanation_window))
        canvas.bind("<ButtonRelease-1>", lambda event: main_app._stop_dragging(event))
        canvas.bind("<B1-Motion>", lambda event: main_app._do_dragging(event, explanation_window))
     