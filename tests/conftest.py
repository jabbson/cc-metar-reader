"""Pytest configuration and fixtures for METAR reader tests."""

import pytest
from app import app as flask_app


@pytest.fixture
def app():
    """Create Flask application for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


# Sample METAR strings for testing various conditions
SAMPLE_METARS = {
    'clear': 'KJFK 081751Z 31021KT 10SM CLR 13/M11 A3012 RMK AO2',
    'rain': 'KHIO 081757Z 17005KT 2 1/2SM RA BR BKN009 BKN029 OVC037 10/09 A3014',
    'snow': 'CYHZ 081800Z 36020KT 10SM DRSN OVC011 M06/M08 A2997',
    'fog': 'KSFO 081756Z 30008KT 1/4SM FG VV002 15/15 A3000',
    'thunderstorm': 'KMIA 081753Z 09015G25KT 3SM +TSRA BKN008 OVC015CB 24/22 A2990',
    'calm': 'KSEA 081753Z 00000KT 10SM FEW022 SCT050 BKN130 07/04 A3025',
    'variable_wind': 'KATL 081752Z VRB05KT 10SM FEW250 18/M03 A3020',
    'light_rain': 'KORD 081756Z 18010KT 10SM -RA SCT035 BKN055 OVC095 12/08 A2995',
}
