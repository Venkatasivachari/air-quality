
import os
import requests
import google.generativeai as genai # <-- Re-added AI library
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Configure APIs ---
try:
    OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
    # Configure the Gemini API
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    print("🔴 Critical Error: API keys not found in .env file.")
    exit()

# Helper function to get AQI description
def get_aqi_description(aqi):
    return {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}.get(aqi, "Unknown")

# --- The rules-based function has been removed ---

# --- Flask Routes ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')
    
@app.route('/api/get_pollution_data')
def get_pollution_data():
    """API endpoint to fetch data and generate AI precautions."""
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

        # --- Step 3: Generate AI Precautions using Gemini ---
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = (
            f"The current Air Quality Index (AQI) in {found_location_name} is {aqi}, which is classified as '{aqi_description}'. "
            "Generate a single, concise health precaution suitable for the general public based on this AQI level. "
            "The precaution should be a single sentence or a very short phrase. Do not use bullet points or headings."
        )
        
        ai_response = model.generate_content(prompt)
        # Add error handling for blocked responses
        precautions = ai_response.text if ai_response.parts else "AI suggestion could not be generated at this time."


        # --- Step 4: Assemble and Return Final JSON ---
        result = {
            "location": found_location_name,
            "aqi": aqi,
            "aqi_description": aqi_description,
            "components": components,
            "precautions": precautions # Use the suggestion from the AI
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)