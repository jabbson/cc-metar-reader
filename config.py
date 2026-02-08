"""Configuration settings for the METAR reader application."""

import os

# Aviation Weather API endpoint
AVIATIONWEATHER_API_URL = "https://aviationweather.gov/api/data/metar"

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Flask configuration
# DEBUG should be False in production. Set via FLASK_DEBUG environment variable.
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
