
import os
import requests
# No longer need 'joblib' or 'pandas'
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv


load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)



try:
    OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
except KeyError:
    print("🔴 Critical Error: OPENWEATHER_API_KEY not found in .env file.")
    exit()

# Helper function to get AQI description
def get_aqi_description(aqi):
    return {1: "Good", 2: "Moderate", 3: "Fair", 4: "Poor", 5: "Very Poor"}.get(aqi, "Unknown")

# --- NEW: Rules-based function for precautions ---
def get_precaution_from_aqi(aqi):
    """Assigns a health precaution based on the overall AQI level."""
    if aqi == 1: # Good
        return "No precaution needed. It's a great day to be active outside!"
    elif aqi == 2: # Fair
        return "Sensitive groups should consider reducing prolonged or heavy outdoor exertion."
    elif aqi == 3: # Moderate
        return "Sensitive people may experience health effects. The general public should limit heavy outdoor work."
    elif aqi == 4: # Poor
        return "Health alert: Everyone may experience health effects. Avoid prolonged outdoor exertion."
    elif aqi == 5: # Very Poor
        return "Serious health warning. Everyone should avoid all outdoor activity."
    else:
        return "Precaution information not available."


# --- Flask Routes ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')
    
@app.route('/api/get_pollution_data')
def get_pollution_data():
    """API endpoint to fetch data and provide precautions based on overall AQI."""
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400

    try:
        # --- Step 1 & 2: Get Live Pollution Data (same as before) ---
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data:
            return jsonify({"error": "Location not found"}), 404
        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
        found_location_name = f"{geo_data[0]['name']}, {geo_data[0]['country']}"

        pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        pollution_response = requests.get(pollution_url)
        pollution_response.raise_for_status()
        pollution_data = pollution_response.json()['list'][0]
        aqi = pollution_data['main']['aqi']
        aqi_description = get_aqi_description(aqi)
        components = pollution_data['components']

        # --- Step 3: Get Precaution from Rules ---
        # This no longer uses the ML model. It uses the simple function above.
        precaution_text = get_precaution_from_aqi(aqi)

        # --- Step 4: Assemble and Return Final JSON ---
        result = {
            "location": found_location_name,
            "aqi": aqi,
            "aqi_description": aqi_description,
            "components": components,
            "precautions": precaution_text # Use the text from our rules-based function
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)