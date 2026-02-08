"""Tests for weather data formatting functions."""

import pytest
from utils.formatters import (
    format_temperature,
    format_wind,
    format_visibility,
    format_sky_conditions,
    format_pressure,
    format_weather_phenomena,
    format_weather_summary
)


class TestFormatTemperature:
    """Test temperature formatting."""

    def test_valid_temperature(self):
        """Test formatting valid temperature."""
        result = format_temperature(70.5, 21.4)
        assert '70°F' in result or '71°F' in result  # Rounding can vary
        assert '21°C' in result

    def test_freezing_temperature(self):
        """Test formatting freezing temperature."""
        result = format_temperature(32, 0)
        assert '32°F' in result
        assert '0°C' in result

    def test_negative_temperature(self):
        """Test formatting negative temperature."""
        result = format_temperature(-5, -20.6)
        assert '-5°F' in result
        assert '-21°C' in result

    def test_missing_temperature(self):
        """Test formatting missing temperature."""
        result = format_temperature(None, None)
        assert result == 'Not available'


class TestFormatWind:
    """Test wind formatting."""

    def test_calm_wind(self):
        """Test formatting calm wind."""
        result = format_wind(0, 'Calm')
        assert result == 'Calm winds'

    def test_north_wind(self):
        """Test formatting north wind."""
        result = format_wind(15, 'N')
        assert '15 mph' in result
        assert 'north' in result.lower()

    def test_southwest_wind(self):
        """Test formatting southwest wind."""
        result = format_wind(25, 'SW')
        assert '25 mph' in result
        assert 'southwest' in result.lower()

    def test_variable_wind(self):
        """Test formatting variable wind."""
        result = format_wind(10, 'Variable')
        assert '10 mph' in result
        assert 'variable' in result.lower()

    def test_none_speed(self):
        """Test formatting None wind speed."""
        result = format_wind(None, 'N')
        assert result == 'Calm winds'


class TestFormatVisibility:
    """Test visibility formatting."""

    def test_unlimited_visibility(self):
        """Test formatting unlimited visibility."""
        result = format_visibility(10)
        assert '10+ miles' in result
        assert 'unlimited' in result

    def test_good_visibility(self):
        """Test formatting good visibility."""
        result = format_visibility(5)
        assert '5 miles' in result

    def test_poor_visibility(self):
        """Test formatting poor visibility."""
        result = format_visibility(0.25)
        assert '0.2' in result or '0.3' in result
        assert 'miles' in result

    def test_fractional_visibility(self):
        """Test formatting fractional visibility."""
        result = format_visibility(2.5)
        assert '2.5 miles' in result

    def test_missing_visibility(self):
        """Test formatting missing visibility."""
        result = format_visibility(None)
        assert result == 'Not available'


class TestFormatSkyConditions:
    """Test sky conditions formatting."""

    def test_clear_skies(self):
        """Test formatting clear skies."""
        result = format_sky_conditions(['CLR'])
        assert 'Clear skies' in result

    def test_few_clouds(self):
        """Test formatting few clouds."""
        result = format_sky_conditions(['FEW at 5,000 ft'])
        assert 'Few clouds' in result
        assert '5,000 ft' in result

    def test_scattered_clouds(self):
        """Test formatting scattered clouds."""
        result = format_sky_conditions(['SCT at 3,000 ft'])
        assert 'Scattered clouds' in result

    def test_broken_clouds(self):
        """Test formatting broken clouds."""
        result = format_sky_conditions(['BKN at 2,000 ft'])
        assert 'Broken clouds' in result

    def test_overcast(self):
        """Test formatting overcast."""
        result = format_sky_conditions(['OVC at 1,500 ft'])
        assert 'Overcast' in result

    def test_multiple_layers(self):
        """Test formatting multiple cloud layers."""
        result = format_sky_conditions([
            'FEW at 2,000 ft',
            'SCT at 5,000 ft',
            'BKN at 10,000 ft'
        ])
        assert 'Few clouds' in result
        assert 'Scattered clouds' in result
        assert 'Broken clouds' in result

    def test_no_sky_conditions(self):
        """Test formatting no sky conditions."""
        result = format_sky_conditions([])
        assert 'not reported' in result.lower()


class TestFormatPressure:
    """Test pressure formatting."""

    def test_standard_pressure(self):
        """Test formatting standard pressure."""
        result = format_pressure(29.92, 1013)
        assert '29.92 inHg' in result
        assert '1013 mb' in result

    def test_high_pressure(self):
        """Test formatting high pressure."""
        result = format_pressure(30.50, 1033)
        assert '30.50 inHg' in result
        assert '1033 mb' in result

    def test_low_pressure(self):
        """Test formatting low pressure."""
        result = format_pressure(29.00, 982)
        assert '29.00 inHg' in result
        assert '982 mb' in result

    def test_missing_pressure(self):
        """Test formatting missing pressure."""
        result = format_pressure(None, None)
        assert result == 'Not available'


class TestFormatWeatherPhenomena:
    """Test weather phenomena formatting."""

    def test_rain(self):
        """Test formatting rain."""
        result = format_weather_phenomena(['RA'])
        assert 'rain' in result

    def test_snow(self):
        """Test formatting snow."""
        result = format_weather_phenomena(['SN'])
        assert 'snow' in result

    def test_fog(self):
        """Test formatting fog."""
        result = format_weather_phenomena(['FG'])
        assert 'fog' in result

    def test_drifting_snow(self):
        """Test formatting drifting snow."""
        result = format_weather_phenomena(['DRSN'])
        assert 'drifting' in result
        assert 'snow' in result

    def test_heavy_rain(self):
        """Test formatting heavy rain."""
        result = format_weather_phenomena(['+RA'])
        assert 'heavy' in result
        assert 'rain' in result

    def test_light_snow(self):
        """Test formatting light snow."""
        result = format_weather_phenomena(['-SN'])
        assert 'light' in result
        assert 'snow' in result

    def test_thunderstorm(self):
        """Test formatting thunderstorm."""
        result = format_weather_phenomena(['TS'])
        assert 'thunderstorm' in result

    def test_multiple_phenomena(self):
        """Test formatting multiple weather phenomena."""
        result = format_weather_phenomena(['RA', 'BR'])
        assert 'rain' in result
        assert 'mist' in result

    def test_no_phenomena(self):
        """Test formatting no weather phenomena."""
        result = format_weather_phenomena([])
        assert result is None


class TestFormatWeatherSummary:
    """Test complete weather summary formatting."""

    def test_clear_weather_summary(self):
        """Test formatting clear weather summary."""
        data = {
            'temp_f': 70,
            'temp_c': 21,
            'wind_speed_mph': 10,
            'wind_dir_text': 'N',
            'visibility_mi': 10,
            'pressure_in': 30.00,
            'pressure_mb': 1016,
            'sky_conditions': ['CLR'],
            'weather': []
        }
        result = format_weather_summary(data)

        assert 'Clear skies' in result
        assert '70°F' in result
        assert '21°C' in result
        assert '10 mph' in result
        assert 'north' in result.lower()

    def test_rainy_weather_summary(self):
        """Test formatting rainy weather summary."""
        data = {
            'temp_f': 50,
            'temp_c': 10,
            'wind_speed_mph': 5,
            'wind_dir_text': 'S',
            'visibility_mi': 3,
            'pressure_in': 29.90,
            'pressure_mb': 1013,
            'sky_conditions': ['OVC at 1,000 ft'],
            'weather': ['RA']
        }
        result = format_weather_summary(data)

        assert 'Overcast' in result
        assert 'rain' in result
        assert '50°F' in result
        assert '3 miles' in result

    def test_minimal_data_summary(self):
        """Test formatting summary with minimal data."""
        data = {
            'temp_f': None,
            'temp_c': None,
            'wind_speed_mph': 0,
            'wind_dir_text': 'Calm',
            'visibility_mi': None,
            'pressure_in': None,
            'pressure_mb': None,
            'sky_conditions': [],
            'weather': []
        }
        result = format_weather_summary(data)

        # Should handle missing data gracefully
        assert 'Calm' in result
        assert len(result) > 0
