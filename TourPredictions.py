import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
#import glob

#merge files
tour_files = ['FearlessTour_VenueID.csv', 'SpeakNowTour_VenueID.csv', 'RedTour_VenueID.csv'
              , '1989Tour_VenueID.csv', 'ReputationTour_VenueID.csv', 'ErasTour_VenueID.csv']

tour_df = [pd.read_csv(f, parse_dates = ['Date']) for f in tour_files]
all_tours = pd.concat(tour_df, ignore_index = True)

#print(all_tours.head())

tours_album = pd.read_csv('ToursPerAlbum.csv', parse_dates = ['Album_ReleaseDate', 'Tour_StartDate', 'Tour_EndDate'])
merged_tours = all_tours.merge(tours_album, on = 'Tour_ID', how = 'left')

print(merged_tours.head())

#prep
merged_tours['DaysSinceAlbumRelease'] = (merged_tours['Date'] - merged_tours['Album_ReleaseDate']).dt.days
merged_tours['DaysSinceTourStart'] = (merged_tours['Date'] - merged_tours['Tour_StartDate']).dt.days #??

region_map = {
    "United States": "North America", "Canada": "North America",
    "Japan": "Asia", "Singapore": "Asia", "Australia": "Oceania",
    "United Kingdom": "Europe", "Germany": "Europe", "France": "Europe"
}
merged_tours["Region"] = merged_tours["Country"].map(region_map).fillna("Other")

for col in ['Revenue', 'Venue_Capacity', 'Attendance']:
    if col not in merged_tours.columns:
        merged_tours[col] = np.nan

tour_summary = merged_tours.groupby("Tour_ID").agg({
    "Album_Name": "first",
    "Album_ReleaseDate": "first",
    "Tour_StartDate": "first",
    "Tour_EndDate": "first",
    "City": pd.Series.nunique,
    "Country": pd.Series.nunique,
    "Venue": pd.Series.nunique,
    "Attendance": "mean",
    "Revenue": "mean",
    "Venue_Capacity": "mean"
}).reset_index()

tour_summary.rename(columns={"City": "NumCities", "Country": "NumCountries"}, inplace = True)

for col in ['Revenue', 'Venue_Capacity', 'Attendance']:
    if col not in tour_summary.columns:
        tour_summary[col] = np.nan

#Predicting Showgirl Tour Start
tour_gap = tour_summary.dropna(subset = ['Album_ReleaseDate', 'Tour_StartDate']) #shouldn't have nulls but safety
tour_gap['GapDays'] = (tour_gap['Tour_StartDate'] - tour_gap['Album_ReleaseDate']).dt.days
X = np.arange(len(tour_gap)).reshape(-1, 1)
y = tour_gap['GapDays']

LR_TourGap = LinearRegression().fit(X, y)

next_tour = np.array([[len(tour_gap)]])
predicted_gap = LR_TourGap.predict(next_tour)[0]
print(f'Predicting {predicted_gap:.0f} days between the album release and the next tour start date.')

Showgirl_ReleaseDate = pd.to_datetime(tours_album.loc[tours_album['Album_Name'] == 'The Life of a Showgirl', 'Album_ReleaseDate'].iloc[0])
Showgirl_Tour_StartDate = Showgirl_ReleaseDate + pd.Timedelta(days = predicted_gap)
Showgirl_Tour_StartDate_f = Showgirl_Tour_StartDate.strftime('%B %d, %Y')
print(f'Based on our prediction of {predicted_gap:.0f} days between album release and the next tour'
      f', we expected The Life of a Showgirl tour will start on {Showgirl_Tour_StartDate_f}')



#predicting starting location
City_Start = merged_tours.sort_values('Date').groupby('Tour_ID').first().reset_index()
City_Start['GapDays'] = (City_Start['Tour_StartDate'] - City_Start['Album_ReleaseDate']).dt.days
City_Start['StartMonth'] = City_Start['Tour_StartDate'].dt.month

City_Start = City_Start.merge(tour_summary[['Tour_ID', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']]
                              , on = 'Tour_ID'
                              , how = 'left')
for col in ['NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']:
    if col not in City_Start.columns:
        City_Start[col] = 0
City_Start.fillna(0, inplace = True)

city_encoder = LabelEncoder()
y_city = city_encoder.fit_transform(City_Start['City'].astype(str))
X_city = City_Start[['GapDays', 'StartMonth', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']].fillna(0)
city_clf = RandomForestClassifier(random_state = 42).fit(X_city, y_city)

next_date = np.array([[predicted_gap, Showgirl_Tour_StartDate.month, 0, 0, 0, 0]])
predicted_city = city_encoder.inverse_transform(city_clf.predict(next_date))[0]

predicted_region = merged_tours.loc[merged_tours['City'] == predicted_city, 'Region'].mode()[0]

#adding freq since previous model predicted Tokyo as the start which doesn't feel correct
city_freq = merged_tours['City'].value_counts(normalize = True)
city_prob = city_clf.predict_proba(next_date)[0]
prob_df = pd.DataFrame({'City': city_encoder.classes_, 'ModelProb': city_prob})
prob_df['Frequency'] = prob_df['City'].map(city_freq).fillna(0)

prob_df['CombinedScore'] = 0.5 * prob_df['ModelProb'] + 0.5 * prob_df['Frequency']
prob_df = prob_df.sort_values('CombinedScore', ascending = False).reset_index(drop = True)

print(f'The next tour will most likely start in {predicted_city}, {predicted_region}.')

#rank
prob_df['Rank'] = prob_df.index + 1
print(prob_df.head(10))



