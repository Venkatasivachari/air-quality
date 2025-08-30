// static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('location-form');
    const locationInput = document.getElementById('location-input');
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const location = locationInput.value.trim();
        if (!location) {
            alert('Please select a city.');
            return;
        }

        resultsContainer.style.display = 'none';
        resultsContainer.innerHTML = '';
        loader.style.display = 'block';

        try {
            const response = await fetch(`/api/get_pollution_data?location=${encodeURIComponent(location)}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An unknown error occurred.');
            }
            
            const data = await response.json();
            displayResults(data);

        } catch (error) {
            displayError(error.message);
        } finally {
            loader.style.display = 'none';
        }
    });

    function displayResults(data) {
        resultsContainer.className = '';
        resultsContainer.classList.add(`aqi-${data.aqi}`);

        // Health Precautions
        let precautionsHtml = '';
        if (data.precautions) {
            precautionsHtml = `
                <div class="precautions">
                    <h3>Health Precautions</h3>
                    <p>${data.precautions}</p>
                </div>
            `;
        }

        // Pollutant data
        const pollutantsHtml = Object.entries(data.components).map(([key, value]) => `
            <div class="pollutant-card">
                <strong>${key.replace('_', '.').toUpperCase()}</strong>
                <span>${value}</span>
            </div>
        `).join('');

        // Chart Containers (reduced size + stacked layout)
        const chartHtml = `
            <div class="charts">
                <canvas id="pollutantsPieChart" width="350" height="350"></canvas>
                <canvas id="pollutantsBarChart" width="400" height="300"></canvas>
            </div>
        `;

        resultsContainer.innerHTML = `
            <h2>${data.location}</h2>
            <p><strong>Overall Air Quality: ${data.aqi_description} (AQI: ${data.aqi})</strong></p>

            <h3>Pollutant Levels (µg/m³)</h3>
            <div class="pollutants">${pollutantsHtml}</div>

            ${chartHtml}
            ${precautionsHtml}
        `;

        resultsContainer.style.display = 'block';

        // --- CHARTS ---
        const ctxPie = document.getElementById('pollutantsPieChart').getContext('2d');
        const ctxBar = document.getElementById('pollutantsBarChart').getContext('2d');

        const labels = Object.keys(data.components).map(key => key.replace('_', '.').toUpperCase());
        const values = Object.values(data.components);

        // Pie Chart with percentages
        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#8BC34A', '#FF9800', '#9C27B0']
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} µg/m³ (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        // Bar Chart (stacked neatly below pie)
        // Bar Chart (stacked neatly below pie)
    new Chart(ctxBar, {
        type: 'bar',
        data: {
        labels: labels,
        datasets: [{
            label: 'Pollutant Levels (µg/m³)',
            data: values,
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#8BC34A', '#FF9800', '#9C27B0'
            ]
        }]
    },
    options: {
        responsive: false,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

    }

    function displayError(message) {
        resultsContainer.innerHTML = `<p style="color: red; text-align: center;">Error: ${message}</p>`;
        resultsContainer.style.display = 'block';
        resultsContainer.className = '';
    }
});
