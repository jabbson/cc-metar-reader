"""Tests for Flask application routes and endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from services.metar_fetcher import MetarFetchError
from services.metar_parser import MetarParseError
from tests.conftest import SAMPLE_METARS


class TestRoutes:
    """Test Flask application routes."""

    def test_index_route(self, client):
        """Test that index route returns homepage."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'METAR Weather Reader' in response.data

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error'].lower()


class TestWeatherAPI:
    """Test /api/weather endpoint."""

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_valid_icao_code(self, mock_parse, mock_fetch, client):
        """Test API with valid ICAO code."""
        # Mock the service layer
        mock_fetch.return_value = SAMPLE_METARS['clear']
        mock_parse.return_value = {
            'station': 'KJFK',
            'time': '2026-02-08 17:51 UTC',
            'temp_f': 55,
            'temp_c': 13,
            'wind_speed_mph': 24,
            'wind_speed_kt': 21,
            'wind_dir_text': 'NW',
            'visibility_mi': 10,
            'pressure_in': 30.12,
            'pressure_mb': 1020,
            'sky_conditions': ['CLR'],
            'weather': []
        }

        response = client.get('/api/weather/KJFK')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['icao_code'] == 'KJFK'
        assert 'summary' in data
        assert 'data' in data
        assert 'raw_metar' in data
        assert data['data']['Location'] == 'KJFK'
        assert 'Temperature' in data['data']
        assert 'Wind' in data['data']

    @patch('app.fetch_metar')
    def test_fetch_error(self, mock_fetch, client):
        """Test API handles fetch errors."""
        mock_fetch.side_effect = MetarFetchError("Airport not found")

        response = client.get('/api/weather/ZZZZ')
        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False
        assert 'Airport not found' in data['error']

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_parse_error(self, mock_parse, mock_fetch, client):
        """Test API handles parse errors."""
        mock_fetch.return_value = "INVALID METAR"
        mock_parse.side_effect = MetarParseError("Invalid format")

        response = client.get('/api/weather/KHIO')
        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False
        assert 'parse' in data['error'].lower()

    @patch('app.fetch_metar')
    def test_unexpected_error(self, mock_fetch, client):
        """Test API handles unexpected errors."""
        mock_fetch.side_effect = Exception("Unexpected error")

        response = client.get('/api/weather/KHIO')
        assert response.status_code == 500

        data = response.get_json()
        assert data['success'] is False
        assert 'unexpected' in data['error'].lower()

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_rainy_weather(self, mock_parse, mock_fetch, client):
        """Test API with rainy weather conditions."""
        mock_fetch.return_value = SAMPLE_METARS['rain']
        mock_parse.return_value = {
            'station': 'KHIO',
            'time': '2026-02-08 17:57 UTC',
            'temp_f': 50,
            'temp_c': 10,
            'wind_speed_mph': 6,
            'wind_speed_kt': 5,
            'wind_dir_text': 'S',
            'visibility_mi': 2.5,
            'pressure_in': 30.14,
            'pressure_mb': 1021,
            'sky_conditions': ['BKN at 900 ft', 'BKN at 2,900 ft', 'OVC at 3,700 ft'],
            'weather': ['RA', 'BR']
        }

        response = client.get('/api/weather/KHIO')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'RA' in data['data']['Weather Conditions']
        assert data['data']['Visibility'] == '2.5 miles'

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_calm_wind(self, mock_parse, mock_fetch, client):
        """Test API with calm wind conditions."""
        mock_fetch.return_value = SAMPLE_METARS['calm']
        mock_parse.return_value = {
            'station': 'KSEA',
            'time': '2026-02-08 17:53 UTC',
            'temp_f': 45,
            'temp_c': 7,
            'wind_speed_mph': 0,
            'wind_speed_kt': 0,
            'wind_dir_text': 'Calm',
            'visibility_mi': 10,
            'pressure_in': 30.25,
            'pressure_mb': 1025,
            'sky_conditions': ['FEW at 2,200 ft', 'SCT at 5,000 ft', 'BKN at 13,000 ft'],
            'weather': []
        }

        response = client.get('/api/weather/KSEA')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['data']['Wind'] == 'Calm'


class TestFormattingHelpers:
    """Test internal formatting helper functions."""

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_format_temperature(self, mock_parse, mock_fetch, client):
        """Test temperature formatting in response."""
        mock_fetch.return_value = SAMPLE_METARS['clear']
        mock_parse.return_value = {
            'station': 'KJFK',
            'temp_f': 55.4,
            'temp_c': 13.0,
            'wind_speed_mph': 0,
            'wind_speed_kt': 0,
            'wind_dir_text': 'Calm',
            'visibility_mi': 10,
            'pressure_in': 30.12,
            'pressure_mb': 1020,
            'sky_conditions': [],
            'weather': []
        }

        response = client.get('/api/weather/KJFK')
        data = response.get_json()

        # Temperature should be rounded to integers
        assert '55°F' in data['data']['Temperature']
        assert '13°C' in data['data']['Temperature']

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_format_visibility(self, mock_parse, mock_fetch, client):
        """Test visibility formatting in response."""
        mock_fetch.return_value = SAMPLE_METARS['clear']

        # Test visibility >= 10 miles
        mock_parse.return_value = {
            'station': 'KJFK',
            'temp_f': 55,
            'temp_c': 13,
            'wind_speed_mph': 0,
            'wind_speed_kt': 0,
            'wind_dir_text': 'Calm',
            'visibility_mi': 10,
            'pressure_in': 30.12,
            'pressure_mb': 1020,
            'sky_conditions': [],
            'weather': []
        }

        response = client.get('/api/weather/KJFK')
        data = response.get_json()
        assert data['data']['Visibility'] == '10+ miles'

    @patch('app.fetch_metar')
    @patch('app.parse_metar')
    def test_missing_data_handling(self, mock_parse, mock_fetch, client):
        """Test handling of missing weather data."""
        mock_fetch.return_value = SAMPLE_METARS['clear']
        mock_parse.return_value = {
            'station': 'KJFK',
            'temp_f': None,
            'temp_c': None,
            'wind_speed_mph': 0,
            'wind_speed_kt': 0,
            'wind_dir_text': 'Calm',
            'visibility_mi': None,
            'pressure_in': None,
            'pressure_mb': None,
            'sky_conditions': [],
            'weather': []
        }

        response = client.get('/api/weather/KJFK')
        data = response.get_json()

        assert data['success'] is True
        assert data['data']['Temperature'] == 'Not available'
        assert data['data']['Visibility'] == 'Not available'
        assert data['data']['Pressure'] == 'Not available'
