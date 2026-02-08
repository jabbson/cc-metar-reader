"""Flask application for METAR weather reader."""

import logging
from flask import Flask, render_template, jsonify
from services.metar_fetcher import fetch_metar, MetarFetchError
from services.metar_parser import parse_metar, MetarParseError
from utils.formatters import format_weather_summary
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config)


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/api/weather/<icao_code>')
def get_weather(icao_code):
    """
    Fetch and parse METAR data for the specified airport.

    Args:
        icao_code: 4-letter ICAO airport code

    Returns:
        JSON response with weather data or error message
    """
    try:
        # Fetch raw METAR data
        raw_metar = fetch_metar(icao_code)

        # Parse METAR into structured data
        weather_data = parse_metar(raw_metar)

        # Generate human-readable summary
        summary = format_weather_summary(weather_data)

        # Prepare response
        response = {
            'success': True,
            'icao_code': icao_code.upper(),
            'summary': summary,
            'data': {
                'Location': weather_data.get('station', 'Unknown'),
                'Time': weather_data.get('time', 'Not available'),
                'Weather Conditions': _format_conditions(weather_data),
                'Temperature': _format_temp(weather_data),
                'Wind': _format_wind_display(weather_data),
                'Visibility': _format_visibility_display(weather_data),
                'Pressure': _format_pressure_display(weather_data),
                'Sky Conditions': _format_sky_display(weather_data),
            },
            'raw_metar': raw_metar
        }

        return jsonify(response)

    except MetarFetchError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except MetarParseError as e:
        return jsonify({
            'success': False,
            'error': f"Unable to parse METAR data: {str(e)}"
        }), 400

    except Exception as e:
        logger.exception(f"Unexpected error processing METAR for {icao_code}: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


def _format_conditions(weather_data):
    """Format weather conditions for display."""
    weather = weather_data.get('weather', [])
    if weather:
        return ', '.join(weather)
    return 'Clear'


def _format_temp(weather_data):
    """Format temperature for display."""
    temp_f = weather_data.get('temp_f')
    temp_c = weather_data.get('temp_c')
    if temp_f is not None and temp_c is not None:
        return f"{int(round(temp_f))}°F ({int(round(temp_c))}°C)"
    return 'Not available'


def _format_wind_display(weather_data):
    """Format wind for display."""
    speed_mph = weather_data.get('wind_speed_mph', 0)
    speed_kt = weather_data.get('wind_speed_kt', 0)
    direction = weather_data.get('wind_dir_text', 'Calm')

    if speed_mph == 0:
        return 'Calm'

    return f"{int(round(speed_mph))} mph ({int(round(speed_kt))} kt) from {direction}"


def _format_visibility_display(weather_data):
    """Format visibility for display."""
    vis = weather_data.get('visibility_mi')
    if vis is None:
        return 'Not available'

    if vis >= 10:
        return '10+ miles'
    elif vis == int(vis):
        return f'{int(vis)} miles'
    else:
        return f'{vis:.1f} miles'


def _format_pressure_display(weather_data):
    """Format pressure for display."""
    pressure_in = weather_data.get('pressure_in')
    pressure_mb = weather_data.get('pressure_mb')

    if pressure_in is not None and pressure_mb is not None:
        return f"{pressure_in:.2f} inHg ({int(round(pressure_mb))} mb)"
    return 'Not available'


def _format_sky_display(weather_data):
    """Format sky conditions for display."""
    sky = weather_data.get('sky_conditions', [])
    if not sky:
        return 'Not reported'
    return ', '.join(sky)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Page not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5555)
