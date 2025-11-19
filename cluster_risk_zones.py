# import pandas as pd
# import geopandas as gpd
# from sklearn.cluster import KMeans
# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)


# def load_weather_data(file_path):
#     try:
#         df = pd.read_csv(file_path)
#         return df
#     except FileNotFoundError:
#         print(f"Error: {file_path} not found")
#         return None


# def cluster_risk_zones(df, n_clusters=3):
#     # Normalize temperature_c for clustering
#     df["temperature_c_normalized"] = (
#         df["temperature_c"] - df["temperature_c"].mean()
#     ) / df["temperature_c"].std()
    
#     # Use normalized temperature for clustering
#     features = ["temperature_c_normalized", "humidity", "wind_speed_kph", "precipitation_mm"]
#     X = df[features].fillna(0)
    
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#     df["risk_zone"] = kmeans.fit_predict(X)
#     df["risk_level"] = df["risk_zone"].map({0: "Low", 1: "Medium", 2: "High"})
    
#     return df


# def allocate_resources(df, available_resources):
#     # Define resources (example: can be loaded from config or API)
#     resources = {
#         'ambulances': available_resources.get('ambulances', 20),
#         'shelters': available_resources.get('shelters', 10),
#         'rescue_teams': available_resources.get('rescue_teams', 15)
#     }
    
#     # Sort by risk (High first)
#     risk_priority = {'High': 3, 'Medium': 2, 'Low': 1}
#     df['priority'] = df['risk_level'].map(risk_priority)
#     df = df.sort_values('priority', ascending=False)
    
#     # Greedy allocation: distribute proportionally
#     total_priority = df['priority'].sum()
#     for resource, quantity in resources.items():
#         df[resource] = (df['priority'] / total_priority * quantity).round().astype(int)
    
#     return df


# def save_geojson(df, output_file):
#     gdf = gpd.GeoDataFrame(
#         df,
#         geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
#         crs="EPSG:4326"
#     )
#     gdf.to_file(output_file, driver="GeoJSON")
#     print(f"GeoJSON saved to {output_file}")


# def main():
#     input_file = "preprocessed_weather_data.csv"
#     output_csv = "clustered_risk_zones.csv"
#     output_geojson = "clustered_risk_zones.geojson"
    
#     df = load_weather_data(input_file)
#     if df is None:
#         return
    
#     df = cluster_risk_zones(df)
    
#     # Example available resources (can be dynamic/user input)
#     available_resources = {'ambulances': 50, 'shelters': 20, 'rescue_teams': 30}
#     df = allocate_resources(df, available_resources)
    
#     df.to_csv(output_csv, index=False)
#     print(f"Clustered data saved to {output_csv}")
    
#     save_geojson(df, output_geojson)


# if __name__ == "__main__":
#     main()


#dynamic



import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np


def load_weather_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None


def compute_composite_risk_score(df):
    features = ['temperature_c', 'humidity', 'wind_speed_kph', 'precipitation_mm']
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features].fillna(0))
    weights = np.array([0.4, 0.2, 0.2, 0.2])
    df['risk_score'] = np.dot(scaled_features, weights)
    return df


def cluster_risk_zones(df, n_clusters=3):
    df = compute_composite_risk_score(df)
    
    # Use composite risk score and features for clustering
    features = ['risk_score', 'temperature_c', 'humidity', 'wind_speed_kph', 'precipitation_mm']
    X = df[features].fillna(0)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['risk_zone'] = kmeans.fit_predict(X)
    
    # Map clusters to risk levels by average risk_score in cluster
    cluster_risk = df.groupby('risk_zone')['risk_score'].mean().sort_values()
    risk_level_map = {}
    risk_levels = ['Low', 'Medium', 'High']
    for i, cluster in enumerate(cluster_risk.index):
        risk_level_map[cluster] = risk_levels[min(i, len(risk_levels)-1)]
    df['risk_level'] = df['risk_zone'].map(risk_level_map)
    return df


def identify_safe_zones_near_cities(df, distance_km=20):
    """
    For each city, identify ONE safe zone nearby in the safest direction
    based on weather data analysis.
    
    Args:
        df: DataFrame with city risk data
        distance_km: Distance in km to place safe zone from city center
    
    Returns:
        DataFrame with safe zones (one per city)
    """
    safe_zones = []
    
    # Conversion factor: 1 degree ≈ 111 km
    distance_deg = distance_km / 111.0
    
    # Directions to check (N, NE, E, SE, S, SW, W, NW)
    directions = [
        (0, distance_deg, 'North'),
        (distance_deg * 0.707, distance_deg * 0.707, 'NorthEast'),
        (distance_deg, 0, 'East'),
        (distance_deg * 0.707, -distance_deg * 0.707, 'SouthEast'),
        (0, -distance_deg, 'South'),
        (-distance_deg * 0.707, -distance_deg * 0.707, 'SouthWest'),
        (-distance_deg, 0, 'West'),
        (-distance_deg * 0.707, distance_deg * 0.707, 'NorthWest')
    ]
    
    for idx, city_row in df.iterrows():
        city_name = city_row['city']
        city_lon = city_row['longitude']
        city_lat = city_row['latitude']
        city_risk = city_row['risk_score']
        
        # Analyze weather patterns to determine safest direction
        # Lower temperature, lower wind, lower precipitation = safer
        best_direction = None
        lowest_risk = float('inf')
        best_coords = None
        
        # Check each direction
        for lon_offset, lat_offset, direction_name in directions:
            safe_lon = city_lon + lon_offset
            safe_lat = city_lat + lat_offset
            
            # Calculate estimated risk in that direction
            # Use inverse of city risk with some randomness for directionality
            # In real scenario, you'd query actual weather data at those coordinates
            
            # Simple heuristic: areas opposite to wind direction are safer
            wind_factor = 1.0
            if city_row['wind_speed_kph'] > 20:  # High wind
                # Prefer perpendicular directions to wind
                wind_factor = 0.8
            
            # Lower precipitation areas are safer
            precip_factor = 1.0 - (city_row['precipitation_mm'] / 100.0)
            precip_factor = max(0.5, min(1.0, precip_factor))
            
            # Calculate directional risk score
            directional_risk = city_risk * wind_factor * precip_factor
            
            # Add slight preference for certain directions based on weather
            if city_row['temperature_c'] > 30:  # Hot weather
                # Prefer north/northeast (cooler)
                if 'North' in direction_name or 'East' in direction_name:
                    directional_risk *= 0.9
            
            if city_row['precipitation_mm'] > 50:  # Heavy rain
                # Prefer elevated areas (assume east/northeast)
                if 'East' in direction_name or 'North' in direction_name:
                    directional_risk *= 0.85
            
            if directional_risk < lowest_risk:
                lowest_risk = directional_risk
                best_direction = direction_name
                best_coords = (safe_lon, safe_lat)
        
        # Create safe zone entry
        safe_zone = {
            'city': city_name,
            'safe_zone_id': f"SafeZone_{city_name}",
            'longitude': best_coords[0],
            'latitude': best_coords[1],
            'risk_score': lowest_risk,
            'direction': best_direction,
            'distance_km': distance_km
        }
        safe_zones.append(safe_zone)
        print(f"Safe zone for {city_name}: {best_direction} direction, risk score: {lowest_risk:.2f}")
    
    safe_zones_df = pd.DataFrame(safe_zones)
    print(f"\nIdentified {len(safe_zones_df)} safe zones (one per city)")
    return safe_zones_df


def allocate_resources(df, available_resources):
    resources = {
        'ambulances': available_resources.get('ambulances', 20),
        'shelters': available_resources.get('shelters', 10),
        'rescue_teams': available_resources.get('rescue_teams', 15)
    }
    risk_priority = {'High': 3, 'Medium': 2, 'Low': 1}
    df['priority'] = df['risk_level'].map(risk_priority)
    df = df.sort_values('priority', ascending=False)
    total_priority = df['priority'].sum()
    if total_priority > 0:
        for resource, quantity in resources.items():
            df[resource] = (df['priority'] / total_priority * quantity).round().astype(int)
    return df


def save_geojson(gdf, output_file):
    gdf.to_file(output_file, driver="GeoJSON")
    print(f"GeoJSON saved to {output_file}")


def main():
    input_file = "preprocessed_weather_data.csv"
    output_csv = "clustered_risk_zones.csv"
    output_risk_geojson = "clustered_risk_zones.geojson"
    output_safe_zones_geojson = "safe_zones.geojson"
    
    df = load_weather_data(input_file)
    if df is None:
        return
    
    df = cluster_risk_zones(df)
    
    available_resources = {'ambulances': 50, 'shelters': 20, 'rescue_teams': 30}
    df = allocate_resources(df, available_resources)
    
    df.to_csv(output_csv, index=False)
    print(f"Clustered data saved to {output_csv}")
    
    # Save risk zones as GeoJSON
    risk_gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
        crs="EPSG:4326"
    )
    save_geojson(risk_gdf, output_risk_geojson)
    
    # Identify and save safe zones (one per city, nearby)
    safe_zones = identify_safe_zones_near_cities(df, distance_km=20)
    if not safe_zones.empty:
        safe_zone_gdf = gpd.GeoDataFrame(
            safe_zones,
            geometry=gpd.points_from_xy(safe_zones['longitude'], safe_zones['latitude']),
            crs="EPSG:4326"
        )
        save_geojson(safe_zone_gdf, output_safe_zones_geojson)
    else:
        print("No safe zones detected.")


if __name__ == '__main__':
    main()

