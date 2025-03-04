"""
Test script for the donation window to verify SSL certificate handling
"""
import sys
import logging
import os
from donate_window import show_donate_window, create_qt_conf

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('donate_window_test.log')
        ]
    )
    
    # Log test start
    logging.info("Starting donation window test")
    
    # Set Chromium flags to suppress SSL errors (redundant as it's also in donate_window.py, but ensures it's set)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3 --ignore-certificate-errors"
    logging.info("Set Chromium flags to ignore certificate errors")
    
    # Create qt.conf for DPI settings
    create_qt_conf()
    
    # Show donation window
    logging.info("Showing donation window")
    window, app = show_donate_window()
    
    # Log when window is shown
    logging.info("Donation window shown, waiting for user interaction")
    
    # Run the application
    sys.exit(app.exec_())
