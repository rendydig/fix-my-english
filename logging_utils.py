"""
Utility functions for safer logging, especially for handling Unicode and special characters.
"""
import logging

def safe_log_url(url, max_length=100):
    """
    Safely log a URL by handling potential Unicode encoding issues.
    
    Args:
        url: The URL to log
        max_length: Maximum length to truncate the URL to (default: 100)
        
    Returns:
        A safe version of the URL for logging
    """
    try:
        # If url is None, return a placeholder
        if url is None:
            return "<None>"
            
        # Convert to string if it's not already
        url_str = str(url)
        
        # Truncate to avoid potential issues with very long URLs
        safe_url = url_str[:max_length]
        
        # If truncated, add an indicator
        if len(url_str) > max_length:
            safe_url += "..."
            
        # Replace any potentially problematic characters
        safe_url = safe_url.encode('ascii', 'replace').decode('ascii')
        
        return safe_url
    except Exception as e:
        # If there's any error, return a generic message
        logging.error(f"Error creating safe URL for logging: {e.__class__.__name__}")
        return "<URL logging error>"

def configure_utf8_logging():
    """Configure logging with UTF-8 encoding to avoid Unicode errors"""
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'  # Specify UTF-8 encoding for log output
        )
    except TypeError:
        # For Python versions that don't support the encoding parameter
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.warning("Logging configured without UTF-8 encoding - some characters may not display correctly")
