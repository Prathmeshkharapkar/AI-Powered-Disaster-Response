import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def load_weather_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None


def cluster_risk_zones(df, n_clusters=3):
    # Normalize temperature_c for clustering
    df["temperature_c_normalized"] = (
        df["temperature_c"] - df["temperature_c"].mean()
    ) / df["temperature_c"].std()
    
    # Use normalized temperature for clustering
    features = ["temperature_c_normalized", "humidity", "wind_speed_kph", "precipitation_mm"]
    X = df[features].fillna(0)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["risk_zone"] = kmeans.fit_predict(X)
    df["risk_level"] = df["risk_zone"].map({0: "Low", 1: "Medium", 2: "High"})
    
    return df


def allocate_resources(df, available_resources):
    # Define resources (example: can be loaded from config or API)
    resources = {
        'ambulances': available_resources.get('ambulances', 20),
        'shelters': available_resources.get('shelters', 10),
        'rescue_teams': available_resources.get('rescue_teams', 15)
    }
    
    # Sort by risk (High first)
    risk_priority = {'High': 3, 'Medium': 2, 'Low': 1}
    df['priority'] = df['risk_level'].map(risk_priority)
    df = df.sort_values('priority', ascending=False)
    
    # Greedy allocation: distribute proportionally
    total_priority = df['priority'].sum()
    for resource, quantity in resources.items():
        df[resource] = (df['priority'] / total_priority * quantity).round().astype(int)
    
    return df


def save_geojson(df, output_file):
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    gdf.to_file(output_file, driver="GeoJSON")
    print(f"GeoJSON saved to {output_file}")


def main():
    input_file = "preprocessed_weather_data.csv"
    output_csv = "clustered_risk_zones.csv"
    output_geojson = "clustered_risk_zones.geojson"
    
    df = load_weather_data(input_file)
    if df is None:
        return
    
    df = cluster_risk_zones(df)
    
    # Example available resources (can be dynamic/user input)
    available_resources = {'ambulances': 50, 'shelters': 20, 'rescue_teams': 30}
    df = allocate_resources(df, available_resources)
    
    df.to_csv(output_csv, index=False)
    print(f"Clustered data saved to {output_csv}")
    
    save_geojson(df, output_geojson)


if __name__ == "__main__":
    main()
