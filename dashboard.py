# import streamlit as st
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# import os
# import glob
# import time
# import subprocess

# st.set_page_config(page_title="Disaster Response Dashboard", layout="wide")

# def load_geojson(file_path):
#     if not os.path.exists(file_path):
#         st.error(f"GeoJSON file not found: {file_path}")
#         return None
#     try:
#         gdf = gpd.read_file(file_path)
#         return gdf
#     except Exception as e:
#         st.error(f"Error loading GeoJSON: {file_path}: {e}")
#         return None

# def create_map(risk_gdf, route_gdfs, selected_cities, disaster_focus):
#     center_lat = risk_gdf["latitude"].mean()
#     center_lon = risk_gdf["longitude"].mean()
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
#     color_map = {"Low": "green", "Medium": "orange", "High": "red"}

#     destination_points = {
#         "New York": (-73.8, 40.8, "Safe Zone NY"),
#         "Los Angeles": (-118.1, 34.1, "Safe Zone LA"),
#         "Miami": (-80.3, 25.8, "Safe Zone Miami"),
#         "Mumbai": (72.9, 19.1, "Safe Zone Mumbai"),
#         "Pune": (73.8, 18.6, "Safe Zone Pune"),
#         "Bangalore": (77.6, 13.0, "Safe Zone Bangalore"),
#         "Hyderabad": (78.5, 17.4, "Safe Zone Hyderabad")
#     }

#     # Filter risk data
#     risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
#     for _, row in risk_gdf_filtered.iterrows():
#         folium.CircleMarker(
#             location=[row["latitude"], row["longitude"]],
#             radius=10,
#             color=color_map.get(row["risk_level"], "blue"),
#             fill=True,
#             fill_color=color_map.get(row["risk_level"], "blue"),
#             fill_opacity=0.7,
#             popup=(
#                 f"City: {row['city']}<br>"
#                 f"Risk Level: {row['risk_level']}<br>"
#                 f"Temperature: {row['temperature_c']:.1f}°C<br>"
#                 f"Humidity: {row['humidity']*100:.0f}%<br>"
#                 f"Wind Speed: {row['wind_speed_kph']:.1f} kph<br>"
#                 f"Precipitation: {row['precipitation_mm']:.1f} mm<br>"
#                 f"Alert Level: {row.get('alert_level', 'None')}<br>"
#                 f"Alert Type: {row.get('alert_type', 'None')}<br>"
#                 f"Social Reports: {row.get('social_reports', 0)}<br>"
#                 f"Urgency Score: {row.get('urgency_score', 0):.2f}"
#             )
#         ).add_to(m)
    
#     # Filter and display routes, ensuring they end at safe zone
#     for route_gdf in route_gdfs:
#         if route_gdf is not None:
#             for _, row in route_gdf.iterrows():
#                 city = row.get("city", "Unknown")
#                 if city in selected_cities and city in destination_points:
#                     coords = [(lat, lon) for lon, lat in row["geometry"].coords]  # Swapped lat/lon for Folium
#                     safe_lat, safe_lon = destination_points[city][1], destination_points[city][0]
#                     safe_zone_name = destination_points[city][2]
#                     # Append safe zone coord if not already the endpoint (for precision)
#                     if coords and (coords[-1] != (safe_lat, safe_lon)):
#                         coords.append((safe_lat, safe_lon))
#                     folium.PolyLine(
#                         locations=coords,
#                         color="blue",
#                         weight=5,
#                         popup=f"Evacuation Route: {city} to {safe_zone_name} (Focus: {disaster_focus})"
#                     ).add_to(m)
    
#     # Add safe zone markers for selected cities
#     for city, (lon, lat, name) in destination_points.items():
#         if city in selected_cities:
#             folium.Marker(
#                 location=[lat, lon],
#                 icon=folium.Icon(color="green", icon="info-sign"),
#                 popup=f"Safe Zone: {name}"
#             ).add_to(m)

#     return m

# def update_weather_data():
#     subprocess.run(["python", "fetch_weather_data.py"])

# def main():
#     st.title("AI-Powered Disaster Response Dashboard")
#     st.markdown("Visualizing risk zones and evacuation routes for disaster response.")

#     if 'last_update' not in st.session_state:
#         st.session_state.last_update = time.time()

#     if time.time() - st.session_state.last_update > 1800:  # 30 minutes in seconds
#         update_weather_data()
#         st.session_state.last_update = time.time()
#         st.experimental_rerun()

#     risk_geojson = "clustered_risk_zones.geojson"
#     risk_gdf = load_geojson(risk_geojson)
#     if risk_gdf is None:
#         return

#     route_files = glob.glob("evacuation_route_*.geojson")
#     route_gdfs = [load_geojson(f) for f in route_files]
#     route_gdfs = [gdf for gdf in route_gdfs if gdf is not None]

#     # Dynamically populate cities from risk_gdf
#     all_cities = risk_gdf["city"].unique().tolist()
#     if not all_cities:
#         st.error("No cities found in risk data.")
#         return
#     selected_cities = st.multiselect("Select Cities", all_cities)

#     disaster_focus = st.radio("Disaster Focus", ["All", "Floods", "Cyclones", "Earthquakes"], index=0)

#     st.subheader("Risk Zones and Evacuation Routes")
#     folium_map = create_map(risk_gdf, route_gdfs, selected_cities, disaster_focus)
#     st_folium(folium_map, width=700, height=500)

#     st.subheader("Weather, Risk, Alerts, and Social Data")
#     possible_cols = ["city", "timestamp", "temperature_c", "humidity", "wind_speed_kph", 
#                      "precipitation_mm", "weather_condition", "risk_level",
#                      "alert_level", "alert_type", "alert_description", 
#                      "social_reports", "urgency_score"]
#     # Filter to only existing columns to avoid KeyError
#     display_cols = [col for col in possible_cols if col in risk_gdf.columns]
#     risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
#     st.dataframe(risk_gdf_filtered[display_cols])

# if __name__ == "__main__":
#     main()

#for dynamic



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

def create_map(risk_gdf, safe_zones_gdf, route_gdfs, selected_cities, disaster_focus):
    center_lat = risk_gdf["latitude"].mean()
    center_lon = risk_gdf["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    color_map = {"Low": "green", "Medium": "orange", "High": "red"}

    # Filter risk data by selected cities
    risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
    for _, row in risk_gdf_filtered.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=12,
            color=color_map.get(row["risk_level"], "blue"),
            fill=True,
            fill_color=color_map.get(row["risk_level"], "blue"),
            fill_opacity=0.7,
            popup=(
                f"<b>🏙️ City: {row['city']}</b><br>"
                f"Risk Level: {row['risk_level']}<br>"
                f"Temperature: {row['temperature_c']:.1f}°C<br>"
                f"Humidity: {row['humidity']*100:.0f}%<br>"
                f"Wind Speed: {row['wind_speed_kph']:.1f} kph<br>"
                f"Precipitation: {row['precipitation_mm']:.1f} mm<br>"
                f"Alert Level: {row.get('alert_level', 'None')}<br>"
                f"Alert Type: {row.get('alert_type', 'None')}<br>"
                f"Risk Score: {row.get('risk_score', 0):.2f}"
            ),
            tooltip=f"{row['city']} - {row['risk_level']} Risk"
        ).add_to(m)
    
    # Display ROUTES FIRST (so they appear under markers)
    route_count = 0
    if route_gdfs:
        for route_gdf in route_gdfs:
            if route_gdf is not None and 'city' in route_gdf.columns:
                routes_filtered = route_gdf[route_gdf["city"].isin(selected_cities)]
                for _, row in routes_filtered.iterrows():
                    city = row.get("city", "Unknown")
                    coords = [(lat, lon) for lon, lat in row["geometry"].coords]
                    
                    # Main evacuation route - thick blue line
                    folium.PolyLine(
                        locations=coords,
                        color="#0066FF",
                        weight=6,
                        opacity=0.8,
                        popup=f"<b>🚨 Evacuation Route</b><br>From: {city}<br>To: SafeZone_{city}",
                        tooltip=f"Route: {city} → Safe Zone"
                    ).add_to(m)
                    
                    # Add directional arrows along the route
                    if len(coords) >= 2:
                        mid_point = coords[len(coords)//2]
                        folium.Marker(
                            location=mid_point,
                            icon=folium.Icon(color="blue", icon="arrow-right", prefix='fa'),
                            popup=f"Direction: {city} → Safe Zone"
                        ).add_to(m)
                    
                    route_count += 1
    
    # Filter safe zones by selected cities
    if not safe_zones_gdf.empty and 'city' in safe_zones_gdf.columns:
        safe_zones_filtered = safe_zones_gdf[safe_zones_gdf["city"].isin(selected_cities)]
        for _, row in safe_zones_filtered.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.Icon(color="green", icon="home", prefix='fa'),
                popup=(
                    f"<b>✅ Safe Zone: {row.get('safe_zone_id', 'Unknown')}</b><br>"
                    f"City: {row.get('city', 'Unknown')}<br>"
                    f"Direction: {row.get('direction', 'N/A')}<br>"
                    f"Distance: {row.get('distance_km', 0):.1f} km<br>"
                    f"Risk Score: {row.get('risk_score', 0):.2f}<br>"
                    f"Coordinates: ({row['latitude']:.4f}, {row['longitude']:.4f})"
                ),
                tooltip=f"Safe Zone for {row.get('city', 'Unknown')}"
            ).add_to(m)
    
    # Add legend
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; height: auto; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
        <p style="margin:0; font-weight:bold;">Legend</p>
        <p style="margin:5px 0;"><span style="color:red;">⬤</span> High Risk Zone</p>
        <p style="margin:5px 0;"><span style="color:orange;">⬤</span> Medium Risk Zone</p>
        <p style="margin:5px 0;"><span style="color:green;">⬤</span> Low Risk Zone</p>
        <p style="margin:5px 0;"><span style="color:#0066FF;">━━</span> Evacuation Route</p>
        <p style="margin:5px 0;">🏠 Safe Zone</p>
        <p style="margin:5px 0; font-size:12px; color:grey;">Routes shown: {route_count}</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

def update_weather_data():
    subprocess.run(["python", "fetch_weather_data.py"])

def main():
    st.title("🚨 AI-Powered Disaster Response")
    st.markdown("Visualizing risk zones, safe zones, and **evacuation routes** for disaster response.")

    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()

    if time.time() - st.session_state.last_update > 1800:  # 30 minutes
        update_weather_data()
        st.session_state.last_update = time.time()
        st.rerun()

    risk_geojson = "clustered_risk_zones.geojson"
    risk_gdf = load_geojson(risk_geojson)
    if risk_gdf is None:
        return

    # Load AI-identified safe zones
    safe_zones_file = "safe_zones.geojson"
    safe_zones_gdf = load_geojson(safe_zones_file)
    if safe_zones_gdf is None:
        safe_zones_gdf = gpd.GeoDataFrame(columns=['safe_zone_id', 'city', 'latitude', 'longitude', 'risk_score'])
        st.warning("⚠️ No safe zones identified yet. Run cluster_risk_zones.py first.")

    # Load evacuation routes
    route_files = glob.glob("dynamic_evacuation_routes.geojson")
    if not route_files:
        route_files = glob.glob("evacuation_route_*.geojson")
    route_gdfs = [load_geojson(f) for f in route_files]
    route_gdfs = [gdf for gdf in route_gdfs if gdf is not None]
    
    if not route_gdfs or all(gdf.empty for gdf in route_gdfs):
        st.warning("⚠️ No evacuation routes found. Run optimize_routes.py to generate routes.")

    # Dynamically populate cities from risk_gdf
    all_cities = risk_gdf["city"].unique().tolist()
    if not all_cities:
        st.error("No cities found in risk data.")
        return
    
    # Sidebar controls
    st.sidebar.header("🎛️ Controls")
    selected_cities = st.sidebar.multiselect(
        "Select Cities to Display", 
        all_cities, 
        default=all_cities,
        help="Select specific cities to view their risk zones, safe zones, and evacuation routes"
    )
    
    if not selected_cities:
        st.warning("⚠️ Please select at least one city to display.")
        return

    disaster_focus = st.sidebar.radio("Disaster Focus", ["All", "Floods", "Cyclones", "Earthquakes"], index=0)
    
    # Show route statistics
    if route_gdfs and route_gdfs[0] is not None:
        total_routes = len(route_gdfs[0])
        selected_routes = len(route_gdfs[0][route_gdfs[0]['city'].isin(selected_cities)]) if 'city' in route_gdfs[0].columns else 0
        st.sidebar.info(f"📍 Total Cities: {len(all_cities)}\n\n🛣️ Routes Displayed: {selected_routes}/{total_routes}")

    st.subheader("🗺️ Interactive Map: Risk Zones, Safe Zones & Evacuation Routes")
    folium_map = create_map(risk_gdf, safe_zones_gdf, route_gdfs, selected_cities, disaster_focus)
    st_folium(folium_map, width=1200, height=600)

    # Display safe zones info for selected cities only
    st.subheader(f"✅ AI-Identified Safe Zones for Selected Cities")
    if not safe_zones_gdf.empty:
        if 'city' in safe_zones_gdf.columns:
            safe_zones_filtered = safe_zones_gdf[safe_zones_gdf['city'].isin(selected_cities)]
            if not safe_zones_filtered.empty:
                safe_display_cols = [col for col in ['city', 'safe_zone_id', 'direction', 'distance_km', 
                                                       'latitude', 'longitude', 'risk_score'] 
                                    if col in safe_zones_filtered.columns]
                st.dataframe(safe_zones_filtered[safe_display_cols], use_container_width=True)
            else:
                st.info(f"No safe zones for selected cities: {', '.join(selected_cities)}")
        else:
            st.info("Safe zone data does not contain city information.")
    else:
        st.info("No safe zones detected. Run clustering to identify safe zones.")

    st.subheader(f"📊 Weather, Risk & Alerts Data for Selected Cities")
    possible_cols = ["city", "timestamp", "temperature_c", "humidity", "wind_speed_kph", 
                     "precipitation_mm", "weather_condition", "risk_level", "risk_score",
                     "alert_level", "alert_type", "alert_description"]
    display_cols = [col for col in possible_cols if col in risk_gdf.columns]
    risk_gdf_filtered = risk_gdf[risk_gdf["city"].isin(selected_cities)]
    st.dataframe(risk_gdf_filtered[display_cols], use_container_width=True)

if __name__ == "__main__":
    main()
