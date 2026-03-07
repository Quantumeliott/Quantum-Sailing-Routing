import folium
import numpy as np
from data_marine import MarineEnvironment

env = MarineEnvironment(lat_range=(46.7, 47.7), lon_range=(-3.8, -2.2), resolution=30)
df = env.fetch_weather_grid()

def plot_wind_grid(df):
    # On centre la carte sur la moyenne des points
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()],zoom_start=8, tiles='CartoDB positron')
    for _, row in df.iterrows():
        if np.isnan(row.wind_speed):
            continue
            
        # Coordonnées du point
        origin = [row.latitude, row.longitude]
        
        # Calcul du vecteur vent pour l'affichage (bout de la flèche)
        # On divise par 50 pour que la flèche ne soit pas trop grande sur la carte
        scale = 0.0005 
        angle_rad = np.radians(row.wind_dir)
        
        # En météo, la direction est d'où vient le vent, on l'inverse pour la flèche
        end_lat = row.latitude - (row.wind_speed * scale * np.cos(angle_rad))
        end_lon = row.longitude - (row.wind_speed * scale * np.sin(angle_rad))
        
        # Dessiner le point de la grille
        folium.CircleMarker(origin, radius=2, color='blue', fill=True).add_to(m)
        
        # Dessiner la flèche du vent (PolyLine)
        color = 'green' if row.wind_speed < 15 else 'orange' if row.wind_speed < 25 else 'red'
        folium.PolyLine([origin, [end_lat, end_lon]], color=color, weight=2, opacity=0.8).add_to(m)

    return m

# Utilisation :
my_map = plot_wind_grid(df)
my_map.save("wind_map.html")