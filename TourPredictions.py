import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import random

#merge files
tour_files = ['FearlessTour_PostCleanse.csv', 'SpeakNowTour_PostCleanse.csv', 'RedTour_PostCleanse.csv'
              , '1989Tour_PostCleanse.csv', 'ReputationTour_PostCleanse.csv', 'ErasTour_PostCleanse.csv']

tour_df = [pd.read_csv(f, parse_dates = ['Date']) for f in tour_files]
all_tours = pd.concat(tour_df, ignore_index = True)
#print(all_tours.head())
all_tour_count1 = all_tours.count()

stadiums = pd.read_csv('StadiumList.csv')
stadiums_open = stadiums[stadiums['Operational'].str.lower() == 'open']
# all_tours_before = pd.concat(tour_df, ignore_index=True)
# all_tour_count1 = all_tours_before.count()

for df in [all_tours, stadiums_open]:
    for col in ['Venue_ID', 'Venue', 'City', 'Country']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

# Merge using only Venue_ID
all_tours = all_tours.merge(
    stadiums_open[['Venue_ID', 'Venue', 'City', 'Country', 'Venue_Capacity']],
    on='Venue_ID',
    how='inner',
    suffixes=('', '_stadium')
)

# Replace original columns with stadium info if available
for col in ['City', 'Venue', 'Country', 'Venue_Capacity']:
    if f"{col}_stadium" in all_tours.columns:
        all_tours[col] = all_tours[f"{col}_stadium"]
        all_tours.drop(columns=[f"{col}_stadium"], inplace=True)

# Sanity check
print(f"Rows after merge with open stadiums: {len(all_tours)}")

# ## checks
# print(f"\nRows before merge: {len(pd.concat(tour_df, ignore_index=True))}")
# print(f"Rows after merge:  {len(all_tours)}")
# print(f"Dropped rows:      {len(pd.concat(tour_df, ignore_index=True)) - len(all_tours)}")
# # Find rows from before that didn’t make it into the merged result
# dropped = all_tours_before[~all_tours_before['Venue_ID'].isin(all_tours['Venue_ID'])]

# if dropped.empty:
#     print("✅ No dropped venues — all matched open stadiums.")
# else:
#     print("🚫 Dropped venues (closed or missing):")
#     print(dropped[['Venue_ID', 'Venue', 'City', 'Country']].drop_duplicates().to_string(index=False))

# # Optional: also print open-stadium count for sanity check
# print("\n🏟️ Total open stadiums listed:", len(stadiums_open))


tours_album = pd.read_csv('ToursPerAlbum.csv', parse_dates = ['Album_ReleaseDate', 'Tour_StartDate', 'Tour_EndDate'])
merged_tours = all_tours.merge(tours_album, on = 'Tour_ID', how = 'left')

#print(merged_tours.head())


#prep
merged_tours['DaysSinceAlbumRelease'] = (merged_tours['Date'] - merged_tours['Album_ReleaseDate']).dt.days
merged_tours['DaysSinceTourStart'] = (merged_tours['Date'] - merged_tours['Tour_StartDate']).dt.days

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
    "Revenue": pd.Series.nunique,
    "Venue_Capacity": "mean"
}).reset_index()

tour_summary.rename(columns={"City": "NumCities", "Country": "NumCountries"}, inplace = True)
tour_summary = tour_summary.merge(
    tours_album[['Tour_ID', 'Revenue']]
    , on = 'Tour_ID'
    , how = 'left'
)

#Predicting Showgirl Tour Start; weighing the non-covid albums heavier
Album_Tours = tours_album.copy()

Album_Tours['Album_ReleaseDate'] = pd.to_datetime(Album_Tours['Album_ReleaseDate'])
Album_Tours['Tour_StartDate'] = pd.to_datetime(Album_Tours['Tour_StartDate'], errors = 'coerce')
Album_Tours['Tour_EndDate'] = pd.to_datetime(Album_Tours['Tour_EndDate'], errors = 'coerce')

if 'DateDiff_AlbumRel_TourStart' not in Album_Tours.columns:
    Album_Tours['DateDiff_AlbumRel_TourStart'] = (
        Album_Tours['Tour_StartDate'] - Album_Tours['Album_ReleaseDate']
    ).dt.days

def assign_weight(album):
    if album in ['Fearless', 'Speak Now', 'Red', '1989', 'Reputation', 'Midnights']:
        return 2.0
    elif album in ['Lover', 'folkore', 'evermore', 'The Tortured Poets Department']:
        return 0.5
    else:
        return 1

Album_Tours['Weight'] = Album_Tours['Album_Name'].apply(assign_weight)

diff_date_albums = Album_Tours.dropna(subset = ['DateDiff_AlbumRel_TourStart']).copy()

weighted_avg_days = np.average(
    diff_date_albums['DateDiff_AlbumRel_TourStart'], weights = diff_date_albums['Weight']
)
unweighted_avg_days = diff_date_albums['DateDiff_AlbumRel_TourStart'].mean()

weighted_avg_days = weighted_avg_days.round()
unweighted_avg_days = unweighted_avg_days.round()

print(f'Weighted average between album release and tour start is {weighted_avg_days} days')
print(f'Unweighted average between album release and tour start is {unweighted_avg_days} days')

Album_Tours = Album_Tours.sort_values('Tour_StartDate')
Album_Tours['Days_Between_Tours'] = Album_Tours['Tour_StartDate'].diff().dt.days
avg_days_btwn_tours = Album_Tours['Days_Between_Tours'].mean()

# print(f'Predicting {avg_days_btwn_album_tour:.0f} days between the album release and the next tour start date.')

Showgirl_ReleaseDate = pd.to_datetime(
    tours_album.loc[tours_album['Album_Name'] == 'The Life of a Showgirl', 'Album_ReleaseDate'].iloc[0]
    )
Showgirl_Tour_StartDate = Showgirl_ReleaseDate + pd.Timedelta(days = weighted_avg_days)
Showgirl_Tour_StartDate_f = Showgirl_Tour_StartDate.strftime('%B %d, %Y')
print(f'Based on our prediction of {weighted_avg_days:.0f} days between album release and the next tour'
      f', we expected The Life of a Showgirl tour will start on {Showgirl_Tour_StartDate_f}')




#predicting starting location
for col in ['NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']:
    if col not in tour_summary.columns:
        tour_summary[col] = np.nan
        
City_Start = merged_tours.merge(
    tour_summary[['Tour_ID', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']],
    on='Tour_ID',
    how='left'
)

City_Start.columns = City_Start.columns.str.strip()  # remove whitespace

cols_to_drop = [c for c in City_Start.columns if c.startswith('Revenue') or c.startswith('Venue_Capacity')]
if cols_to_drop:
    City_Start = City_Start.drop(columns=cols_to_drop)

City_Start['GapDays'] = (City_Start['Tour_StartDate'] - City_Start['Album_ReleaseDate']).dt.days
City_Start['StartMonth'] = City_Start['Tour_StartDate'].dt.month

for col in ['Revenue', 'Venue_Capacity', 'Attendance']:
    if col not in tour_summary.columns:
        tour_summary[col] = np.nan

City_Start = City_Start.merge(tour_summary[['Tour_ID', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']]
                              , on = 'Tour_ID'
                              , how = 'left')

#resolving column dropping error
for col in ['NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']:
    if col not in City_Start.columns:
        City_Start[col] = 0

City_Start.fillna(0, inplace = True)

print(City_Start.shape)
print(City_Start.head())


city_encoder = LabelEncoder()
y_city = city_encoder.fit_transform(City_Start['City'].astype(str))
X_city = City_Start[['GapDays', 'StartMonth', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']].fillna(0)
city_clf = RandomForestClassifier(random_state = 13).fit(X_city, y_city)

#next_date = np.array([[predicted_gap, Showgirl_Tour_StartDate.month, 0, 0, 0, 0]])
next_date_df = pd.DataFrame(
    [[weighted_avg_days, Showgirl_Tour_StartDate.month, 0, 0, 0, 0]]
    , columns = ['GapDays', 'StartMonth', 'NumCities', 'NumCountries', 'Revenue', 'Venue_Capacity']
)
predicted_city = city_encoder.inverse_transform(city_clf.predict(next_date_df))[0]
predicted_region = merged_tours.loc[merged_tours['City'] == predicted_city, 'Region'].mode()[0]


# #adding freq since previous model predicted Tokyo as the start which doesn't feel correct
# city_freq = merged_tours['City'].value_counts(normalize = True)
# city_prob = city_clf.predict_proba(next_date_df)[0]
# prob_df = pd.DataFrame({'City': city_encoder.classes_, 'ModelProb': city_prob})
# prob_df['Frequency'] = prob_df['City'].map(city_freq).fillna(0)

# prob_df['CombinedScore'] = 0.5 * prob_df['ModelProb'] + 0.5 * prob_df['Frequency']
# prob_df = prob_df.sort_values('CombinedScore', ascending = False).reset_index(drop = True)

# #rank
# prob_df['Rank'] = prob_df.index + 1

# print(f'The next tour will most likely start in {predicted_city}, {predicted_region}.')

# #print(prob_df.head(10))



##simulate a full tour
np.random.seed(13)
random.seed(13)

#use past tour routes
region_routes = (merged_tours.sort_values('Date')
                 .groupby(['Region', 'Tour_ID'])['City']
                 .apply(list)
                )

#markov chain
transition_count = defaultdict(Counter)
for route in region_routes:
    for a, b in zip(route[:-1], route[1:]):
        transition_count[a][b] += 1

transition_probability = {
    a: {b: count / sum(counter.values()) for b, count in counter.items()}
    for a, counter in transition_count.items()
}

#take earlier predicted starting city, Glendale
tour_cities = [predicted_city]  #need list
current_city = predicted_city
avg_num_shows = int(tour_summary['NumCities'].mean() * 0.8)

for i in range(avg_num_shows - 1):
    if current_city in transition_probability:
        next_city = np.random.choice(
            list(transition_probability[current_city].keys())
            , p = list(transition_probability[current_city].values())
        )
    else:
        region_cities = merged_tours.loc[
            (merged_tours['Region'] == predicted_region)
            & (merged_tours['Venue_ID'].isin(stadiums_open['Venue_ID']))
            , 'City'].unique()
        next_city = np.random.choice(region_cities)

    #do not want to go back to a city already visited even if this has happened with London
    if next_city not in tour_cities:
        tour_cities.append(next_city)
        current_city = next_city


#avg days between shows historically
merged_tours = merged_tours.sort_values(['Tour_ID', 'Date', 'City'])

merged_tours['NextCity'] = merged_tours.groupby('Tour_ID')['City'].shift(-1)
merged_tours['NextDate'] = merged_tours.groupby('Tour_ID')['Date'].shift(-1)

merged_tours['GapDays'] = np.where(
    merged_tours['City'] != merged_tours['NextCity']
    , (merged_tours['NextDate'] - merged_tours['Date']).dt.days
    , np.nan
# avg_days_btwn_gap = merged_tours['GapDays'].median()
)

city_change_gap = merged_tours.dropna(subset = ['GapDays'])
median_gap = city_change_gap['GapDays'].median()
mean_gap = city_change_gap['GapDays'].mean()
avg_days_btwn_gap = round(median_gap + 0.5)


#review attendance and add extra nights
tour_plan = []


# avg_days_btwn = 3
current_date = Showgirl_Tour_StartDate

#evaluate attendance growth
rep_avg = merged_tours.loc[merged_tours['Album_Name'] == 'Reputation', 'Attendance'].mean()
eras_avg = merged_tours.loc[merged_tours['Album_Name'] == 'Midnights', 'Attendance'].mean()
attendance_growth = eras_avg / rep_avg #if rep_avg and not np.isnan(rep_avg) else 1.1


#NA cities
for city in tour_cities:
    subset = merged_tours.loc[merged_tours['City'] == city]
    venue = subset['Venue'].mode()[0] if not subset.empty and not subset['Venue'].mode().empty else 'Unknown Venue'
    avg_attendance = subset['Attendance'].mean() if not subset.empty else np.nan
    avg_capacity = subset['Venue_Capacity'].mean() if not subset.empty else np.nan

    nights_amount = 1
    reason = 'Normal'

    #overall attendance
    if pd.notna(avg_attendance):
        predicted_attendance = avg_attendance * attendance_growth
    else:
        predicted_attendance = np.nan

    #add more nights
    if pd.notna(predicted_attendance) and pd.notna(avg_capacity):
        ratio = predicted_attendance / avg_capacity
        if ratio > 1.6:
            nights_amount = 5
            reason = 'Massive demand'
        if ratio > 1.3:
            nights_amount = 3
            reason = 'High demand'
        if ratio > 1.1:
            nights_amount = 2
            reason = 'Increased demand'

    tour_plan.append({
        'City' : city
        , 'Venue': venue
        , 'Nights' : nights_amount
        , 'Reason' : reason
        , 'Start_Date' : current_date.strftime('%Y-%m-%d')
    })

    total_days = nights_amount + avg_days_btwn_gap
    current_date += pd.Timedelta(days = total_days)

tour_plan_df = pd.DataFrame(tour_plan)
# print(tour_plan_df.to_string(index = False))


##world tour
full_tour = tour_plan_df.copy()
current_city = tour_plan_df['City'].iloc[-1]
current_date = pd.to_datetime(tour_plan_df['Start_Date'].iloc[-1]) + pd.Timedelta(days=avg_days_btwn_gap)
world_regions = ['Europe', 'Asia', 'Oceania', 'Other']


region_routes_world = merged_tours.sort_values('Date').groupby(['Region', 'Tour_ID'])['City'].apply(list)
transition_count_world = defaultdict(Counter)
for route in region_routes_world:
    for a, b in zip(route[:-1], route[1:]):
        transition_count_world[a][b] += 1

transition_probability_world = {
    a: {b: count / sum(counter.values()) for b, count in counter.items()}
    for a, counter in transition_count_world.items()
}

visited_cities = set(full_tour['City'].tolist())

for region in world_regions:
    # historical cities in region
    region_cities = merged_tours.loc[
        (merged_tours['Region'] == region) &
        (merged_tours['Venue_ID'].isin(stadiums_open['Venue_ID'])),
        ['City', 'Venue', 'Venue_Capacity', 'Country']
    ].drop_duplicates()

    if region_cities.empty:
        continue

    current_city_region = region_cities['City'].iloc[0]

    for _ in range(len(region_cities)):
        # use Markov chain if possible
        if current_city_region in transition_probability_world:
            next_city = np.random.choice(
                list(transition_probability_world[current_city_region].keys()),
                p=list(transition_probability_world[current_city_region].values())
            )
        else:
            remaining_cities = [c for c in region_cities['City'] if c not in visited_cities]
            if remaining_cities:
                next_city = np.random.choice(remaining_cities)
            else:
                break
        # skip already visited
        if next_city in visited_cities:
            remaining_cities = [c for c in region_cities['City'] if c not in visited_cities]
            if remaining_cities:
                next_city = np.random.choice(remaining_cities)
            else:
                break

        row = region_cities[region_cities['City'] == next_city].iloc[0]
        venue = row['Venue']
        country = row['Country']
        venue_capacity = row['Venue_Capacity']
        nights = 2
        reason = 'Normal'

        full_tour = pd.concat([full_tour, pd.DataFrame([{
            'City': next_city,
            'Venue': venue,
            'Venue_Capacity': venue_capacity,
            'Nights': nights,
            'Reason': reason,
            'Start_Date': current_date.strftime('%Y-%m-%d'),
            'Country': country
        }])], ignore_index=True)

        visited_cities.add(next_city)
        current_city_region = next_city
        current_date += pd.Timedelta(days=nights + avg_days_btwn_gap)

##full tour summary
world_summary = pd.DataFrame([{
    'Tour_ID': 'ShowgirlWorldTour',
    'Album_Name': 'The Life of a Showgirl',
    'Album_ReleaseDate': Showgirl_ReleaseDate,
    'Tour_StartDate': tour_plan_df['Start_Date'].iloc[0],
    'Tour_EndDate': full_tour['Start_Date'].iloc[-1],
    'NumCities': full_tour['City'].nunique(),
    'NumCountries': full_tour['Country'].nunique() if 'Country' in full_tour else np.nan,
    'Revenue': np.nan,
    'Venue_Capacity': full_tour['Venue_Capacity'].mean(),
    'Attendance': np.nan
}])
tour_summary = pd.concat([tour_summary, world_summary], ignore_index=True)


print(full_tour.to_string(index=False))
print(f"Avg days between shows: {avg_days_btwn_gap:.1f}")
print(f"Avg predicted nights per city: {full_tour['Nights'].mean():.2f}")
print(f'Avg predicted nights per city is {tour_plan_df['Nights'].mean():.2f}')
