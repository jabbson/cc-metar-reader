// Main JavaScript for METAR Weather Reader

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('weather-form');
    const input = document.getElementById('icao-input');
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const weatherResults = document.getElementById('weather-results');
    const exampleCodes = document.querySelectorAll('.example-code');

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const icaoCode = input.value.trim().toUpperCase();

        if (!icaoCode || icaoCode.length !== 4) {
            showError('Please enter a valid 4-letter ICAO code');
            return;
        }

        await fetchWeather(icaoCode);
    });

    // Handle example code clicks
    exampleCodes.forEach(button => {
        button.addEventListener('click', async function() {
            const code = this.getAttribute('data-code');
            input.value = code;
            await fetchWeather(code);
        });
    });

    // Convert input to uppercase as user types
    input.addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });

    async function fetchWeather(icaoCode) {
        // Hide previous results and errors
        hideError();
        hideResults();
        showLoading();

        try {
            const response = await fetch(`/api/weather/${icaoCode}`);
            const data = await response.json();

            hideLoading();

            if (data.success) {
                displayWeather(data);
            } else {
                showError(data.error || 'Failed to fetch weather data');
            }
        } catch (error) {
            hideLoading();
            showError('Network error. Please check your connection and try again.');
            console.error('Fetch error:', error);
        }
    }

    function displayWeather(data) {
        // Display summary
        const summaryDiv = document.getElementById('weather-summary');
        summaryDiv.textContent = data.summary;

        // Display data table
        const tableBody = document.getElementById('weather-table-body');
        tableBody.innerHTML = '';

        for (const [key, value] of Object.entries(data.data)) {
            const row = document.createElement('tr');
            const keyCell = document.createElement('td');
            const valueCell = document.createElement('td');

            keyCell.textContent = key;
            keyCell.className = 'key-cell';
            valueCell.textContent = value;
            valueCell.className = 'value-cell';

            row.appendChild(keyCell);
            row.appendChild(valueCell);
            tableBody.appendChild(row);
        }

        // Display raw METAR
        const rawMetar = document.getElementById('raw-metar');
        rawMetar.textContent = data.raw_metar;

        // Show results
        showResults();
    }

    function showLoading() {
        loading.style.display = 'block';
        submitBtn.disabled = true;
    }

    function hideLoading() {
        loading.style.display = 'none';
        submitBtn.disabled = false;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function showResults() {
        weatherResults.style.display = 'block';
        // Smooth scroll to results
        weatherResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideResults() {
        weatherResults.style.display = 'none';
    }
});
