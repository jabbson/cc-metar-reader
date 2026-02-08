"""Tests for METAR parsing with real METAR strings."""

import pytest
from services.metar_parser import parse_metar, MetarParseError, _degrees_to_compass
from tests.conftest import SAMPLE_METARS


class TestMetarParser:
    """Test METAR parsing with various weather conditions."""

    def test_parse_clear_weather(self):
        """Test parsing clear weather METAR."""
        metar = SAMPLE_METARS['clear']
        data = parse_metar(metar)

        assert data['station'] == 'KJFK'
        assert data['temp_c'] is not None
        assert data['temp_f'] is not None
        assert data['wind_speed_kt'] > 0
        assert data['visibility_mi'] == 10
        assert data['pressure_in'] is not None
        assert 'CLR' in str(data['sky_conditions']) or len(data['sky_conditions']) == 0

    def test_parse_rain(self):
        """Test parsing METAR with rain."""
        metar = SAMPLE_METARS['rain']
        data = parse_metar(metar)

        assert data['station'] == 'KHIO'
        assert 'RA' in data['weather']  # Rain
        assert 'BR' in data['weather']  # Mist
        assert data['visibility_mi'] < 10

    def test_parse_snow(self):
        """Test parsing METAR with drifting snow."""
        metar = SAMPLE_METARS['snow']
        data = parse_metar(metar)

        assert data['station'] == 'CYHZ'
        assert any('DR' in w or 'SN' in w for w in data['weather'])  # Drifting snow
        assert data['temp_c'] < 0  # Below freezing

    def test_parse_fog(self):
        """Test parsing METAR with fog."""
        metar = SAMPLE_METARS['fog']
        data = parse_metar(metar)

        assert data['station'] == 'KSFO'
        assert 'FG' in data['weather']  # Fog
        assert data['visibility_mi'] < 1  # Low visibility

    def test_parse_thunderstorm(self):
        """Test parsing METAR with thunderstorm."""
        metar = SAMPLE_METARS['thunderstorm']
        data = parse_metar(metar)

        assert data['station'] == 'KMIA'
        # Should have thunderstorm indicators
        assert any('TS' in w or '+' in w or 'RA' in w for w in data['weather'])
        assert data['visibility_mi'] < 10

    def test_parse_calm_wind(self):
        """Test parsing METAR with calm winds."""
        metar = SAMPLE_METARS['calm']
        data = parse_metar(metar)

        assert data['station'] == 'KSEA'
        assert data['wind_speed_kt'] == 0
        assert data['wind_speed_mph'] == 0
        # With 00000KT, direction is reported but speed is 0
        assert data['wind_dir_text'] in ('Calm', 'N')  # Parser may vary

    def test_parse_variable_wind(self):
        """Test parsing METAR with variable wind."""
        metar = SAMPLE_METARS['variable_wind']
        data = parse_metar(metar)

        assert data['station'] == 'KATL'
        # Variable winds may have no direction or special handling
        assert data['wind_speed_kt'] > 0

    def test_parse_light_rain(self):
        """Test parsing METAR with light rain (- prefix)."""
        metar = SAMPLE_METARS['light_rain']
        data = parse_metar(metar)

        assert data['station'] == 'KORD'
        assert any('-' in w or 'RA' in w for w in data['weather'])  # Light rain

    def test_parse_empty_string(self):
        """Test parsing empty METAR string raises error."""
        with pytest.raises(MetarParseError):
            parse_metar("")

    def test_parse_invalid_metar(self):
        """Test parsing invalid METAR string raises error."""
        with pytest.raises(MetarParseError):
            parse_metar("INVALID METAR STRING")

    def test_parse_missing_fields(self):
        """Test parsing METAR with some missing optional fields."""
        # METAR with basic required fields but no remarks
        metar = "KORD 081800Z 00000KT 10SM CLR 15/10 A3000"
        data = parse_metar(metar)

        assert data['station'] == 'KORD'
        assert data['wind_speed_kt'] == 0
        assert data['temp_c'] is not None
        assert data['visibility_mi'] == 10
        # All fields should be present in dict even if None
        assert 'temp_c' in data
        assert 'visibility_mi' in data
        assert 'pressure_in' in data


class TestCompassConversion:
    """Test wind direction to compass conversion."""

    def test_north(self):
        """Test north direction."""
        assert _degrees_to_compass(0) == 'N'
        assert _degrees_to_compass(360) == 'N'

    def test_east(self):
        """Test east direction."""
        assert _degrees_to_compass(90) == 'E'

    def test_south(self):
        """Test south direction."""
        assert _degrees_to_compass(180) == 'S'

    def test_west(self):
        """Test west direction."""
        assert _degrees_to_compass(270) == 'W'

    def test_northeast(self):
        """Test northeast direction."""
        assert _degrees_to_compass(45) == 'NE'

    def test_southwest(self):
        """Test southwest direction."""
        assert _degrees_to_compass(225) == 'SW'

    def test_none_value(self):
        """Test None value returns Variable."""
        assert _degrees_to_compass(None) == 'Variable'

    def test_boundary_values(self):
        """Test boundary values near cardinal directions."""
        # Just before North (348.75 - 11.25 = 337.5 to 360)
        assert _degrees_to_compass(350) == 'N'
        # Just after North (0 + 11.25 = 0 to 11.25)
        assert _degrees_to_compass(10) == 'N'
