# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib # For saving the model

print("--- Starting Model Training ---")

# --- Step 1: Load and Prepare Data ---
try:
    # Make sure your dataset is named 'AirQuality.csv'
    df = pd.read_csv('AirQuality.csv')
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: 'AirQuality.csv' not found. Please download the dataset and place it in the project folder.")
    exit()

# Let's focus on a few key pollutants for simplicity
df = df[['PM2.5', 'PM10', 'NO2', 'CO', 'SO2']].copy()

# Clean the data: drop rows with any missing values
df.dropna(inplace=True)
print(f"Dataset cleaned. Remaining rows: {len(df)}")


# --- Step 2: Create Precaution Labels ---
def get_precaution_for_pm25(pm25_level):
    """Assigns a health precaution based on the PM2.5 level."""
    if pm25_level <= 30:
        return "Air is clean. No need to worry."
    elif 31 <= pm25_level <= 60:
        return "Air is okay, but sensitive people should be careful."
    elif 61 <= pm25_level <= 90:
        return "Air is not good. Limit outdoor activities."
    elif 91 <= pm25_level <= 120:
        return "Air is bad. Try to stay indoors."
    elif 121 <= pm25_level <= 250:
        return "Air is very bad. Avoid going outside."
    elif pm25_level > 250:
        return "Air is dangerous. Stay indoors with clean air."
    else:
        return "Data not valid"


df['Precaution'] = df['PM2.5'].apply(get_precaution_for_pm25)
print("'Precaution' column created.")


# --- Step 3: Define Features (X) and Target (y) ---
features = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2']
target = 'Precaution'

X = df[features]
y = df[target]


# --- Step 4: Split Data into Training and Testing Sets ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Data split into training and testing sets.")


# --- Step 5: Train the Model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("Training the Random Forest model...")
model.fit(X_train, y_train)
print("Model training complete.")



predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model Accuracy: {accuracy * 100:.2f}%")


# --- Step 7: Save the Trained Model ---
model_filename = 'pollution_model.joblib'
joblib.dump(model, model_filename)
print(f"Model saved successfully as '{model_filename}'")