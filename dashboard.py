import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import glob
import time
import subprocess

st.set_page_config(page_title="Disaster Response Dashboard", layout="wide")

def load_geojson(file_path):
    if not os.path.exists(file_path):
        st.error(f"GeoJSON file not found: {file_path}")
        return None
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON: {file_path}: {e}")
        return None

def create_map(risk_gdf, route_gdfs, selected_cities, disaster_focus):
    center_lat = risk_gdf["latitude"].mean()
    center_lon = risk_gdf["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
    color_map = {"Low": "green", "Medium": "orange", "High": "red"}

    destination_points = {
        "New York": (-73.8, 40.8, "Safe Zone NY"),
        "Los Angeles": (-118.1, 34.1, "Safe Zone LA"),
        "Miami": (-80.3, 25.8, "Safe Zone Miami"),
        "Mumbai": (72.9, 19.1, "Safe Zone Mumbai"),
        "Pune": (73.8, 18.6, "Safe Zone Pune"),
        "Bangalore": (77.6, 13.0, "Safe Zone Bangalore"),
        "Hyderabad": (78.5, 17.4, "Safe Zone Hyderabad")
    }

    # Filter risk data
    risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
    for _, row in risk_gdf_filtered.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=10,
            color=color_map.get(row["risk_level"], "blue"),
            fill=True,
            fill_color=color_map.get(row["risk_level"], "blue"),
            fill_opacity=0.7,
            popup=(
                f"City: {row['city']}<br>"
                f"Risk Level: {row['risk_level']}<br>"
                f"Temperature: {row['temperature_c']:.1f}°C<br>"
                f"Humidity: {row['humidity']*100:.0f}%<br>"
                f"Wind Speed: {row['wind_speed_kph']:.1f} kph<br>"
                f"Precipitation: {row['precipitation_mm']:.1f} mm<br>"
                f"Alert Level: {row.get('alert_level', 'None')}<br>"
                f"Alert Type: {row.get('alert_type', 'None')}<br>"
                f"Social Reports: {row.get('social_reports', 0)}<br>"
                f"Urgency Score: {row.get('urgency_score', 0):.2f}"
            )
        ).add_to(m)
    
    # Filter and display routes, ensuring they end at safe zone
    for route_gdf in route_gdfs:
        if route_gdf is not None:
            for _, row in route_gdf.iterrows():
                city = row.get("city", "Unknown")
                if city in selected_cities and city in destination_points:
                    coords = [(lat, lon) for lon, lat in row["geometry"].coords]  # Swapped lat/lon for Folium
                    safe_lat, safe_lon = destination_points[city][1], destination_points[city][0]
                    safe_zone_name = destination_points[city][2]
                    # Append safe zone coord if not already the endpoint (for precision)
                    if coords and (coords[-1] != (safe_lat, safe_lon)):
                        coords.append((safe_lat, safe_lon))
                    folium.PolyLine(
                        locations=coords,
                        color="blue",
                        weight=5,
                        popup=f"Evacuation Route: {city} to {safe_zone_name} (Focus: {disaster_focus})"
                    ).add_to(m)
    
    # Add safe zone markers for selected cities
    for city, (lon, lat, name) in destination_points.items():
        if city in selected_cities:
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="green", icon="info-sign"),
                popup=f"Safe Zone: {name}"
            ).add_to(m)

    return m

def update_weather_data():
    subprocess.run(["python", "fetch_weather_data.py"])

def main():
    st.title("AI-Powered Disaster Response Dashboard")
    st.markdown("Visualizing risk zones and evacuation routes for disaster response.")

    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()

    if time.time() - st.session_state.last_update > 1800:  # 30 minutes in seconds
        update_weather_data()
        st.session_state.last_update = time.time()
        st.experimental_rerun()

    risk_geojson = "clustered_risk_zones.geojson"
    risk_gdf = load_geojson(risk_geojson)
    if risk_gdf is None:
        return

    route_files = glob.glob("evacuation_route_*.geojson")
    route_gdfs = [load_geojson(f) for f in route_files]
    route_gdfs = [gdf for gdf in route_gdfs if gdf is not None]

    # Dynamically populate cities from risk_gdf
    all_cities = risk_gdf["city"].unique().tolist()
    if not all_cities:
        st.error("No cities found in risk data.")
        return
    selected_cities = st.multiselect("Select Cities", all_cities)

    disaster_focus = st.radio("Disaster Focus", ["All", "Floods", "Cyclones", "Earthquakes"], index=0)

    st.subheader("Risk Zones and Evacuation Routes")
    folium_map = create_map(risk_gdf, route_gdfs, selected_cities, disaster_focus)
    st_folium(folium_map, width=700, height=500)

    st.subheader("Weather, Risk, Alerts, and Social Data")
    possible_cols = ["city", "timestamp", "temperature_c", "humidity", "wind_speed_kph", 
                     "precipitation_mm", "weather_condition", "risk_level",
                     "alert_level", "alert_type", "alert_description", 
                     "social_reports", "urgency_score"]
    # Filter to only existing columns to avoid KeyError
    display_cols = [col for col in possible_cols if col in risk_gdf.columns]
    risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
    st.dataframe(risk_gdf_filtered[display_cols])

if __name__ == "__main__":
    main()
