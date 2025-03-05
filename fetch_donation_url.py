import requests
import re
import logging
import html
from logging_utils import safe_log_url

def fetch_donation_url():
    """
    Fetch donation URL from fixitai.hashnode.dev/donate meta tag
    and fix any HTML entity encoding issues.
    """
    try:
        url = "https://fixitai.hashnode.dev/donate"
        # Set encoding explicitly and add timeout
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url}, status code: {response.status_code}")
            # Return default URL as fallback
            return 'https://trakteer.id/rendyadi/tip?open=true'
            
        # Extract meta content using regex
        pattern = r'<meta property="og:description" content="([^"]*)"'
        match = re.search(pattern, response.text)
        
        if match:
            donation_url = match.group(1).strip()
            # Fix HTML entity encoding using html.unescape
            donation_url = html.unescape(donation_url)
            logging.info(f"Fetched donation URL: {safe_log_url(donation_url)}")
            return donation_url
        else:
            logging.warning(f"Meta description not found in {url}")
            # Return default URL as fallback
            return 'https://trakteer.id/rendyadi/tip?open=true'
            
    except Exception as e:
        logging.error(f"Error fetching donation URL: {str(e)}")
        # Return default URL as fallback
        return 'https://trakteer.id/rendyadi/tip?open=true'
