"""
Module containing the HTML content for the donation page.
This allows the HTML to be included in the Python executable without requiring an external file.
"""
from fetch_donation_url import fetch_donation_url

# HTML content as a Python string
DONATION_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https: http: qrc:; script-src 'self' 'unsafe-inline' 'unsafe-eval' qrc:; style-src 'self' 'unsafe-inline'; img-src 'self' https: http: data: blob:;">
    <title>Support Fix My English</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: #00B4DB;  /* fallback for old browsers */
            background: -webkit-linear-gradient(to right, #0083B0, #00B4DB);  /* Chrome 10-25, Safari 5.1-6 */
            background: linear-gradient(to right, #0083B0, #00B4DB); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
        }
        
        .container {
            max-width: 800px;
            padding: 40px;
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: fadeIn 0.8s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: white;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .description {
            margin-bottom: 30px;
            line-height: 1.6;
            font-size: 1.1rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .features {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
        }
        
        .feature {
            background-color: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 12px;
            width: calc(33.33% - 20px);
            min-width: 200px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }
        
        .feature h3 {
            margin-bottom: 10px;
            font-size: 1.2rem;
        }
        
        .donate-button {
            display: inline-block;
            margin-top: 30px;
            padding: 15px 40px;
            background-color: #FF5722;
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
            border: none;
            cursor: pointer;
        }
        
        .donate-button:hover {
            background-color: #FF7043;
            box-shadow: 0 6px 20px rgba(255, 87, 34, 0.6);
            transform: translateY(-2px);
        }
        
        .footer {
            margin-top: 40px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
            font-style: italic;
        }
    </style>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div class="container">
        <h1>Support Fix My English</h1>
        
        <p class="description">
            Your support helps us continue developing and improving this application. 
            Fix My English is a desktop utility that helps you correct and improve your text with the power of 
            Google's Generative AI, making your writing more professional and error-free.
        </p>
        
        <div class="features">
            <div class="feature">
                <h3>Quick Text Correction</h3>
                <p>Instantly improve your text with a simple hotkey (Ctrl+Alt+Space)</p>
            </div>
            <div class="feature">
                <h3>AI-Powered</h3>
                <p>Leverages Google's Gemini model for high-quality text improvements</p>
            </div>
            <button id="donateButton" class="donate-button">Donasi</button>
        </div>
        <div id="loadingMessage" class="loading">Opening donation page...</div>
        <p class="description">
            By supporting this project, you help us maintain the API services, develop new features, 
            and ensure the application remains updated and functional for all users.
        </p>
        
        <div class="footer">
            <p>Thank you for using Fix My English! ❤️</p>
        </div>
    </div>
    
    <script>
        // Initialize the Qt web channel
        let handler;
        
        // This function will be called once the web channel is set up
        function onWebChannelReady(channel) {
            // Get the handler object that was registered in Python
            handler = channel.objects.handler;
            console.log("Web channel initialized successfully");
        }
        
        // Set up the web channel when the document is ready
        document.addEventListener("DOMContentLoaded", function() {
            if (typeof QWebChannel !== "undefined") {
                new QWebChannel(qt.webChannelTransport, onWebChannelReady);
                console.log("QWebChannel setup initiated");
            } else {
                console.error("QWebChannel not available");
            }
        });
        
        // Handle donation button click
        document.getElementById('donateButton').addEventListener('click', function() {
            // Show loading message
            document.getElementById('loadingMessage').style.display = 'block';
            
            const donationUrl = '{{DONATION_URL_PLACEHOLDER}}';
            
            // Try to use the web channel if available
            if (handler) {
                console.log('Using web channel to open URL');
                handler.openExternalUrl(donationUrl);
            } else {
                console.log('Web channel not available, using fallback method');
                // Fallback to standard navigation
                try {
                    window.location.href = donationUrl;
                } catch (error) {
                    console.error('Error navigating to donation page:', error);
                    document.getElementById('loadingMessage').textContent = 'Error opening donation page. Please try again.';
                }
            }
        });
        
        // Log when page is loaded
        window.addEventListener('load', function() {
            console.log('Donation page loaded successfully');
            
            // Check if all images are loaded correctly
            var images = document.getElementsByTagName('img');
            for (var i = 0; i < images.length; i++) {
                (function(img) {
                    // If image is already complete, check if it loaded successfully
                    if (img.complete) {
                        if (img.naturalWidth === 0) {
                            console.error('Image failed to load:', img.src);
                        }
                    } else {
                        // If not complete, add load and error event listeners
                        img.addEventListener('load', function() {
                            console.log('Image loaded successfully:', img.src);
                        });
                        
                        img.addEventListener('error', function() {
                            console.error('Image failed to load:', img.src);
                            // Try to reload the image with a cache-busting parameter
                            if (!img.src.includes('?nocache=')) {
                                img.src = img.src + '?nocache=' + new Date().getTime();
                            }
                        });
                    }
                })(images[i]);
            }
        });
    </script>
</body>
</html>
"""

# Replace the donation URL placeholder with the actual URL
def get_donation_page_html():
    """
    Get the donation page HTML with the actual donation URL fetched from the server.
    """
    try:
        donation_url = fetch_donation_url()
        return DONATION_PAGE_HTML.replace('{{DONATION_URL_PLACEHOLDER}}', donation_url)
    except Exception as e:
        import logging
        logging.error(f"Error in get_donation_page_html: {str(e)}")
        # Fallback to default URL if there's an error
        return DONATION_PAGE_HTML.replace('{{DONATION_URL_PLACEHOLDER}}', 'https://trakteer.id/rendyadi/tip?open=true')
