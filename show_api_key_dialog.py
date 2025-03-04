import tkinter as tk
from tkinter import Text, Label, messagebox
import os
import google.generativeai as genai

def show_api_key_dialog(main_app):
        """Show a dialog to input the Google Gemini API key"""
        # Create a new window
        api_window = tk.Toplevel(main_app.root)
        api_window.title("API Key Required")
        api_window.geometry("400x200")
        api_window.resizable(False, False)
        api_window.configure(bg="#ffffff")
        
        # Make the window appear on top
        api_window.attributes("-topmost", True)
        
        # Center the window on the screen
        window_width = 400
        window_height = 200
        screen_width = api_window.winfo_screenwidth()
        screen_height = api_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        api_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Add a label with instructions
        Label(api_window, text="Please enter your Google Gemini API Key:", 
              font=("Segoe UI", 11), bg="#ffffff", fg="#333333").pack(pady=(20, 10))
        
        # Add a text field for the API key
        api_entry = Text(api_window, height=1, width=40, font=("Segoe UI", 10),
                        relief="solid", bd=1)
        api_entry.pack(pady=(0, 20), padx=20)
        
        # Variable to track if the API key was saved successfully
        main_app.api_key_saved = False
        
        # Function to save the API key
        def save_api_key():
            api_key = api_entry.get("1.0", "end-1c").strip()
            if not api_key:
                messagebox.showerror("Error", "API Key cannot be empty!")
                return
            
            try:
                # Encrypt the API key
                encrypted_key = main_app.encrypt_api_key(api_key)
                if encrypted_key:
                    # Save the encrypted key to the file
                    with open('api.key', 'w') as f:
                        f.write(encrypted_key)
                    
                    # Set the API key in the environment
                    os.environ["GOOGLE_API_KEY"] = api_key
                    
                    # Initialize the model
                    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
                    main_app.model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    # Set the flag to indicate successful save
                    main_app.api_key_saved = True
                    
                    # Close the window
                    api_window.destroy()
                    
                    # Initialize the tips feature
                    main_app.setup_tips_feature()
                    
                    # Show success message
                    messagebox.showinfo("Success", "API Key saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to encrypt API key!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
        
        # Function to handle window close event
        def on_closing():
            if not main_app.api_key_saved:
                if messagebox.askokcancel("Quit", "API Key is required to run the application. Are you sure you want to quit?"):
                    api_window.destroy()
                    # Exit the application gracefully
                    main_app.exit_application()
            else:
                api_window.destroy()
        
        # Set the window close handler
        api_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Add a save button
        save_button = tk.Button(api_window, text="Save", font=("Segoe UI", 10, "bold"),
                              bg="#3498db", fg="white", relief="flat", padx=15, pady=5,
                              command=save_api_key, cursor="hand2")
        save_button.pack(pady=(0, 20))
        
        # Focus on the entry field
        api_entry.focus_set()
        
        # Wait for the window to be closed
        api_window.wait_window()
        
        # Return whether the API key was saved successfully
        return main_app.api_key_saved
