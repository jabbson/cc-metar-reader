"""METAR data fetcher - handles API calls to aviationweather.gov."""

import re
import requests
from config import AVIATIONWEATHER_API_URL, REQUEST_TIMEOUT


class MetarFetchError(Exception):
    """Exception raised when METAR data cannot be fetched."""
    pass


def validate_icao_code(icao_code):
    """
    Validate ICAO airport code format.

    Args:
        icao_code: Airport code to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not icao_code:
        return False

    # ICAO codes are 4 letters
    pattern = r'^[A-Z]{4}$'
    return bool(re.match(pattern, icao_code.upper()))


def fetch_metar(icao_code):
    """
    Fetch METAR data from aviationweather.gov API.

    Args:
        icao_code: 4-letter ICAO airport code (e.g., 'KHIO')

    Returns:
        str: Raw METAR string

    Raises:
        MetarFetchError: If data cannot be fetched or code is invalid
    """
    # Validate ICAO code
    if not validate_icao_code(icao_code):
        raise MetarFetchError(f"Invalid ICAO code format: {icao_code}. Must be 4 letters.")

    icao_code = icao_code.upper()

    try:
        # Build request URL
        params = {'ids': icao_code}

        # Make API request
        response = requests.get(
            AVIATIONWEATHER_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        # Check for HTTP errors
        response.raise_for_status()

        # Get the METAR text
        metar_text = response.text.strip()

        if not metar_text:
            raise MetarFetchError(f"No METAR data found for airport: {icao_code}")

        return metar_text

    except requests.exceptions.Timeout:
        raise MetarFetchError(f"Request timed out while fetching METAR for {icao_code}")

    except requests.exceptions.ConnectionError:
        raise MetarFetchError("Unable to connect to aviation weather service")

    except requests.exceptions.HTTPError as e:
        raise MetarFetchError(f"HTTP error occurred: {e}")

    except Exception as e:
        raise MetarFetchError(f"Unexpected error fetching METAR: {str(e)}")
