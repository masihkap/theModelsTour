import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point
import numpy as np


tour_df = pd.read_csv('Predicted_Showgirl_Tour.csv')

#combine Oceania and Asia
tour_df['Continent'] = tour_df['Continent'].str.title()
tour_df['Continent_Combined'] = tour_df['Continent'].replace({'Oceania': 'Oceania & Asia',
                                                              'Asia': 'Oceania & Asia'})
continents = ['North America', 'South America', 'Europe', 'Oceania & Asia']


continent_extents = {
    'North America': [-170, -50, 5, 75],
    'South America': [-90, -30, -60, 15],
    'Europe': [-25, 45, 35, 72],
    'Oceania & Asia': [90, 180, -50, 60]
}


#label overlap filter
def filter_labels(lons, lats, labels, min_distance = 2.0):
    keep = []
    positions = []

    for lon, lat, label in zip(lons, lats, labels):
        too_close = False
        for px, py in positions:
            dx = (lon - px) * np.cos(np.radians(lat))
            dy = lat - py
            distance = np.sqrt(dx**2 + dy**2)
            if distance < min_distance:
                too_close = True
                break
        if not too_close:
            keep.append((lon, lat, label))
            positions.append((lon, lat))
    return keep

#continent loop
for cont in continents:
    cont_df = tour_df[tour_df['Continent_Combined'] == cont]
    if cont_df.empty:
        continue

    fig = plt.figure(figsize=(14,10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    #base map features
    ax.add_feature(cfeature.LAND, facecolor = 'beige')
    ax.add_feature(cfeature.OCEAN, facecolor = 'lightblue')
    ax.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='gray', linewidth = 0.5)
    ax.add_feature(cfeature.COASTLINE, edgecolor = 'gray', linewidth = 0.5)
    if cont == 'North America':
        ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

    #cities
    for lon, lat in zip(cont_df['Longitude'], cont_df['Latitude']):
               ax.text(lon, lat, '❤', fontsize = 10, color = "#693FA7"       
               , ha = 'center', va = 'center', zorder = 5, transform=ccrs.PlateCarree())

    #labels
    labels_to_plot = filter_labels(
        cont_df['Longitude'], cont_df['Latitude'], cont_df['City'], min_distance = 3.5
    )

    for lon, lat, label in labels_to_plot:
        ax.text(lon + 0.4, lat + 0.4, label, fontsize = 8, ha = 'center', va = 'bottom', color = 'black', zorder = 6,
                path_effects=[path_effects.withStroke(linewidth = 1, foreground = "white")])

    #map
    ax.set_extent(continent_extents[cont], crs=ccrs.PlateCarree())
    ax.set_axis_off()

    #save
    plt.title(f"{cont} Tour Locations", fontsize=16)
    plt.savefig(f"{cont.replace(' ', '')}_ShowgirlTour.png", dpi=300, bbox_inches='tight')
    plt.close()

print(f'Maps created')