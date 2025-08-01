# AI-Powered Disaster Response and Evacuation Planning

## Overview

This project delivers an **AI-powered system** for real-time disaster response and evacuation planning. It predicts risk zones using live weather, geospatial, and alert data, and recommends optimal evacuation routes and resource allocation using machine learning and optimization algorithms. Visual summaries and an interactive dashboard help emergency managers make informed decisions rapidly.

## Features

- **Predict disaster impact zones:** Uses ML & clustering on weather and geo-features.
- **Integrate real-time feeds:** Ingests weather, public alerts, and social data.
- **Optimize evacuation routes:** Fast Dijkstra-based network optimization.
- **Dynamic resource allocation:** Proportional assignment of ambulances, shelters, teams.
- **Live dashboard:** Visualizes risk, weather, alerts, and evacuation plans on an interactive map.
- **Simulation-ready:** Test evacuation strategies for various scenarios.

## ML Libraries Used

- **scikit-learn**: Employed for KMeans clustering in risk zone prediction (see `cluster_risk_zones.py` for implementation details). This handles unsupervised learning to categorize areas into Low, Medium, and High risk based on normalized weather features like temperature, humidity, wind speed, and precipitation.

## Directory Structure

├── fetch_weather_data.py
├── cluster_risk_zones.py
├── optimize_routes.py
├── dashboard.py
├── preprocessed_weather_data.csv
├── clustered_risk_zones.csv
├── clustered_risk_zones.geojson
├── optimized_evacuation_routes.geojson
├── requirements.txt
├── README.md


## Setup & Installation


1. **Environment setup**  
Install Python 3.9+ and pip. (Recommended: Create a virtual environment.)


2. **Install dependencies**  



## How To Run The Project

**Step 1: Fetch Weather & Alert Data**  
Fetches and preprocesses weather and alert data for target cities.
python fetch_weather_data.py



**Step 2: Cluster Risk Zones & Allocate Resources**  
Clusters cities/zones into risk categories, allocates dynamic resources.
python cluster_risk_zones.py



**Step 3: Optimize Evacuation Routes**  
Creates and saves evacuation routes from risk areas to safe zones.
python optimize_routes.py



**Step 4: Launch the Dashboard**  
Starts the Streamlit dashboard for real-time visualization.

(fetch_weather_data.py>>cluster_risk_zones.py>>optimize_routes.py>>dashboard.py)

(NOTE: File already has csv files,you can directly run using streamlit run dashboard.py )

## Usage

- On the dashboard:
  - **Select cities** of interest and the disaster focus type.
  - **View map:** Risk zones (colored markers), real-time weather/alert data, and recommended blue evacuation routes leading to green safe-zone markers.
  - **Weather, Risk, Alerts:** Detailed table below the map.
- **Automatic Data Refresh:** Weather data auto-updates every 30 minutes if dashboard remains running.

## Files Provided

- **Working code** for all ingestion, modeling, optimization, and visualization steps.
- **Simple UI:** Accessible, no coding needed after setup.
- **Sample outputs:** Input/output CSVs and GeoJSONs.
- **Requirements:** See `requirements.txt` for all packages and dependencies.



## Advanced Notes

- To test different disaster scenarios, edit the resource counts or city list in scripts before running.
- For custom deployments (e.g., cloud/server), ensure correct file paths and environment access.






