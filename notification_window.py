import tkinter as tk
from tkinter import Frame, Label, ttk
from tray_icon import create_tray_icon_image

class NotificationWindow:
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Welcome")
        self.root.overrideredirect(True)  # Remove window border
        self.root.attributes("-topmost", True)  # Always on top
        
        # Set window size and position
        window_width = 400
        window_height = 300
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
        
        # Add title
        self.title_label = Label(self.canvas, text="Welcome", 
                               font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#3498db")
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")
        
        # Add instructions
        instructions = [
            "• Tekan Ctrl+Alt+Space untuk membuka jendela input",
            "• Ketik atau copy/paste teks Anda untuk diperbaiki",
            "• tekan CTRL+ENTER untuk Submit",
            "• Teks yang sudah diperbaiki akan diketik secara otomatis",
            "• Tips bahasa Inggris akan muncul secara berkala",
            "• Akses lebih banyak opsi dari ikon baki sistem",
            "• Anda dapat menyeret jendela input ke posisi mana saja",
            "• Gunakan System tray (pojok kanan bawah) mengaktifkan/mematikan Auto-tips",
            "• Tips dapat dikonfigurasi untuk muncul pada interval yang berbeda"
        ]
        
        # Create a frame for the instructions with scrollbar
        instruction_container = Frame(self.canvas, bg="#ffffff")
        instruction_container.place(relx=0.5, rely=0.5, anchor="center", width=350, height=150)
        
        # Add scrollbar to the instruction container
        scrollbar = ttk.Scrollbar(instruction_container, orient="vertical", style="rounded.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a canvas inside the container for scrolling
        instruction_canvas = tk.Canvas(instruction_container, bg="#ffffff", 
                                     highlightthickness=0, yscrollcommand=scrollbar.set)
        instruction_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar to scroll the canvas
        scrollbar.config(command=instruction_canvas.yview)
        
        # Create a frame inside the canvas to hold the instruction labels
        instruction_frame = Frame(instruction_canvas, bg="#ffffff")
        instruction_canvas.create_window((0, 0), window=instruction_frame, anchor="nw")
        
        # Add each instruction line
        for i, instruction in enumerate(instructions):
            Label(instruction_frame, text=instruction, font=("Segoe UI", 10), 
                 bg="#ffffff", fg="#333333", anchor="w", justify="left", wraplength=320).pack(
                     pady=(5 if i == 0 else 2), padx=10, anchor="w")
        
        # Update the scrollregion when the frame size changes
        instruction_frame.update_idletasks()
        instruction_canvas.config(scrollregion=instruction_canvas.bbox("all"))
        
        # Enable mousewheel scrolling
        instruction_canvas.bind("<MouseWheel>", lambda e: instruction_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Store the canvas as an instance variable so we can access it in other methods
        self.instruction_canvas = instruction_canvas

        # Add close button
        self.close_button = Label(self.canvas, text="×", font=("Segoe UI", 16, "bold"), 
                                bg="#ffffff", fg="#e74c3c", cursor="hand2")
        self.close_button.place(relx=0.95, rely=0.05, anchor="ne")
        self.close_button.bind("<Button-1>", lambda e: self.close())
        
        # Add "OK, Got it!" button
        self.ok_button = tk.Button(self.canvas, text="OK, Got it!", font=("Segoe UI", 10, "bold"),
                                bg="#3498db", fg="white", relief="flat", padx=15, pady=5,
                                command=self.close, cursor="hand2")
        self.ok_button.place(relx=0.5, rely=0.85, anchor="center")
        
        # Make window draggable
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        
        self.x = 0
        self.y = 0
    
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
    
    def start_move(self, event):
        """Start window movement"""
        if event.widget != self.close_button and event.widget != self.ok_button:
            self.x = event.x
            self.y = event.y
    
    def stop_move(self, event):
        """Stop window movement"""
        self.x = None
        self.y = None
    
    def do_move(self, event):
        """Move the window"""
        if event.widget != self.close_button and event.widget != self.ok_button:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
    
    def close(self):
        """Close the notification window"""
        # Unbind the mousewheel event before closing to prevent errors
        if hasattr(self, 'instruction_canvas'):
            self.instruction_canvas.unbind("<MouseWheel>")
        self.root.destroy()

