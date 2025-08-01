

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WEATHERAPI_KEY")
print(f"API Key: {API_KEY}")

# Base URL for WeatherAPI.com
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def fetch_weather_data(city, api_key):
    if not api_key:
        print(f"No API key provided for {city}")
        return None
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        print(f"Raw response for {city}: {str(response.json())[:100]}...")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {city}: {e}")
        return None

# New function for public alerts
def fetch_public_alerts(city, api_url="https://www.gdacs.org/API/v1/alerts"):
    try:
        response = requests.get(api_url, params={"location": city})
        response.raise_for_status()
        alerts = response.json().get("alerts", [])
        if alerts:
            # Extract key info from the first active alert
            alert = alerts[0]
            return {
                "alert_level": alert.get("severity", "Unknown"),
                "alert_type": alert.get("eventtype", "Unknown"),
                "alert_description": alert.get("description", "")
            }
        return {"alert_level": "None", "alert_type": "None", "alert_description": ""}
    except Exception as e:
        print(f"Error fetching alerts for {city}: {e}")
        return {"alert_level": "None", "alert_type": "None", "alert_description": ""}

# Update preprocess_weather_data to include alerts
def preprocess_weather_data(weather_json, alerts):
    if not weather_json or "error" in weather_json:
        print(f"Invalid JSON or error in response: {weather_json}")
        return None
    
    data = {
        "city": weather_json["location"]["name"],
        "timestamp": weather_json["location"]["localtime"],
        "latitude": weather_json["location"]["lat"],
        "longitude": weather_json["location"]["lon"],
        "temperature_c": weather_json["current"]["temp_c"],
        "humidity": weather_json["current"]["humidity"],
        "pressure_mb": weather_json["current"]["pressure_mb"],
        "wind_speed_kph": weather_json["current"]["wind_kph"],
        "weather_condition": weather_json["current"]["condition"]["text"],
        "precipitation_mm": weather_json["current"]["precip_mm"],
        "alert_level": alerts["alert_level"],
        "alert_type": alerts["alert_type"],
        "alert_description": alerts["alert_description"]
    }
    
    df = pd.DataFrame([data])
    
    df["humidity"] = df["humidity"] / 100
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0)
    
    return df

def main():
    cities = ["New York", "Los Angeles", "Miami", "Mumbai", "Pune", "Bangalore", "Hyderabad"]
    all_data = pd.DataFrame()
    
    for city in cities:
        print(f"Fetching data for {city}...")
        weather_json = fetch_weather_data(city, API_KEY)
        alerts = fetch_public_alerts(city)  # Fetch public alerts for the city
        if weather_json:
            df = preprocess_weather_data(weather_json, alerts)
            if df is not None:
                print(f"Data for {city}:\n{df.to_string()}\n")
                all_data = pd.concat([all_data, df], ignore_index=True)
    
    if not all_data.empty:
        print(f"Combined DataFrame:\n{all_data.to_string()}\n")
        if len(all_data) > 1:
            all_data["temperature_c"] = (
                all_data["temperature_c"] - all_data["temperature_c"].mean()
            ) / all_data["temperature_c"].std()
        output_file = "preprocessed_weather_data.csv"
        try:
            all_data.to_csv(output_file, index=False)
            print(f"Data saved to {output_file}")
        except PermissionError as e:
            print(f"PermissionError: {e}. Try saving to a different file or running as administrator.")
    else:
        print("No data to save.")

if __name__ == "__main__":
    main()
