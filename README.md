# Quick Input Application

A simple Windows application that provides a quick multi-line text input field when you press CTRL+ALT+SPACE.

## Features

- Press CTRL+ALT+SPACE to show a multi-line text input field in the middle of the screen
- Submit text by pressing CTRL+ENTER
- Press ESC to cancel and hide the input field
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
3. Press CTRL+ALT+SPACE to show the multi-line input field
4. Type your text (supports multiple lines)
5. Press CTRL+ENTER to submit
6. Press Escape to cancel and hide the input field

## Requirements

- keyboard
- pyautogui
- pywin32
- pystray
- Pillow
