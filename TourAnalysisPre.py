import pandas as pd
from datetime import date
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns

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

# #**see about dictionary prior and insert**
# Tour_Attendances = {}
# Tour_Attendances['Tour_ID'] = 1
# Tour_Attendances['Total_Attendance'] = FearlessTour['Attendance'].sum(skipna = True)
# Tour_Attendances['Total_Shows'] = FearlessTour['Date'].sum()
# Tour_Attendances['Per_Show_Attend'] = Tour_Attendances['Total_Attendance']/Tour_Attendances['Total_Shows']


tour_summary = []

for tour, df in Tours.items():
    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if tour == 'ErasTour':
        total_row = df[df.apply(lambda row: 
                                row.astype(str).str.contains('Total', case=False).any(), 
                                axis=1)]
        if not total_row.empty:
            total_attendance = float(total_row['Attendance'].iloc[0])
            total_shows = df['Date'].nunique()
            total_cities = df['City'].nunique()

        else:
            concert_rows = df[df['Attendance'].notna()]
            total_attendance = concert_rows['Attendance'].sum()
            total_shows = df['Date'].nunique()
            total_cities = df['City'].nunique()
    else:
        # use calc for other tours
        concert_rows = df[df['Attendance'].notna()]

        total_attendance = concert_rows['Attendance'].sum()
        total_shows = df['Date'].nunique()
        total_cities = df['City'].nunique()

    # Average attendance per show
    avg_attendance_show = total_attendance / total_shows if total_shows else 0
   
    tour_summary.append({
        'Tour': tour
        , 'Total_Attendance': total_attendance
        , 'Total_Shows': total_shows
        , 'Total_Cities': total_cities
        , 'Avg_Attendance_Per_Show': avg_attendance_show
    })


tour_summary_df = pd.DataFrame(tour_summary)
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Avg_Attendance_Per_Show'].pct_change() * 100
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Attendance_Growth_Previous_Tour'].round(2)
tour_summary_df['Tour'] = tour_summary_df['Tour'].replace({'Tour1989': '1989Tour'})
print(tour_summary_df)
print()

# Sort by tour chronological order
tour_order = ['FearlessTour', 'SpeakNowTour', 'RedTour', '1989Tour', 'ReputationTour', 'ErasTour']
tour_summary_df['Tour'] = pd.Categorical(tour_summary_df['Tour'], categories=tour_order, ordered=True)
tour_summary_df = tour_summary_df.sort_values('Tour')

# # Plot total attendance growth
eras_colors = ['#D8B372', '#A088A2', '#7A2E39', "#8AC9E4", "#746F70", "#242E47"]
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Total_Attendance', data=tour_summary_df, palette=eras_colors, hue = 'Tour')
plt.title('Total Attendance per Tour', fontsize=16)
plt.ylabel('Total Attendance')
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"Total_Attendance_per_Tour", dpi=300, bbox_inches='tight')
plt.show()

# Plot average attendance per show growth
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Avg_Attendance_Per_Show', data=tour_summary_df, palette=eras_colors)
plt.title('Average Attendance per Show per Tour', fontsize=16)
plt.ylabel('Average Attendance per Show')
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"Avg_Attendance_per_Show_per_Tour", dpi=300, bbox_inches='tight')
plt.show()


Album_Tours = pd.read_csv('ToursPerAlbum.csv')
Album_Tours['Tour_StartDate'] = pd.to_datetime(Album_Tours['Tour_StartDate'])
Album_Tours['Tour_EndDate'] = pd.to_datetime(Album_Tours['Tour_EndDate'])


FirstTourDate = Album_Tours['Tour_StartDate'].min()
LastTourDate = Album_Tours['Tour_EndDate'].max()
CurrentDate = date.today()
Format_Today = CurrentDate.strftime('%Y-%m-%d')
Days_Btwn_FirstTour_LastTour = LastTourDate - FirstTourDate

print(f'Days between the first tour date and last tour date are {Days_Btwn_FirstTour_LastTour}', end = '\n\n')
AllTours_Days = Days_Btwn_FirstTour_LastTour / 6 #number of tours
print(f'There is a tour every {AllTours_Days} days', end = '\n\n')


#avg tour length
Album_Tours['Tour_Length'] = Album_Tours['Tour_EndDate'] - Album_Tours['Tour_StartDate']
print(Album_Tours)
print()

Avg_Tour_Length = Album_Tours['Tour_Length'].mean()
print(f'Average tour length is {Avg_Tour_Length}', end='\n\n')

Avg_TourStart_AlbumRel_Diff = Album_Tours['DateDiff_AlbumRel_TourStart'].mean()
print(f'Average time between album release and tour start date is {Avg_TourStart_AlbumRel_Diff}', end = '\n\n')

# #city visit counts
# ##evaluate how many cities she has visited
# ##evaluate how many countries she has visited
# ##evaluate how many times she has played in certain cities
# ###most visited cities (descending order)
# ##evaluate how many times she has played in certain countries
# ##most visited venues (descending order)

StadiumList = pd.read_csv('StadiumList.csv')

Cities_Toured = StadiumList['City'].nunique()
print(f'Number of distinct cities visited is: {Cities_Toured}', end='\n\n')


Countries_Toured = StadiumList['Country'].nunique()
print(f'Number of distinct countries visited is: {Countries_Toured}', end='\n\n')


##bring in revenue added to album_tours but only report Eras once
Album_Tours_copy = Album_Tours.copy()
unique_revenue = Album_Tours.drop_duplicates(subset = ['Tour_ID']).copy()

Tour_ID_Name = {
    1: 'FearlessTour',
    2: 'SpeakNowTour',
    3: 'RedTour',
    4: 'Tour1989',
    5: 'ReputationTour',
    6: 'ErasTour',
    7: 'ErasTour'
}

Album_Tours_copy['Tour'] = Album_Tours_copy['Tour_ID'].map(Tour_ID_Name)
unique_revenue['Tour'] = unique_revenue['Tour_ID'].map(Tour_ID_Name)

revenue_per_tour = unique_revenue.groupby('Tour')['Revenue'].sum().reset_index()
tour_summary_df = tour_summary_df.merge(revenue_per_tour, how = 'left', on = 'Tour')
tour_summary_df['Avg_Revenue_Per_Show'] = tour_summary_df['Revenue'] / tour_summary_df['Total_Shows']
tour_summary_df['Revenue_Growth_Previous_Tour'] = tour_summary_df['Avg_Revenue_Per_Show'].pct_change() * 100

tour_summary_df['Revenue'] = tour_summary_df['Revenue'].apply(lambda x: f"${x:,.0f}")
tour_summary_df['Avg_Revenue_Per_Show'] = tour_summary_df['Avg_Revenue_Per_Show'].apply(lambda x: f"${x:,.0f}")
tour_summary_df['Revenue_Growth_Previous_Tour'] = tour_summary_df['Revenue_Growth_Previous_Tour'].round(2)
print(tour_summary_df, '\n\n')

AvgShowNum = tour_summary_df['Total_Shows'].mean()
print(f'Number of shows, on average, is {AvgShowNum} shows per tour.', end = '\n\n')

AvgCityNum = tour_summary_df['Total_Cities'].mean().round()
print(f'Number of cities, on average, is {AvgCityNum} cities per tour.', end = '\n\n')

for tour, df in Tours.items():
    df['Tour'] = tour

All_Tours = pd.concat(Tours.values(), ignore_index = True)
All_Tours = pd.DataFrame(All_Tours)

AT_Cities = All_Tours['City'].value_counts()
AT_Cities = pd.DataFrame(AT_Cities)
Top_10_Cities = AT_Cities.head(10)
# print(f'Top 10 visited cities are {Top_10_Cities}', end='\n\n')

City_Headers = ['City', 'Number of Visits']
print(tabulate(Top_10_Cities, headers = City_Headers, tablefmt = 'fancy_grid', showindex = 'always'), end='\n\n')


AT_Country = All_Tours['Country'].value_counts()
AT_Country = pd.DataFrame(AT_Country)

Top_10_Countries = AT_Country.head(10)
Country_Headers = ['Country', 'Number of Visits']
print(tabulate(Top_10_Countries, headers = Country_Headers, tablefmt = 'fancy_grid', showindex = 'always'), end='\n\n')
# print(f'Top 10 countries are: {Top_10_Countries}', end='\n\n')

print(AT_Country)

AT_Venues = All_Tours['Venue'].value_counts()
AT_Venues = pd.DataFrame(AT_Venues)

Top_10_Venues = AT_Venues.head(10)
Venue_Headers = ['Venue', 'Number of Visits']
print(tabulate(Top_10_Venues, headers = Venue_Headers, tablefmt = 'fancy_grid', showindex = 'always'), end = '\n\n')
# print(f'Top 10 visited venues are {Top_10_Venues}', end='\n\n')


