import pandas as pd
from datetime import date
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt

#attendance growth
##sum all concert attendance per tour/individual concerts 

Tours = {
    'FearlessTour': pd.read_csv('FearlessTour.csv')
    , 'SpeakNowTour': pd.read_csv('SpeakNowTour.csv')
    , 'RedTour': pd.read_csv('RedTour.csv')
    , 'Tour1989': pd.read_csv('1989Tour.csv')
    , 'ReputationTour': pd.read_csv('ReputationTour.csv')
    , 'ErasTour': pd.read_csv('ErasTour_Post.csv')
}


tour_summary = []

for tour, df in Tours.items():
    concert_attendance = df[df['Attendance'].notna()]
    total_attendance = concert_attendance['Attendance'].sum()
    total_shows = concert_attendance['Date'].count()
    avg_attendance_show = total_attendance / total_shows

    tour_summary.append({
        'Tour': tour
        , 'Total_Attendance': total_attendance
        , 'Total_Shows': total_shows
        , 'Average_Attendance_Per_Show': avg_attendance_show
    })


All_Tours = pd.concat(Tours.values(), ignore_index = True)
All_Tours = pd.DataFrame(All_Tours)


def prep_top10_tab(series, col_name):
    df = series.head(10).reset_index()
    df.columns = [col_name, 'Number of Visits']
    return df

Top_10_Cities = prep_top10_tab(All_Tours['City'].value_counts(), 'City')
Top_10_Countries = prep_top10_tab(All_Tours['Country'].value_counts(), 'Country')
Top_10_Venues = prep_top10_tab(All_Tours['Venue'].value_counts(), 'Venue')

def save_table(df, filename, title = None, fig_size = (8, 3), col_widths = None, title_pad = None):
    fig, ax = plt.subplots(figsize = fig_size)
    ax.axis('tight')
    ax.axis('off')

    n_rows, n_cols = df.shape
    if col_widths is None:
        col_widths = [1] * n_cols

    table = ax.table(
        cellText = df.values
        , colLabels = df.columns
        , colWidths = col_widths
        , cellLoc = 'center'
        , loc = 'center'
    )


    for i in range(n_rows):
        for j in range(n_cols):
            color = "#bbd8eb" if i % 2 == 0 else "#ffffff"
            table[(i + 1, j)].set_facecolor(color)

    for j in range(n_cols):
        table[(0, j)].set_facecolor('#000000')
        table[(0, j)].set_text_props(weight = 'bold', color = '#ffffff')

    if title:
        plt.title(title, fontsize = 14, pad = title_pad)

    plt.tight_layout(pad = 1.0)

    plt.savefig(filename, bbox_inches = 'tight', dpi = 300)
    plt.close()




save_table(Top_10_Cities, "Top10Cities.png", title = 'Top 10 Visited Cities', fig_size = (8, 3))
save_table(Top_10_Countries, "Top10Countries.png", title = "Top 10 Visited Countries", fig_size = (8, 3))
save_table(Top_10_Venues, "Top10Venues.png", title = "Top 10 Visited Venues", fig_size = (8, 3))

print('Images created')
