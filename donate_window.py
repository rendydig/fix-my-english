from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QUrl, Signal, QObject
import sys
import os
import logging
from donation_page_html import DONATION_PAGE_HTML

# Set Chromium flags to suppress SSL errors and disable web security for redirections
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3 --ignore-certificate-errors --disable-web-security"

class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts URL requests to handle them properly"""
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        logging.info(f"Intercepted URL request: {url}")
        # We don't block any requests, just log them

class DonateWebPage(QWebEnginePage):
    """Custom web page that ignores SSL certificate errors and handles navigation"""
    navigationRequested = Signal(QUrl)
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.navigationRequested.connect(self.handleNavigation)
        
    def certificateError(self, error):
        # Accept all certificates to bypass SSL errors
        logging.info(f"Ignoring certificate error: {error.errorDescription()}")
        # For Qt6, we need to use the correct method to ignore certificate errors
        try:
            error.ignoreCertificateError()
            return True
        except AttributeError:
            # Fallback for different PySide6 versions
            logging.warning("Using alternative method to ignore certificate error")
            return True
        
    def javaScriptConsoleMessage(self, level, message, line, source):
        # Log JavaScript console messages but don't show them to the user
        logging.info(f"JavaScript Console ({source}:{line}): {message}")
    
    def acceptNavigationRequest(self, url, type, isMainFrame):
        # Emit signal when navigation is requested
        if isMainFrame:
            self.navigationRequested.emit(url)
            logging.info(f"Navigation requested to: {url.toString()}")
        return True
    
    def handleNavigation(self, url):
        # Handle navigation to external URLs
        url_string = url.toString()
        if url_string.startswith("https://") and not url_string.startswith("file://"):
            logging.info(f"External URL navigation: {url_string}")
            # We'll let the navigation proceed, but log it

class DonateWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Support Our Project')
        self.setMinimumSize(360, 600)

        # Create custom web profile with SSL error handling
        self.profile = QWebEngineProfile("DonateProfile")
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Set user agent to a modern browser to improve compatibility
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Add URL request interceptor
        self.interceptor = UrlRequestInterceptor()
        self.profile.setUrlRequestInterceptor(self.interceptor)
        
        # Configure profile settings
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        
        # Additional settings to enable loading content from HTTPS
        # Note: WebSecurityEnabled is not available in this version of PySide6
        # Using alternative settings to achieve the same goal
        
        # Create web view with custom page
        self.web_view = QWebEngineView()
        self.web_page = DonateWebPage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Connect to page signals
        self.web_page.navigationRequested.connect(self.on_navigation_requested)
        
        # Load HTML content directly from the Python string
        self.web_view.setHtml(DONATION_PAGE_HTML, QUrl("file://"))

        # Set layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for cleaner look
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Apply window styling
        self.setStyleSheet('''
            QMainWindow {
                background-color: #ffffff;
                border-radius: 8px;
            }
            QWebEngineView {
                border: none;
            }
        ''')
    
    def on_navigation_requested(self, url):
        """Handle navigation requests from the web page"""
        url_string = url.toString()
        logging.info(f"Navigation requested to: {url_string}")
        
        # For external URLs, we can choose to open in system browser instead
        # But for now, we'll let the web view handle it
        if url_string.startswith("https://trakteer.id"):
            logging.info("Allowing navigation to donation site")
            # We could use QDesktopServices.openUrl(url) to open in system browser
            # But we'll let the web view handle it for now

def show_donate_window():
    """Create and show a standalone donation window"""
    # Check if QApplication instance exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    window = DonateWindow()
    window.show()
    return window, app

def create_qt_conf():
    """Create qt.conf file to handle DPI awareness settings"""
    qt_conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qt.conf')
    
    # Check if file already exists
    if not os.path.exists(qt_conf_path):
        with open(qt_conf_path, 'w') as f:
            f.write("[Platforms]\n")
            f.write("WindowsArguments = dpiawareness=0\n")
        logging.info(f"Created qt.conf at {qt_conf_path}")
    
    return qt_conf_path

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create qt.conf file for DPI handling
    create_qt_conf()
    
    # For testing the window standalone
    window, app = show_donate_window()
    sys.exit(app.exec())
