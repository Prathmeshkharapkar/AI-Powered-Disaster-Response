import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import LineString
import warnings
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=FutureWarning)
ox.settings.use_cache = True
ox.settings.log_console = True

# Load risk zones from GeoJSON
def load_risk_zones(file_path):
    try:
        gdf = gpd.read_file(file_path)
        logger.info(f"Loaded GeoJSON with columns: {list(gdf.columns)}")
        return gdf
    except Exception as e:
        logger.error(f"Error loading GeoJSON: {e}")
        return None

# Compute evacuation route for a single city
def compute_evacuation_route(gdf, city, destination_points):
    try:
        # Get city coordinates
        city_data = gdf[gdf["city"] == city][["latitude", "longitude", "risk_level"]]
        if city_data.empty:
            logger.error(f"No data found for city: {city}")
            return None, None
        
        lat, lon, risk_level = city_data.iloc[0][["latitude", "longitude", "risk_level"]]
        
        # Select destination based on city (includes safe zone name)
        destination = destination_points.get(city, (lat + 0.1, lon, f"Default {city}"))
        
        # Define bounding box (0.05° ~ 5-6 km radius)
        north, south = lat + 0.05, lat - 0.05
        east, west = lon + 0.05, lon - 0.05
        logger.info(f"Fetching road network for {city}: ({north}, {south}, {east}, {west})")
        
        # Retry logic for OSM queries
        for attempt in range(3):
            try:
                G = ox.graph_from_bbox(north=north, south=south, east=east, west=west, network_type="drive")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(1)
                if attempt == 2:
                    logger.error(f"Failed to fetch road network for {city}: {e}")
                    return None, None
        
        # Assign weights based on multiple disaster types
        risk_dict = {(row["longitude"], row["latitude"]): row["risk_level"] for _, row in gdf.iterrows()}
        for u, v, data in G.edges(data=True):
            edge_midpoint = (
                (G.nodes[u]["x"] + G.nodes[v]["x"]) / 2,
                (G.nodes[u]["y"] + G.nodes[v]["y"]) / 2
            )
            risk_weight = 1.0
            flood_weight = 1.0
            cyclone_weight = 1.0
            quake_weight = 1.0
            for (lon2, lat2), level in risk_dict.items():
                if abs(edge_midpoint[0] - lon2) < 0.05 and abs(edge_midpoint[1] - lat2) < 0.05:
                    if level == "High":
                        risk_weight = 100.0
                        quake_weight = 50.0  # Placeholder for earthquake intensity
                    elif level == "Medium":
                        risk_weight = 10.0
                        quake_weight = 10.0
                    # Fetch weather data for this point
                    city_data = gdf[(gdf["longitude"] == lon2) & (gdf["latitude"] == lat2)]
                    if not city_data.empty:
                        precip = city_data["precipitation_mm"].iloc[0]
                        wind = city_data["wind_speed_kph"].iloc[0]
                        flood_weight += precip / 10  # Adjust for floods
                        cyclone_weight += wind / 20  # Adjust for cyclones
            data["weight"] = data.get("length", 1.0) * max(risk_weight, flood_weight, cyclone_weight, quake_weight)
        
        # Find start and end nodes
        start_node = ox.distance.nearest_nodes(G, lon, lat)
        end_node = ox.distance.nearest_nodes(G, destination[0], destination[1])
        
        # Compute shortest path
        logger.info(f"Computing shortest path for {city}...")
        route = nx.shortest_path(G, start_node, end_node, weight="weight")
        route_coords = [(G.nodes[node]["x"], G.nodes[node]["y"]) for node in route]  # [lon, lat]
        logger.info(f"Route computed for {city}")
        return route, route_coords
    except nx.NetworkXNoPath:
        logger.warning(f"No path found for {city}. Skipping.")
        return None, None
    except Exception as e:
        logger.error(f"Error computing route for {city}: {e}")
        return None, None

# Save route as GeoJSON
def save_route_geojson(city, route_coords, output_file):
    if not route_coords:
        logger.warning(f"No route to save for {city}.")
        return
    line = LineString(route_coords)
    gdf_route = gpd.GeoDataFrame({"city": [city], "geometry": [line]}, crs="EPSG:4326")
    gdf_route.to_file(output_file, driver="GeoJSON")
    logger.info(f"Route saved to {output_file}")

def main():
    # Load risk zones
    geojson_file = "clustered_risk_zones.geojson"
    gdf = load_risk_zones(geojson_file)
    if gdf is None:
        return
    
    # Define destination points for each city with safe zone names
    destination_points = {
        "New York": (-73.5, 41.0, "Safe Zone NY"),  # North of New York
        "Los Angeles": (-118.0, 34.5, "Safe Zone LA"),  # North of Los Angeles
        "Miami": (-80.0, 26.0, "Safe Zone Miami"),  # North of Miami
        "Mumbai": (72.82599999999999, 19.075, "Safe Zone Mumbai"),  # North of Mumbai
        "Pune": (73.8567, 18.6333, "Safe Zone Pune"),  # North of Pune
        "Delhi": (77.1025, 28.8041, "Safe Zone Delhi"),  # North of Delhi
        "Bangalore": (77.5833, 13.0833, "Safe Zone Bangalore"),  # North of Bangalore
        "Hyderabad": (78.4744, 17.4753, "Safe Zone Hyderabad")  # North of Hyderabad
    }
    
    # Compute routes for all cities
    for city in gdf["city"]:
        route, route_coords = compute_evacuation_route(gdf, city, destination_points)
        if route:
            output_file = f"evacuation_route_{city.lower().replace(' ', '_')}.geojson"
            save_route_geojson(city, route_coords, output_file)

if __name__ == "__main__":
    main()