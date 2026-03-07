import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
import time
from retry_requests import retry

class MarineEnvironment:
    def __init__(self, lat_range, lon_range, resolution=10):

        self.lats = np.linspace(lat_range[0], lat_range[1], resolution)
        self.lons = np.linspace(lon_range[0], lon_range[1], resolution)
        
        # Setup API avec cache et retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    def fetch_weather_grid(self):
        grid_results = []
        
        url_m = "https://marine-api.open-meteo.com/v1/marine"
        url_w = "https://api.open-meteo.com/v1/forecast"
        
        
        for lat in self.lats:
            for lon in self.lons:
                params_m = {
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": ["wave_height"],
                    "forecast_days": 1
                }
                params_w = {
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": ["wind_speed_10m", "wind_direction_10m"],
                    "wind_speed_unit": "kn",
                    "forecast_days": 1
                }
                try:
                    res_w = self.client.weather_api(url_w, params=params_w)[0]
                    res_m = self.client.weather_api(url_m, params=params_m)[0]
                    
                    # Extraction des données actuelles
                    wind_speed = res_w.Hourly().Variables(0).ValuesAsNumpy()[0]
                    wind_dir = res_w.Hourly().Variables(1).ValuesAsNumpy()[0]
                    wave_h = res_m.Hourly().Variables(0).ValuesAsNumpy()[0]

                    grid_results.append({
                        "latitude": lat,
                        "longitude": lon,
                        "wind_speed": wind_speed,
                        "wind_dir": wind_dir,
                        "wave_height": wave_h
                    })
                except Exception as e:
                    print(f"ERREUR sur {lat}, {lon}: {e}")  # Changez pour voir les erreurs

        return pd.DataFrame(grid_results)

    def get_neighbors(self, current_node_idx, df_grid):
        """
        Utile pour le mapping QUBO : définit quels points sont 
        accessibles depuis le point actuel (N, S, E, W, Diagonales)
        """
        # Logique à implémenter pour créer les arêtes de ton graphe
        pass