import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from adjustText import adjust_text

# Load predicted tour
tour_df = pd.read_csv('Predicted_Showgirl_Tour.csv')

# Fix continent naming if needed
tour_df['Continent'] = tour_df['Continent'].str.title()

# Combine Oceania + Asia
tour_df['Continent_Combined'] = tour_df['Continent'].replace({'Oceania': 'Oceania & Asia', 'Asia': 'Oceania & Asia'})

# Define continents to plot
continents = ['North America', 'South America', 'Europe', 'Oceania & Asia']

# Set map extents for better zoom
continent_extents = {
    'North America': [-170, -50, 5, 75],
    'South America': [-90, -30, -60, 15],
    'Europe': [-25, 45, 35, 72],
    'Oceania & Asia': [90, 180, -50, 60]  # Asia + Oceania
}

# Loop through continents
for name in continents:
    cont_df = tour_df[tour_df['Continent_Combined'] == name]
    if cont_df.empty:
        continue

    fig = plt.figure(figsize=(14,10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Base map
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.COASTLINE)

    # Plot cities
    ax.scatter(cont_df['Longitude'], cont_df['Latitude'], color='blue', s=10, zorder=5, transform=ccrs.PlateCarree())

    # Add city labels
    texts = []
    for _, row in cont_df.iterrows():
        texts.append(ax.text(row['Longitude'] + 0.5, row['Latitude']  + 0.5, row['City'],
                             fontsize=8, ha = 'center', va = 'center'))

    # Adjust labels to avoid overlaps
    adjust_text(texts, 
                ax=ax,
                expand_points=(2.0, 2.0),
                expand_text=(1.5, 1.5),
                arrowprops = None)

    # Set map extent
    ax.set_extent(continent_extents[name], crs=ccrs.PlateCarree())

    # plt.title(f"{name} Tour Locations", fontsize=18)
    # plt.show()

    plt.savefig(f"{name.replace(' ', '')}_ShowgirlTour.png", dpi=300, bbox_inches='tight')
    plt.close()

