import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QUrl, Signal, QObject

# Configure basic logging
logging.basicConfig(level=logging.INFO, 
                  format='%(asctime)s - %(levelname)s - %(message)s')

# Set Chromium flags to suppress SSL errors
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3 --ignore-certificate-errors --disable-web-security"

class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts URL requests to handle redirections properly"""
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        logging.info(f"Intercepted URL request: {url}")
        # Allow all requests to proceed, including redirections

class TestHttpsImagesPage(QWebEnginePage):
    """Custom web page that handles redirections and SSL errors"""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
    def certificateError(self, error):
        # Accept all certificates to bypass SSL errors
        logging.info(f"Ignoring certificate error: {error.errorDescription()}")
        try:
            error.ignoreCertificateError()
            return True
        except AttributeError:
            # Fallback for different PySide6 versions
            logging.warning("Using alternative method to ignore certificate error")
            return True
        
    def javaScriptConsoleMessage(self, level, message, line, source):
        # Log JavaScript console messages
        logging.info(f"JavaScript Console ({source}:{line}): {message}")

class TestHttpsImagesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Test HTTPS Images')
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add a label with instructions
        label = QLabel("Testing HTTPS image loading in QWebEngineView")
        layout.addWidget(label)
        
        # Create custom web profile with interceptor
        self.profile = QWebEngineProfile("TestProfile")
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
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
        
        # Create web view with custom page
        self.web_view = QWebEngineView()
        self.web_page = TestHttpsImagesPage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Create HTML with HTTPS images
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'self' https: http:; img-src * data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';">
            <title>HTTPS Image Test</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                img { max-width: 100%; height: auto; margin: 10px 0; border: 1px solid #ddd; }
                .image-container { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>HTTPS Image Loading Test</h1>
            
            <div class="image-container">
                <h3>HTTPS Image from DigitalOcean Spaces:</h3>
                <img src="https://trakteer-uploads.sgp1.digitaloceanspaces.com/images/avatar/ava-NmaQ5kjtbJoiaBKm1qqf4CsrtB2yecsS1741084337.jpg" alt="Avatar Image">
            </div>
            
            <div class="image-container">
                <h3>HTTPS Image from Unsplash:</h3>
                <img src="https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3" alt="Code Image">
            </div>
            
            <div class="image-container">
                <h3>HTTPS Image from Placeholder:</h3>
                <img src="https://via.placeholder.com/300x200" alt="Placeholder">
            </div>
            
            <div id="status">Loading images...</div>
            
            <script>
                window.onload = function() {
                    document.getElementById('status').textContent = 'All images loaded successfully!';
                    
                    // Check if images are loaded
                    var images = document.getElementsByTagName('img');
                    for (var i = 0; i < images.length; i++) {
                        if (!images[i].complete || images[i].naturalWidth === 0) {
                            document.getElementById('status').textContent = 'Some images failed to load';
                            console.error('Image failed to load:', images[i].src);
                        }
                    }
                };
                
                // Log any image loading errors
                document.addEventListener('error', function(e) {
                    if (e.target.tagName.toLowerCase() === 'img') {
                        console.error('Error loading image:', e.target.src);
                        document.getElementById('status').textContent = 'Error loading some images. Check console for details.';
                    }
                }, true);
            </script>
        </body>
        </html>
        """
        
        # Load the HTML content
        self.web_view.setHtml(html, QUrl("https://example.com/"))
        
        # Add web view to layout
        layout.addWidget(self.web_view)
        
        # Add a button to reload the page
        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.web_view.reload)
        layout.addWidget(reload_button)
        
        # Set layout to central widget
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Log when page is loaded
        self.web_view.loadFinished.connect(self.on_load_finished)
    
    def on_load_finished(self, success):
        if success:
            logging.info("Page loaded successfully")
        else:
            logging.error("Failed to load page")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestHttpsImagesWindow()
    window.show()
    sys.exit(app.exec())
