import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from geopy.distance import geodesic
import random
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

#"randomness" recreation
random.seed(13)
np.random.seed(13)

#file load
tour_file_paths = [
    'FearlessTour_PostCleanse.csv', 'SpeakNowTour_PostCleanse.csv', 'RedTour_PostCleanse.csv',
    '1989Tour_PostCleanse.csv', 'ReputationTour_PostCleanse.csv', 'ErasTour_PostCleanse.csv'
]
stadium_path = 'StadiumList.csv'
tours_album_path = 'ToursPerAlbum.csv'

#make sure files are structured
def safe_read_csv(path, parse_dates=None):
    df = pd.read_csv(path)
    if parse_dates:
        for d in parse_dates:
            if d in df.columns:
                df[d] = pd.to_datetime(df[d], errors='coerce')
    return df

def ensure_cols(df, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    return df

def clean_text_cols(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna('').str.strip()
    return df

#file load and cleanse
stadiums = safe_read_csv(stadium_path)

##tours/albums
tours_album = safe_read_csv(tours_album_path, parse_dates=['Album_ReleaseDate','Tour_StartDate','Tour_EndDate'])
tour_dfs = []
for p in tour_file_paths:
    df = safe_read_csv(p, parse_dates=['Date'])
    if df.empty:
        continue
    df.columns = [c.strip() for c in df.columns]
    if 'Venue_Id' in df.columns and 'Venue_ID' not in df.columns:
        df['Venue_ID'] = df['Venue_Id']
        df.drop(columns=['Venue_Id'], inplace=True, errors=True)
    required_cols = ['Date','City','Country','Venue','Attendance','Revenue','Venue_Capacity','Tour_ID','Venue_ID','Album_Name']
    df = ensure_cols(df, required_cols)
    df = clean_text_cols(df, ['City','Country','Venue','Venue_ID','Album_Name'])
    df['City'] = df['City'].str.title()
    df['Venue'] = df['Venue'].str.title()
    df['Country'] = df['Country'].str.title()
    tour_dfs.append(df)
if not tour_dfs:
    raise ValueError("No tour files are found.")

all_tours = pd.concat(tour_dfs, ignore_index=True, sort=False)
all_tours['Date'] = pd.to_datetime(all_tours['Date'], errors='coerce')


##stadiums
stadiums['Venue_ID'] = stadiums.get('Venue_ID', pd.Series()).astype(str).str.strip()
stadiums['City'] = stadiums.get('City', pd.Series()).astype(str).str.strip().str.title()
stadiums['Continent'] = stadiums.get('Continent', pd.Series()).astype(str).str.strip().str.title()
stadiums_open = stadiums[stadiums.get('Operational', '').astype(str).str.lower() == 'open'].copy()
for col in ['Latitude', 'Longitude', 'Venue_Capacity']:
    if col in stadiums_open.columns:
        stadiums_open[col] = pd.to_numeric(stadiums_open[col], errors='coerce')

# Normalize Venue_ID in all_tours
all_tours['Venue_ID'] = pd.to_numeric(all_tours['Venue_ID'], errors='coerce').fillna(0).astype(int).astype(str).str.strip()
stadiums_open['Venue'] = stadiums_open['Venue'].str.strip().str.title()
all_tours['Venue'] = all_tours['Venue'].str.strip().str.title()

# #check df in case of errors
# stadiums_open.to_csv('StadiumOpenCheck.csv', index=False)
# all_tours.to_csv('Tours_check.csv', index = False)

#merge stadiums and tours 
all_tours = all_tours.merge(
    stadiums_open[['Venue_ID','Continent','Latitude','Longitude','State','Venue_Capacity']],
    on='Venue_ID',
    how='left',
    suffixes=('','_stad')
)
all_tours['Venue_Capacity'] = all_tours['Venue_Capacity_stad']
for c in ['Continent','Latitude','Longitude','State','Venue_Capacity']:
    if f'{c}_stad' in all_tours.columns:
        all_tours[c] = all_tours[c].combine_first(all_tours[f'{c}_stad'])
        all_tours.drop(columns=[f'{c}_stad'], inplace=True)
all_tours['Continent'] = all_tours['Continent'].fillna('Unknown').astype(str).str.title()

# ##filter out smaller venues
stadiums_open = stadiums_open[stadiums_open['Venue_Capacity'] >= 50000].copy()


#historical average check for comparison + limit predictive tour build
shows_per_tour = all_tours.groupby('Tour_ID')['Date'].nunique().rename('Shows').reset_index()
if not shows_per_tour.empty:
    avg_shows_per_tour = int(round(shows_per_tour['Shows'].mean()))
else:
    avg_shows_per_tour = 99 #fallback calculated from TourAnalysisPre.py

cities_per_tour = all_tours.groupby('Tour_ID')['City'].nunique().rename('Cities').reset_index()
if not cities_per_tour.empty:
    avg_cities_per_tour = float(cities_per_tour['Cities'].mean())
else:
    avg_cities_per_tour = 63 #fallback calculated from TourAnalysisPre.py

if 'Tour_Length' in tours_album.columns and not tours_album['Tour_Length'].isna().all():
    try:
        tours_album['Tour_Length'] = pd.to_timedelta(tours_album['Tour_Length'])
        avg_tour_length_days = int(round(tours_album['Tour_Length'].dt.days.mean()))
    except Exception:
        avg_tour_length_days = int(round(
            tours_album['Tour_EndDate'].sub(tours_album['Tour_StartDate']).dt.days.mean()
            )) if 'Tour_StartDate' in tours_album.columns else 360
else:
    # fallback estimate: avg_shows * median gap estimate
    all_tours_sorted = all_tours.sort_values(['Tour_ID','Date'])
    all_tours_sorted['NextDate'] = all_tours_sorted.groupby('Tour_ID')['Date'].shift(-1)
    all_tours_sorted['GapDays'] = (all_tours_sorted['NextDate'] - all_tours_sorted['Date']).dt.days
    median_gap = int(round(all_tours_sorted['GapDays'].median(skipna=True))) if not all_tours_sorted['GapDays'].isna().all() else 3
    avg_tour_length_days = int(round(avg_shows_per_tour * (median_gap + 1)))

# print(f'Historical averages: There were an average of {avg_shows_per_tour} shows, '
#       f' {avg_cities_per_tour:.1f} cities and length of {avg_tour_length_days} days per tour.', '\n\n')


#avg show attendance per tour
tour_summary = []
for tid, g in all_tours.groupby('Tour_ID'):
    total_attendance = g['Attendance'].sum()
    total_shows = g['Date'].nunique()
    avg_attendace = total_attendance/total_shows if total_shows > 0 else 0
    tour_summary.append({'Tour_ID': tid, 'Avg_Attendance_Per_Show': avg_attendace})

tour_summary_df = pd.DataFrame(tour_summary).sort_values('Tour_ID')

#regression for attendance growth
tour_summary_df['Prev_Avg'] = tour_summary_df['Avg_Attendance_Per_Show'].shift(1)
tour_summary_df['Growth_Rate'] = (tour_summary_df['Avg_Attendance_Per_Show'] / tour_summary_df['Prev_Avg']) - 1

growth_df = tour_summary_df.dropna(subset = ['Growth_Rate'])
if len(growth_df) >= 2:
    X = growth_df['Prev_Avg'].values.reshape(-1, 1)
    y = growth_df['Avg_Attendance_Per_Show'].values
    reg = LinearRegression().fit(X, y)

    last_att_avg = tour_summary_df['Avg_Attendance_Per_Show'].iloc[-1]
    predicted_att_avg = reg.predict(np.array([[last_att_avg]]))[0]
    att_growth = predicted_att_avg / last_att_avg
else:
    att_growth = 1.1

print(f'Predicted attendance growth is {att_growth}')


#continent transitions
frames = []
for tid, g in all_tours.sort_values('Date').groupby('Tour_ID'):
    g = g.sort_values('Date').reset_index(drop=True)
    if g.shape[0] < 2:
        continue
    for i in range(len(g)-1):
        a_cont = g.loc[i,'Continent'] if pd.notna(g.loc[i,'Continent']) else 'Unknown'
        b_cont = g.loc[i+1,'Continent'] if pd.notna(g.loc[i+1,'Continent']) else 'Unknown'
        days_since = (g.loc[i+1,'Date'] - g.loc[i,'Date']).days if pd.notna(g.loc[i+1,'Date']) and pd.notna(g.loc[i,'Date']) else np.nan
        month = g.loc[i,'Date'].month if pd.notna(g.loc[i,'Date']) else 0
        frames.append({'from_cont': a_cont, 'to_cont': b_cont, 'days_since': days_since, 'month': month})
trans_df = pd.DataFrame(frames)
if trans_df.empty:
    raise ValueError("No continent transitions found in historical data; can't train ML model.")


le_from = LabelEncoder().fit(trans_df['from_cont'])
le_to = LabelEncoder().fit(trans_df['to_cont'])
X = pd.DataFrame({
    'from_enc': le_from.transform(trans_df['from_cont']),
    'days_since': trans_df['days_since'].fillna(trans_df['days_since'].median()),
    'month': trans_df['month'].fillna(0)
})
y = le_to.transform(trans_df['to_cont'])

# multinomial logistic regression training
clf = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
clf.fit(X, y)

#city predictions
#remove single visited cities unless on Eras Tour
city_counts = all_tours['City'].value_counts().to_dict()
single_visit_cities = {city for city, count in city_counts.items() if count == 1}
eras_tour_id = {6, 7}
eras_city = set(all_tours[all_tours['Tour_ID'].isin(eras_tour_id)]['City'].unique())

single_visit_allowed = single_visit_cities & eras_city
single_visit_disallowed = single_visit_cities - eras_city

all_tours_filtered = all_tours[~all_tours['City'].isin(single_visit_disallowed)].copy()
city_freq = all_tours_filtered['City'].value_counts().to_dict()
city_freq = all_tours['City'].value_counts().to_dict()


if 'Tour_ID' in all_tours_filtered.columns and 'Country' in all_tours_filtered.columns:
    cities_per_country = (
        all_tours_filtered.groupby(['Tour_ID','Country'])['City']
        .nunique()
        .reset_index(name='NumCities')
    )
    avg_cities_per_country = cities_per_country.groupby('Country')['NumCities'].mean().to_dict()
else:
    avg_cities_per_country = {}
#print("Computed stats: #unique cities:", len(city_freq))

predicted_cities = []
for country, avg_n in avg_cities_per_country.items():
    n = max(1, int(round(avg_n)))
    candidate_cities = []
    for c, _ in sorted(city_freq.items(), key=lambda x: -x[1]):
        rows = all_tours_filtered.loc[all_tours_filtered['City'].str.lower() == c.lower(), 'Country']
        if rows.empty:
            continue
        city_country = rows.iloc[0].strip().title()
        if city_country == str(country).strip().title():
            candidate_cities.append(c)

    selected = []
    for city in candidate_cities:
        if len(selected) >= n:
            break
        city_rows = all_tours_filtered[all_tours_filtered['City'] == city].sort_values('Date', ascending=False)
        chosen = None
        for _, r in city_rows.iterrows():
            vid = str(r.get('Venue_ID','')).strip()
            if vid and vid in set(stadiums_open['Venue_ID']):
                chosen = stadiums_open[stadiums_open['Venue_ID'] == vid].iloc[0]
                break
        if chosen is None:
            cand = stadiums_open[(stadiums_open['City'].str.lower() == city.lower())]
            if not cand.empty:
                chosen = cand.iloc[0]
        if chosen is not None:
            predicted_cities.append({
                'City': city,
                'Venue_ID': chosen['Venue_ID'],
                'Venue': chosen.get('Venue', ''),
                'State': chosen.get('State', ''),
                'Country': chosen.get('Country', country),
                'Continent': chosen.get('Continent', 'Unknown'),
                'Latitude': chosen.get('Latitude', np.nan),
                'Longitude': chosen.get('Longitude', np.nan),
                'Venue_Capacity': chosen.get('Venue_Capacity', np.nan),
                'HistFreq': city_freq.get(city, 0)
            })
            selected.append(city)

predicted_df = pd.DataFrame(predicted_cities)
if predicted_df.empty:
    raise ValueError("No predicted cities were generated - check mapping between tour files and stadiums_open Venue_IDs.")


predicted_df['Continent'] = predicted_df['Continent'].astype(str).str.strip().str.title()

#some missing lat/long which is a problem for next step mapping
missing_latlng = predicted_df[predicted_df['Latitude'].isna() | predicted_df['Longitude'].isna()]
for i, row in missing_latlng.iterrows():
    vid = row['Venue_ID']
    if vid in stadiums_open['Venue_ID'].values:
        match = stadiums_open[stadiums_open['Venue_ID'] == vid].iloc[0]
        predicted_df.at[i, 'Latitude'] = match['Latitude']
        predicted_df.at[i, 'Longitude'] = match['Longitude']

city_coords = {r['City']:(r['Latitude'], r['Longitude']) for _, r in predicted_df.iterrows() if not pd.isna(r['Latitude']) and not pd.isna(r['Longitude'])}


#use historical city avg per tour to limit city number, prioritizing higher frequency
target_city_count = int(round(avg_cities_per_tour))
if len(predicted_df) > target_city_count:
    predicted_df = predicted_df.sort_values(['HistFreq', 'Venue_Capacity']
                                            , ascending = [False, False]).head(target_city_count).reset_index(drop = True)


#use historical tour for city path
city_transitions = defaultdict(Counter)
for tid, g in all_tours_filtered.sort_values('Date').groupby('Tour_ID'):
    cities = g['City'].tolist()
    for i in range(len(cities)-1):
        city_transitions[cities[i]][cities[i+1]] += 1


# next city based on distance + Markov + popularity
def next_city_score(last_city, candidate_city, last_coords, alpha=0.5, beta=2.0, gamma=2.0):
    dist_score = 1.0
    if last_coords and city_coords.get(candidate_city):
        try:
            dist_km = geodesic(last_coords, city_coords[candidate_city]).km
            dist_score = max(0.1, 3000 - dist_km)/3000.0
        except Exception:
            dist_score = 0.1
    hist_trans_count = city_transitions[last_city][candidate_city]
    total_trans = sum(city_transitions[last_city].values()) if city_transitions[last_city] else 1
    trans_prob = hist_trans_count / total_trans
    freq = predicted_df.loc[predicted_df['City']==candidate_city, 'HistFreq'].iloc[0]
    return alpha*dist_score + beta*trans_prob + gamma*(freq/max(1,predicted_df['HistFreq'].max()))

#gaps between cities
all_tours_sorted = all_tours_filtered.sort_values(['Tour_ID','Date']).copy()
all_tours_sorted['NextDate'] = all_tours_sorted.groupby('Tour_ID')['Date'].shift(-1)
all_tours_sorted['NextCity'] = all_tours_sorted.groupby('Tour_ID')['City'].shift(-1)
all_tours_sorted['NextContinent'] = all_tours_sorted.groupby('Tour_ID')['Continent'].shift(-1)

all_tours_sorted['GapDays'] = np.where(
    all_tours_sorted['City'] != all_tours_sorted['NextCity'],
    (all_tours_sorted['NextDate'] - all_tours_sorted['Date']).dt.days,
    np.nan
)
#increase for continent change
continent_jump_days = 14
all_tours_sorted['GapDays'] = np.where(
    (all_tours_sorted['City'] != all_tours_sorted['NextCity']) &
    (all_tours_sorted['Continent'] != all_tours_sorted['NextContinent']),
    all_tours_sorted['GapDays'] + continent_jump_days,
    all_tours_sorted['GapDays']
)

city_change_gap = all_tours_sorted.dropna(subset=['GapDays'])
median_gap = city_change_gap['GapDays'].median()
avg_days_btwn_gap = int(round(median_gap if pd.notna(median_gap) else 3))

all_tours_sorted['StayNights'] = np.where(
    all_tours_sorted['City'] == all_tours_sorted['City'].shift(-1),
    (all_tours_sorted['NextDate'] - all_tours_sorted['Date']).dt.days,
    1
)
all_tours_sorted['StayNights'] = all_tours_sorted['StayNights'].apply(lambda x: x if x>=1 else 1)
city_base_nights = all_tours_sorted.groupby('City')['StayNights'].mean().to_dict()


# Showgirl tour start; weighted for non-covid albums
if 'Album_ReleaseDate' in tours_album.columns and 'Tour_StartDate' in tours_album.columns:
    at = tours_album.copy()
    at['DateDiff'] = (at['Tour_StartDate'] - at['Album_ReleaseDate']).dt.days
    def assign_weight(album):
        if album in ['Fearless', 'Speak Now', 'Red', '1989', 'Reputation', 'Midnights']:
            return 2.0
        elif album in ['Lover', 'folkore', 'evermore', 'The Tortured Poets Department']:
            return 0.5
        else:
            return 1.0
    at['Weight'] = at['Album_Name'].apply(assign_weight) if 'Album_Name' in at.columns else 1.0
    diff_date_albums = at.dropna(subset=['DateDiff'])
    if not diff_date_albums.empty:
        weighted_avg_days = int(round(np.average(diff_date_albums['DateDiff'], weights=diff_date_albums['Weight'])))
    else:
        weighted_avg_days = 404 #unweighted average between album release and tour start dates
else:
    weighted_avg_days = 404 #unweighted average between album release and tour start dates

Showgirl_ReleaseDate = pd.to_datetime(
    tours_album.loc[tours_album['Album_Name']=='The Life of a Showgirl','Album_ReleaseDate'].iloc[0]
    ) if 'Album_Name' in tours_album.columns else pd.Timestamp.today()
Showgirl_Tour_StartDate = Showgirl_ReleaseDate + pd.Timedelta(days=weighted_avg_days)
print(f"Predicted Showgirl tour start: {Showgirl_Tour_StartDate.date()} ")

#tour planning
#if cities in same state are within 100 miles of eachother, remove the smaller stadium - CA and LA
def remove_close_small_stadiums(df, max_distance = 100):
    df = df.copy()
    to_remove = set()

    for state, g in df.groupby('State'):
        cities = g[['City','Latitude','Longitude','Venue_Capacity']].dropna(subset=['Latitude','Longitude']).to_dict('records')
        for i in range(len(cities)):
            for j in range(i+1, len(cities)):
                city1 = cities[i]
                city2 = cities[j]
                coords1 = (city1['Latitude'], city1['Longitude'])
                coords2 = (city2['Latitude'], city2['Longitude'])
                distance = geodesic(coords1, coords2).miles
                if distance < max_distance:
                    # remove the smaller stadium
                    if city1['Venue_Capacity'] <= city2['Venue_Capacity']:
                        to_remove.add(city1['City'])
                    else:
                        to_remove.add(city2['City'])
    
    return df[~df['City'].isin(to_remove)].reset_index(drop=True)

predicted_df = remove_close_small_stadiums(predicted_df, 100)



remaining = list(predicted_df['City'])

##hardcoded this due to modeling jumping around despite efforts to tame it
fixed_continent_order = ["North America", "South America", "Oceania", "Asia", "Europe"]
continent_sequence_remaining = [c for c in fixed_continent_order if c in predicted_df['Continent'].unique()]

na_cities = [c for c in remaining if predicted_df.loc[predicted_df['City']==c,'Continent'].iloc[0] == "North America"]
start_city = sorted(na_cities, key=lambda c: -predicted_df.loc[predicted_df['City']==c,'HistFreq'].iloc[0])[0] if na_cities else remaining[0]
start_row = predicted_df[predicted_df['City']==start_city].iloc[0]
current_date = Showgirl_Tour_StartDate
tour_plan = []
visited = set()

def compute_nights(city):
    base_nights = 2 #int(round(city_base_nights.get(city, 1) * att_growth))
    nights = max(2, base_nights) #no upper limit
    avg_att = all_tours_filtered.groupby('City')['Attendance'].mean().get(city, np.nan)
    upper_n_limit = predicted_df.set_index('City')['Venue_Capacity'].get(city, np.nan)
    reason = 'Base'
    if pd.notna(avg_att) and pd.notna(upper_n_limit) and upper_n_limit > 0:
        ratio = (avg_att * att_growth) / upper_n_limit
        if ratio > 2.75:
            nights = max(nights, 6)
            reason = 'Massive Demand'
        elif ratio > 2.25:
            nights = max(nights, 4)
            reason = 'High Demand'
        elif ratio > 1.75:
            nights = max(nights, 3)
            reason = 'Increased Demand'
    return nights, reason

nights, reason = compute_nights(start_city)
tour_plan.append({
    'Start_Date': current_date.strftime('%Y-%m-%d'),
    'Venue': start_row['Venue'],
    'City': start_row['City'],
    'State': start_row['State'],
    'Country': start_row['Country'],
    'Continent': start_row['Continent'],
    'Venue_Capacity': start_row['Venue_Capacity'],
    'Latitude': start_row['Latitude'],
    'Longitude': start_row['Longitude'],
    'Nights': nights,
    'Reason': reason
})
visited.add(start_city)
remaining.remove(start_city)
last_city = start_city
last_coords = city_coords.get(last_city)
last_continent = start_row['Continent']
current_date += pd.Timedelta(days=nights + avg_days_btwn_gap)

max_iterations = 1000
iteration = 0

while remaining and iteration < max_iterations:
    iteration += 1
    made_progress = False
    for target_cont in continent_sequence_remaining.copy():
        cont_cities = [c for c in remaining if predicted_df.loc[predicted_df['City']==c,'Continent'].iloc[0] == target_cont]
        if not cont_cities:
            continent_sequence_remaining.remove(target_cont)
            continue
        try:
            next_city = min(cont_cities, key=lambda c: geodesic(last_coords, city_coords[c]).km if last_coords and city_coords.get(c) else np.inf)
        except Exception:
            next_city = max(cont_cities, key = lambda c: predicted_df.loc[predicted_df['City'] == c, 'HistFreq'].iloc[0])
        row = predicted_df[predicted_df['City']==next_city].iloc[0]
        next_coords = city_coords.get(next_city)
        nights, reason = compute_nights(next_city)

        if last_continent != row['Continent']:
            gap_days = continent_jump_days
        else:
            gap_days = avg_days_btwn_gap
        current_date += pd.Timedelta(days=nights + gap_days)


        tour_plan.append({
            'Start_Date': current_date.strftime('%Y-%m-%d'),
            'Venue': row['Venue'],
            'City': row['City'],
            'State': row['State'],
            'Country': row['Country'],
            'Continent': row['Continent'],
            'Venue_Capacity': row['Venue_Capacity'],
            'Latitude': row['Latitude'],
            'Longitude': row['Longitude'],
            'Nights': nights,
            'Reason': reason
        })


        
        #current_date += pd.Timedelta(days=nights + gap_days)
        current_date += pd.Timedelta(days=nights)

        last_city = next_city
        last_coords = next_coords
        last_continent = row['Continent']

        visited.add(next_city)
        remaining.remove(next_city)

        made_progress = True
        break
    if not made_progress:
        break
    
#output
tour_plan_df = pd.DataFrame(tour_plan)

# predictive tour metrics
pred_num_cities = tour_plan_df['City'].nunique()
pred_num_shows = int(tour_plan_df['Nights'].sum())
pred_start = pd.to_datetime(tour_plan_df['Start_Date']).min() if not tour_plan_df.empty else pd.Timestamp.today()
pred_end = (pd.to_datetime(tour_plan_df['Start_Date']) + pd.to_timedelta(tour_plan_df['Nights'], unit='D')).max() if not tour_plan_df.empty else pred_start
pred_tour_length_days = (pred_end - pred_start).days if not tour_plan_df.empty else 0

# # historical metrics
hist_num_cities = int(round(avg_cities_per_tour))
hist_num_shows = int(round(avg_shows_per_tour))
hist_tour_length_days = int(round(avg_tour_length_days))

#eras specific metrics
eras_tour = all_tours[all_tours['Tour_ID'].isin(eras_tour_id)].copy()
if not eras_tour.empty:
    eras_num_cities = eras_tour['City'].nunique()
    eras_num_shows = eras_tour['Date'].nunique()
    eras_startdate = eras_tour['Date'].min()
    eras_enddate = eras_tour['Date'].max()
    eras_tour_length = (eras_enddate - eras_startdate).days
else:
    eras_num_cities = eras_num_shows = eras_tour_length = np.nan

comparison = pd.DataFrame([
    {'Metric': 'Number of Cities (avg)', 'Historical': hist_num_cities, 'Eras': eras_num_cities, 'Predicted': pred_num_cities},
    {'Metric': 'Number of Shows (avg)', 'Historical': hist_num_shows, 'Eras': eras_num_shows, 'Predicted': pred_num_shows},
    {'Metric': 'Tour Length (days avg)', 'Historical': hist_tour_length_days, 'Eras': eras_tour_length, 'Predicted': pred_tour_length_days}
])


print("\n=== Comparison (Historical vs Predicted) ===")
print(comparison.to_string(index=False), '\n\n')

# # save outputs
comparison.to_csv('Predicted_vs_Historical_Comparison.csv', index=False)
print("\nSaved Predicted_Showgirl_Tour.csv and Predicted_vs_Historical_Comparison.csv")

pd.set_option('display.max_rows', 400)
print(tour_plan_df[['Start_Date','Venue','City','State','Country','Continent','Nights','Reason','Venue_Capacity', 'Latitude', 'Longitude']].to_string(index=False))

tour_plan_df.to_csv('Predicted_Showgirl_Tour.csv', index=False)
print("Predicted tour plan saved to Predicted_Showgirl_Tour.csv")

