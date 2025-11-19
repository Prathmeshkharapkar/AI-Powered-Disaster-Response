# import pandas as pd
# import geopandas as gpd
# import networkx as nx
# from shapely.geometry import LineString
# import os

# def load_clustered_data(file_path):
#     if not os.path.exists(file_path):
#         print(f"Error: {file_path} not found")
#         return None
#     return pd.read_csv(file_path)

# def optimize_evacuation_routes(df, safe_zones):
#     G = nx.Graph()  # Create a graph
    
#     # Add nodes for cities and safe zones
#     for _, row in df.iterrows():
#         city = row['city']
#         G.add_node(city, pos=(row['longitude'], row['latitude']), risk=row['risk_level'])
#     for city, (lon, lat, _) in safe_zones.items():
#         G.add_node(f"Safe_{city}", pos=(lon, lat), risk="Low")
    
#     # Add edges with weights (e.g., distance + risk factor)
#     cities = df['city'].tolist()
#     for i in range(len(cities)):
#         for j in range(i + 1, len(cities)):
#             city1, city2 = cities[i], cities[j]
#             pos1 = G.nodes[city1]['pos']
#             pos2 = G.nodes[city2]['pos']
#             distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
#             risk_weight = 1 if G.nodes[city1]['risk'] == "High" or G.nodes[city2]['risk'] == "High" else 0.5
#             G.add_edge(city1, city2, weight=distance * risk_weight)
        
#         # Connect each city to its safe zone
#         safe_node = f"Safe_{city1}"
#         pos1 = G.nodes[city1]['pos']
#         pos_safe = G.nodes[safe_node]['pos']
#         distance = ((pos1[0] - pos_safe[0])**2 + (pos1[1] - pos_safe[1])**2)**0.5
#         G.add_edge(city1, safe_node, weight=distance)
    
#     # Optimize paths using Dijkstra's algorithm
#     routes = {}
#     for city in cities:
#         safe_node = f"Safe_{city}"
#         try:
#             path = nx.dijkstra_path(G, city, safe_node)
#             # Swap to (lat, lon) for consistency with Folium
#             coords = [(lat, lon) for lon, lat in [G.nodes[node]['pos'] for node in path]]
#             routes[city] = LineString(coords)
#         except nx.NetworkXNoPath:
#             print(f"No path found for {city}")
    
#     # Create GeoDataFrame
#     route_data = {'city': list(routes.keys()), 'geometry': list(routes.values())}
#     gdf = gpd.GeoDataFrame(route_data, crs="EPSG:4326")
#     return gdf

# def main():
#     input_file = "clustered_risk_zones.csv"
#     output_geojson = "optimized_evacuation_routes.geojson"
    
#     df = load_clustered_data(input_file)
#     if df is None:
#         return
    
#     # Updated safe zones to match dashboard.py for precise alignment
#     safe_zones = {
#         "New York": (-73.8, 40.8, "Safe Zone NY"),
#         "Los Angeles": (-118.1, 34.1, "Safe Zone LA"),
#         "Miami": (-80.3, 25.8, "Safe Zone Miami"),
#         "Mumbai": (72.9, 19.1, "Safe Zone Mumbai"),
#         "Pune": (73.8, 18.6, "Safe Zone Pune"),
#         "Bangalore": (77.6, 13.0, "Safe Zone Bangalore"),
#         "Hyderabad": (78.5, 17.4, "Safe Zone Hyderabad")
#     }
    
#     route_gdf = optimize_evacuation_routes(df, safe_zones)
#     route_gdf.to_file(output_geojson, driver="GeoJSON")
#     print(f"Optimized routes saved to {output_geojson}")

# if __name__ == "__main__":
#     main()

#for dynamic



import pandas as pd
import geopandas as gpd
import numpy as np
import networkx as nx
from shapely.geometry import LineString


def load_clustered_data(file_path):
    df = pd.read_csv(file_path)
    print(f"✅ Loaded {len(df)} cities: {df['city'].tolist()}")
    return df


def load_safe_zones(file_path):
    try:
        safe_zones_gdf = gpd.read_file(file_path)
        print(f"✅ Loaded {len(safe_zones_gdf)} safe zones")
        return safe_zones_gdf
    except Exception as e:
        print(f"❌ Could not load safe zones: {e}")
        return None


def build_dynamic_graph(df, safe_zones):
    G = nx.Graph()
    
    # Add city nodes
    for _, row in df.iterrows():
        G.add_node(row['city'], 
                   pos=(row['longitude'], row['latitude']), 
                   risk=row['risk_score'],
                   type='city')
    
    # Add safe zone nodes
    for _, row in safe_zones.iterrows():
        G.add_node(row['safe_zone_id'], 
                   pos=(row['longitude'], row['latitude']), 
                   risk=row['risk_score'],
                   type='safe_zone',
                   parent_city=row.get('city', 'Unknown'))
    
    cities = df['city'].tolist()
    
    # Connect each city to its safe zone
    for city in cities:
        city_safe_zone = f"SafeZone_{city}"
        if city_safe_zone in G.nodes():
            pos_city = G.nodes[city]['pos']
            pos_safe = G.nodes[city_safe_zone]['pos']
            dist = np.linalg.norm(np.array(pos_city) - np.array(pos_safe))
            risk_weight = G.nodes[city]['risk'] + 1
            G.add_edge(city, city_safe_zone, weight=dist * risk_weight)
            print(f"✅ Connected {city} → {city_safe_zone}")
        else:
            print(f"❌ Safe zone {city_safe_zone} not found!")
    
    print(f"\n📊 Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")
    return G


def find_evacuation_routes(G, cities):
    routes = {}
    for city in cities:
        city_safe_zone = f"SafeZone_{city}"
        try:
            if city_safe_zone in G.nodes():
                path = nx.shortest_path(G, city, city_safe_zone, weight='weight')
                
                # Get coordinates (lon, lat) for GeoJSON
                coords_lonlat = [G.nodes[node]['pos'] for node in path]
                line = LineString(coords_lonlat)
                routes[city] = line
                
                print(f"✅ Route for {city}: {coords_lonlat}")
            else:
                print(f"❌ No safe zone for {city}")
        except Exception as e:
            print(f"❌ Error for {city}: {e}")
    
    return routes


def save_routes_to_geojson(routes, output_file):
    if not routes:
        print("❌ No routes to save!")
        return
    
    gdf = gpd.GeoDataFrame({
        'city': list(routes.keys()),
        'geometry': list(routes.values())
    }, crs='EPSG:4326')
    
    gdf.to_file(output_file, driver='GeoJSON')
    print(f"\n✅ Saved {len(gdf)} routes to {output_file}")
    print(f"Routes saved for cities: {gdf['city'].tolist()}\n")


def main():
    print("="*60)
    print("GENERATING EVACUATION ROUTES")
    print("="*60 + "\n")
    
    df = load_clustered_data('clustered_risk_zones.csv')
    safe_zones = load_safe_zones('safe_zones.geojson')
    
    if safe_zones is None or safe_zones.empty:
        print("❌ No safe zones! Run cluster_risk_zones.py first.")
        return
    
    G = build_dynamic_graph(df, safe_zones)
    routes = find_evacuation_routes(G, df['city'].tolist())
    save_routes_to_geojson(routes, 'dynamic_evacuation_routes.geojson')
    
    print("="*60)
    print("✅ DONE! Run dashboard.py to visualize routes")
    print("="*60)


if __name__ == '__main__':
    main()
