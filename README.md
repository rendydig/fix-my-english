# Quick Input Application

A simple Windows application that provides a quick multi-line text input field when you press CTRL+ALT+SPACE, and automatically types the entered text when submitted.

## Features

- Press CTRL+ALT+SPACE to show a multi-line text input field in the middle of the screen
- Submit text by pressing CTRL+ENTER to automatically type the text in your active application
- Press ESC to cancel and hide the input field without typing anything
- System tray icon with menu options:
  - Start Service: Enable the CTRL+ALT+SPACE hotkey
  - Stop Service: Disable the CTRL+ALT+SPACE hotkey
  - Show Input: Manually show the input field
  - Quit: Exit the application

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS and Linux
   ```
## Usage

1. Run the application:
   ```
   python main.py
   ```
   or use the provided batch file:
   ```
   run_app.bat
   ```
2. The application will start and show a system tray icon
3. Click or focus on the application where you want the text to be typed
4. Press CTRL+ALT+SPACE to show the multi-line input field
5. Type your text (supports multiple lines)
6. Press CTRL+ENTER to submit - the input window will close and the text will be automatically typed in your active application
7. Press Escape to cancel and hide the input field without typing anything

## Requirements

- keyboard
- pyautogui
- pywin32
- pystray
- Pillow
