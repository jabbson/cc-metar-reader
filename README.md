# METAR Weather Reader

A Flask web application that decodes aviation METAR weather reports and presents them in plain English for non-pilots.

## Features

- Enter any airport ICAO code (e.g., KHIO, KJFK, KSEA)
- Fetches current METAR data from aviationweather.gov
- Decodes technical aviation weather format
- Displays weather in plain English summary
- Shows detailed weather data in a clear table format
- Real-time updates without page reload

## Decoded Information

- Location (airport code)
- Weather conditions (clear, rain, snow, etc.)
- Temperature (Fahrenheit and Celsius)
- Wind direction and speed
- Visibility
- Atmospheric pressure
- Sky conditions

## Setup

1. Clone the repository:
```bash
cd /Users/jabbson/Projects/claude/cc-metar-reader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5555
```

3. Enter a 4-letter ICAO airport code and click "Get Weather"

## Example Airport Codes

- **KHIO** - Portland-Hillsboro Airport, Oregon
- **KJFK** - John F. Kennedy International Airport, New York
- **KSEA** - Seattle-Tacoma International Airport, Washington
- **EGLL** - London Heathrow Airport, United Kingdom
- **LFPG** - Paris Charles de Gaulle Airport, France

## How It Works

1. User enters an ICAO airport code
2. Application fetches the latest METAR report from aviationweather.gov
3. METAR string is parsed using the python-metar library
4. Weather data is converted to human-readable format
5. Results are displayed as both a plain English summary and a detailed table

## Technology Stack

- **Backend**: Flask (Python web framework)
- **METAR Parsing**: python-metar library
- **API**: aviationweather.gov public API
- **Frontend**: HTML, CSS, JavaScript (vanilla)

## Project Structure

```
cc-metar-reader/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── .coveragerc            # Coverage configuration
├── services/              # Business logic
│   ├── metar_fetcher.py  # API integration
│   └── metar_parser.py   # METAR decoding
├── utils/                 # Helper functions
│   └── formatters.py     # Human-readable formatting
├── templates/             # HTML templates
│   ├── base.html
│   └── index.html
├── static/                # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── tests/                 # Test suite
    ├── conftest.py        # Pytest fixtures
    ├── test_app.py        # Flask route tests
    ├── test_metar_parser.py  # Parser tests
    └── test_formatters.py # Formatter tests
```

## Testing

The application includes a comprehensive test suite with 67 tests covering all major functionality.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py -v

# Run specific test class
pytest tests/test_app.py::TestWeatherAPI -v
```

### Test Coverage

- **67 tests** across 3 test modules
- **85.25%** code coverage
- Tests use real METAR strings for authentic parsing validation
- Mocked external API calls for fast, reliable testing

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and sample METARs
├── test_app.py              # Flask route and API endpoint tests (11 tests)
├── test_metar_parser.py     # METAR parsing with real data (19 tests)
└── test_formatters.py       # Human-readable formatting tests (37 tests)
```

### Test Categories

- **Route Tests**: Home page, API endpoints, error handling
- **Parser Tests**: Real METAR strings (clear, rain, snow, fog, thunderstorms)
- **Formatter Tests**: Temperature, wind, visibility, pressure, sky conditions
- **Edge Cases**: Invalid inputs, missing data, extreme weather

### Viewing Coverage Report

After running tests with coverage, open the HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Production Deployment

For production environments, follow these best practices:

1. **Disable Debug Mode**: Set the `FLASK_DEBUG` environment variable to control debug mode:
```bash
export FLASK_DEBUG=False  # or unset it (defaults to False)
python app.py
```

2. **Use a Production Server**: Instead of the Flask development server, use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5555 app:app
```

3. **Enable HTTPS**: Use a reverse proxy like Nginx with SSL certificates

4. **Environment Variables**: Consider using environment variables for sensitive configuration

5. **Logging**: Logs are written to stdout/stderr and can be redirected to files or logging services

## License

MIT
