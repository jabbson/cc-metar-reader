"""METAR parser - decodes METAR strings using python-metar library."""

import logging
from metar.Metar import Metar

logger = logging.getLogger(__name__)


class MetarParseError(Exception):
    """Exception raised when METAR data cannot be parsed."""
    pass


def parse_metar(metar_string):
    """
    Parse METAR string into structured data.

    Args:
        metar_string: Raw METAR string from API

    Returns:
        dict: Parsed weather data with keys:
            - station: Airport ICAO code
            - time: Observation time
            - temp_c: Temperature in Celsius
            - temp_f: Temperature in Fahrenheit
            - dewpoint_c: Dewpoint in Celsius
            - dewpoint_f: Dewpoint in Fahrenheit
            - wind_speed_kt: Wind speed in knots
            - wind_speed_mph: Wind speed in mph
            - wind_dir: Wind direction in degrees
            - wind_dir_text: Wind direction as text (N, NE, etc.)
            - visibility_mi: Visibility in statute miles
            - pressure_mb: Pressure in millibars
            - pressure_in: Pressure in inches of mercury
            - sky_conditions: List of sky condition strings
            - weather: List of weather phenomena

    Raises:
        MetarParseError: If METAR cannot be parsed
    """
    if not metar_string:
        raise MetarParseError("METAR string is empty")

    try:
        # Parse the METAR using python-metar library
        obs = Metar(metar_string)

        # Extract data into dictionary
        data = {
            'station': obs.station_id,
            'time': obs.time.strftime('%Y-%m-%d %H:%M UTC') if obs.time else None,
        }

        # Temperature
        if obs.temp:
            data['temp_c'] = obs.temp.value('C')
            data['temp_f'] = obs.temp.value('F')
        else:
            data['temp_c'] = None
            data['temp_f'] = None

        # Dewpoint
        if obs.dewpt:
            data['dewpoint_c'] = obs.dewpt.value('C')
            data['dewpoint_f'] = obs.dewpt.value('F')
        else:
            data['dewpoint_c'] = None
            data['dewpoint_f'] = None

        # Wind
        if obs.wind_speed:
            data['wind_speed_kt'] = obs.wind_speed.value('KT')
            data['wind_speed_mph'] = obs.wind_speed.value('MPH')
        else:
            data['wind_speed_kt'] = 0
            data['wind_speed_mph'] = 0

        if obs.wind_dir:
            data['wind_dir'] = obs.wind_dir.value()
            data['wind_dir_text'] = _degrees_to_compass(obs.wind_dir.value())
        else:
            data['wind_dir'] = None
            data['wind_dir_text'] = 'Variable' if data['wind_speed_kt'] > 0 else 'Calm'

        # Visibility
        if obs.vis:
            data['visibility_mi'] = obs.vis.value('SM')
        else:
            data['visibility_mi'] = None

        # Pressure
        if obs.press:
            data['pressure_mb'] = obs.press.value('MB')
            data['pressure_in'] = obs.press.value('IN')
        else:
            data['pressure_mb'] = None
            data['pressure_in'] = None

        # Sky conditions
        if obs.sky:
            data['sky_conditions'] = []
            for condition in obs.sky:
                sky_str = condition[0]  # SKC, FEW, SCT, BKN, OVC
                if len(condition) > 1 and condition[1]:
                    height_ft = condition[1].value('FT')
                    data['sky_conditions'].append(f"{sky_str} at {int(height_ft):,} ft")
                else:
                    data['sky_conditions'].append(sky_str)
        else:
            data['sky_conditions'] = []

        # Weather phenomena
        if obs.weather:
            weather_strings = []
            for w in obs.weather:
                # Each weather tuple is (intensity, descriptor, precipitation, obscuration, other)
                weather_parts = []
                if w[0]:  # intensity (+ or -)
                    weather_parts.append(w[0])
                if w[1]:  # descriptor (e.g., SH for showers)
                    weather_parts.append(w[1])
                if w[2]:  # precipitation (e.g., RA for rain)
                    weather_parts.append(w[2])
                if w[3]:  # obscuration (e.g., BR for mist, FG for fog)
                    weather_parts.append(w[3])
                if w[4]:  # other
                    weather_parts.append(w[4])

                if weather_parts:
                    weather_strings.append(''.join(weather_parts))

            data['weather'] = weather_strings
        else:
            data['weather'] = []

        return data

    except Exception as e:
        logger.error(f"Failed to parse METAR string: {metar_string[:100]}... Error: {e}")
        raise MetarParseError(f"Failed to parse METAR: {str(e)}") from e


def _degrees_to_compass(degrees):
    """
    Convert wind direction in degrees to compass direction.

    Args:
        degrees: Wind direction in degrees (0-360)

    Returns:
        str: Compass direction (N, NE, E, etc.)
    """
    if degrees is None:
        return 'Variable'

    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    # Each direction covers 22.5 degrees
    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]
