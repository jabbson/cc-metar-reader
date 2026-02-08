"""Formatters for converting METAR data to human-readable text."""


def format_temperature(temp_f, temp_c):
    """
    Format temperature in both Fahrenheit and Celsius.

    Args:
        temp_f: Temperature in Fahrenheit
        temp_c: Temperature in Celsius

    Returns:
        str: Formatted temperature string
    """
    if temp_f is None or temp_c is None:
        return "Not available"

    return f"{int(round(temp_f))}°F ({int(round(temp_c))}°C)"


def format_wind(speed_mph, direction_text):
    """
    Format wind information in plain English.

    Args:
        speed_mph: Wind speed in mph
        direction_text: Wind direction as compass text (N, NE, etc.)

    Returns:
        str: Formatted wind string
    """
    if speed_mph is None or speed_mph == 0:
        return "Calm winds"

    speed = int(round(speed_mph))

    if direction_text == 'Calm':
        return "Calm winds"
    elif direction_text == 'Variable':
        return f"{speed} mph from variable directions"
    else:
        direction_full = _expand_compass_direction(direction_text)
        return f"{speed} mph from the {direction_full.lower()}"


def format_visibility(visibility_mi):
    """
    Format visibility in plain English.

    Args:
        visibility_mi: Visibility in statute miles

    Returns:
        str: Formatted visibility string
    """
    if visibility_mi is None:
        return "Not available"

    vis = round(visibility_mi, 1)

    if vis >= 10:
        return "10+ miles (unlimited)"
    elif vis == int(vis):
        return f"{int(vis)} miles"
    else:
        return f"{vis} miles"


def format_sky_conditions(sky_conditions):
    """
    Format sky conditions in plain English.

    Args:
        sky_conditions: List of sky condition strings

    Returns:
        str: Formatted sky conditions string
    """
    if not sky_conditions:
        return "Sky conditions not reported"

    formatted = []

    for condition in sky_conditions:
        if 'SKC' in condition or 'CLR' in condition:
            return "Clear skies"
        elif 'FEW' in condition:
            formatted.append(f"Few clouds {condition.replace('FEW', '').strip()}")
        elif 'SCT' in condition:
            formatted.append(f"Scattered clouds {condition.replace('SCT', '').strip()}")
        elif 'BKN' in condition:
            formatted.append(f"Broken clouds {condition.replace('BKN', '').strip()}")
        elif 'OVC' in condition:
            formatted.append(f"Overcast {condition.replace('OVC', '').strip()}")
        else:
            formatted.append(condition)

    if not formatted:
        return "Sky conditions not reported"

    return ', '.join(formatted)


def format_pressure(pressure_in, pressure_mb):
    """
    Format atmospheric pressure.

    Args:
        pressure_in: Pressure in inches of mercury
        pressure_mb: Pressure in millibars

    Returns:
        str: Formatted pressure string
    """
    if pressure_in is None or pressure_mb is None:
        return "Not available"

    return f"{pressure_in:.2f} inHg ({int(round(pressure_mb))} mb)"


def format_weather_phenomena(weather_list):
    """
    Format weather phenomena (rain, snow, etc.) in plain English.

    Args:
        weather_list: List of weather phenomenon codes

    Returns:
        str: Formatted weather string
    """
    if not weather_list:
        return None

    # Common weather translations
    # Order matters - process longer codes first to avoid partial replacements
    translations = [
        ('+', 'heavy '),
        ('-', 'light '),
        ('TS', 'thunderstorm'),
        ('SH', 'showers'),
        ('FZ', 'freezing'),
        ('BL', 'blowing'),
        ('DR', 'drifting'),
        ('MI', 'shallow'),
        ('BC', 'patches'),
        ('PR', 'partial'),
        ('RA', 'rain'),
        ('SN', 'snow'),
        ('DZ', 'drizzle'),
        ('FG', 'fog'),
        ('BR', 'mist'),
        ('HZ', 'haze'),
        ('VA', 'volcanic ash'),
        ('DU', 'dust'),
        ('SA', 'sand'),
        ('FU', 'smoke'),
        ('PY', 'spray'),
        ('SQ', 'squalls'),
        ('PO', 'dust whirls'),
        ('DS', 'dust storm'),
        ('SS', 'sandstorm'),
        ('GR', 'hail'),
        ('GS', 'small hail'),
        ('UP', 'unknown precipitation'),
        ('IC', 'ice crystals'),
        ('PL', 'ice pellets'),
        ('SG', 'snow grains'),
    ]

    formatted = []
    for phenomenon in weather_list:
        weather_str = phenomenon
        # Process translations in order
        for code, translation in translations:
            weather_str = weather_str.replace(code, f' {translation}')
        # Clean up extra spaces and strip
        weather_str = ' '.join(weather_str.split()).strip()
        if weather_str:
            formatted.append(weather_str)

    return ', '.join(formatted)


def format_weather_summary(weather_data):
    """
    Create a complete plain English summary of weather conditions.

    Args:
        weather_data: Dictionary of parsed METAR data

    Returns:
        str: Human-readable weather summary
    """
    summary_parts = []

    # Sky conditions
    sky = format_sky_conditions(weather_data.get('sky_conditions', []))
    if sky and 'not reported' not in sky.lower():
        summary_parts.append(sky)

    # Weather phenomena (rain, snow, etc.)
    weather = format_weather_phenomena(weather_data.get('weather', []))
    if weather:
        summary_parts.append(f"with {weather}")

    # Temperature
    temp_f = weather_data.get('temp_f')
    temp_c = weather_data.get('temp_c')
    if temp_f is not None:
        temp_str = format_temperature(temp_f, temp_c)
        summary_parts.append(f"Temperature is {temp_str}")

    # Wind
    wind_speed = weather_data.get('wind_speed_mph', 0)
    wind_dir = weather_data.get('wind_dir_text', 'Variable')
    wind_str = format_wind(wind_speed, wind_dir)
    summary_parts.append(wind_str)

    # Visibility
    visibility = weather_data.get('visibility_mi')
    if visibility is not None:
        vis_str = format_visibility(visibility)
        summary_parts.append(f"Visibility is {vis_str}")

    # Pressure
    pressure_in = weather_data.get('pressure_in')
    pressure_mb = weather_data.get('pressure_mb')
    if pressure_in is not None:
        pressure_str = format_pressure(pressure_in, pressure_mb)
        summary_parts.append(f"Barometric pressure is {pressure_str}")

    # Join all parts with appropriate punctuation
    if len(summary_parts) == 0:
        return "Weather data unavailable."

    summary = '. '.join(summary_parts)
    if not summary.endswith('.'):
        summary += '.'

    return summary


def _expand_compass_direction(direction):
    """
    Expand compass abbreviation to full name.

    Args:
        direction: Compass abbreviation (N, NE, etc.)

    Returns:
        str: Full direction name
    """
    expansions = {
        'N': 'North',
        'NNE': 'North-Northeast',
        'NE': 'Northeast',
        'ENE': 'East-Northeast',
        'E': 'East',
        'ESE': 'East-Southeast',
        'SE': 'Southeast',
        'SSE': 'South-Southeast',
        'S': 'South',
        'SSW': 'South-Southwest',
        'SW': 'Southwest',
        'WSW': 'West-Southwest',
        'W': 'West',
        'WNW': 'West-Northwest',
        'NW': 'Northwest',
        'NNW': 'North-Northwest',
    }

    return expansions.get(direction, direction)
