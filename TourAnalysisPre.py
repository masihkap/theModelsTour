import pandas as pd
from datetime import date
import numpy as np

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


tour_summary_df = pd.DataFrame(tour_summary)
tour_summary_df['Growth_Previous_Tour'] = tour_summary_df['Average_Attendance_Per_Show'].pct_change() * 100
print(tour_summary_df)
print()




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



for tour, df in Tours.items():
    df['Tour'] = tour

All_Tours = pd.concat(Tours.values(), ignore_index = True)


AT_Cities = All_Tours['City'].value_counts()
Top_10_Cities = AT_Cities.head(10)
print(f'Top 10 visited cities are {Top_10_Cities}', end='\n\n')

AT_Country = All_Tours['Country'].value_counts()
Top_10_Countries = AT_Country.head(10)
print(f'Top 10 countries are: {Top_10_Countries}', end='\n\n')

AT_Venues = All_Tours['Venue'].value_counts()
Top_10_Venues = AT_Venues.head(10)
print(f'Top 10 visited venues are {Top_10_Venues}', end='\n\n')

