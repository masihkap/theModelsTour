import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from geopy.distance import geodesic
import random
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

#file load
random.seed(13)
np.random.seed(13)

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
tours_album = safe_read_csv(tours_album_path, parse_dates=['Album_ReleaseDate','Tour_StartDate','Tour_EndDate'])
tour_dfs = []
for p in tour_file_paths:
    df = safe_read_csv(p, parse_dates=['Date'])
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

all_tours = pd.concat(tour_dfs, ignore_index=True, sort=False)
all_tours['Date'] = pd.to_datetime(all_tours['Date'], errors='coerce')

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

stadiums_open.to_csv('StadiumOpenCheck.csv', index=False)
all_tours.to_csv('Tours_check.csv', index = False)

all_tours = all_tours.merge(
    stadiums_open[['Venue_ID','Continent','Latitude','Longitude','State','Venue_Capacity']],
    on='Venue_ID',
    how='left',
    suffixes=('','_stad')
)
for c in ['Continent','Latitude','Longitude','State','Venue_Capacity']:
    if f'{c}_stad' in all_tours.columns:
        all_tours[c] = all_tours[c].combine_first(all_tours[f'{c}_stad'])
        all_tours.drop(columns=[f'{c}_stad'], inplace=True)
all_tours['Continent'] = all_tours['Continent'].fillna('Unknown').astype(str).str.title()


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
#print("Trained multinomial logistic model for continent transitions. classes:", list(le_to.classes_))

#city predictions
city_freq = all_tours['City'].value_counts().to_dict()

if 'Tour_ID' in all_tours.columns and 'Country' in all_tours.columns:
    cities_per_country = (
        all_tours.groupby(['Tour_ID','Country'])['City']
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
    candidate_cities = [c for c, _ in sorted(city_freq.items(), key=lambda x: -x[1])
                        if all_tours.loc[all_tours['City']==c,'Country'].iloc[0].title() == str(country).title()]
    selected = []
    for city in candidate_cities:
        if len(selected) >= n:
            break
        city_rows = all_tours[all_tours['City'] == city].sort_values('Date', ascending=False)
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

missing_latlng = predicted_df[predicted_df['Latitude'].isna() | predicted_df['Longitude'].isna()]
for i, row in missing_latlng.iterrows():
    vid = row['Venue_ID']
    if vid in stadiums_open['Venue_ID'].values:
        match = stadiums_open[stadiums_open['Venue_ID'] == vid].iloc[0]
        predicted_df.at[i, 'Latitude'] = match['Latitude']
        predicted_df.at[i, 'Longitude'] = match['Longitude']

city_coords = {r['City']:(r['Latitude'], r['Longitude']) for _, r in predicted_df.iterrows() if not pd.isna(r['Latitude']) and not pd.isna(r['Longitude'])}

#use historical tour for city path
city_transitions = defaultdict(Counter)
for tid, g in all_tours.sort_values('Date').groupby('Tour_ID'):
    cities = g['City'].tolist()
    for i in range(len(cities)-1):
        city_transitions[cities[i]][cities[i+1]] += 1


# next city based on distance + Markov + popularity
def next_city_score(last_city, candidate_city, last_coords, alpha=0.5, beta=2.0, gamma=2.0):
    dist_score = 1.0
    if last_coords and city_coords.get(candidate_city):
        dist_km = geodesic(last_coords, city_coords[candidate_city]).km
        dist_score = max(0.1, 3000 - dist_km)/3000.0
    hist_trans_count = city_transitions[last_city][candidate_city]
    total_trans = sum(city_transitions[last_city].values()) if city_transitions[last_city] else 1
    trans_prob = hist_trans_count / total_trans
    freq = predicted_df.loc[predicted_df['City']==candidate_city, 'HistFreq'].iloc[0]
    return alpha*dist_score + beta*trans_prob + gamma*(freq/max(1,predicted_df['HistFreq'].max()))

#gaps between cities
all_tours_sorted = all_tours.sort_values(['Tour_ID','Date'])
all_tours_sorted['NextDate'] = all_tours_sorted.groupby('Tour_ID')['Date'].shift(-1)
all_tours_sorted['NextCity'] = all_tours_sorted.groupby('Tour_ID')['City'].shift(-1)
all_tours_sorted['GapDays'] = np.where(
    all_tours_sorted['City'] != all_tours_sorted['NextCity'],
    (all_tours_sorted['NextDate'] - all_tours_sorted['Date']).dt.days,
    np.nan
)
city_change_gap = all_tours_sorted.dropna(subset=['GapDays'])
median_gap = city_change_gap['GapDays'].median()
avg_days_btwn_gap = int(round(median_gap if pd.notna(median_gap) else 3))

all_tours_sorted['StayNights'] = np.where(
    all_tours_sorted['City'] == all_tours_sorted['NextCity'],
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
        weighted_avg_days = 270
else:
    weighted_avg_days = 270

Showgirl_ReleaseDate = pd.to_datetime(
    tours_album.loc[tours_album['Album_Name']=='The Life of a Showgirl','Album_ReleaseDate'].iloc[0]
    ) if 'Album_Name' in tours_album.columns else pd.Timestamp.today()
Showgirl_Tour_StartDate = Showgirl_ReleaseDate + pd.Timedelta(days=weighted_avg_days)
print(f"Predicted Showgirl tour start: {Showgirl_Tour_StartDate.date()} ")

#tour planning
remaining = list(predicted_df['City'])
fixed_continent_order = ["North America", "South America", "Oceania", "Asia", "Europe"]
continent_sequence_remaining = [c for c in fixed_continent_order if c in predicted_df['Continent'].unique()]

# for some reason Rogers Centre is missing despite it being in both files, type and name matching
# mask = (predicted_df['City'].str.lower() == 'toronto') & (predicted_df['Venue'].str.lower() == 'rogers centre')
# predicted_df.loc[mask, 'Latitude'] = 43.6416599
# predicted_df.loc[mask, 'Longitude'] = -79.3891976

na_cities = [c for c in remaining if predicted_df.loc[predicted_df['City']==c,'Continent'].iloc[0] == "North America"]
start_city = sorted(na_cities, key=lambda c: -predicted_df.loc[predicted_df['City']==c,'HistFreq'].iloc[0])[0] if na_cities else remaining[0]
start_row = predicted_df[predicted_df['City']==start_city].iloc[0]
current_date = Showgirl_Tour_StartDate
tour_plan = []
visited = set()
attendance_growth = 1.1

last_continent = start_row['Continent'].strip().title()

def compute_nights(city):
    base_nights = int(round(city_base_nights.get(city, 1) * attendance_growth))
    nights = max(2, min(8, base_nights))
    avg_att = all_tours.groupby('City')['Attendance'].mean().get(city, np.nan)
    cap = predicted_df.set_index('City')['Venue_Capacity'].get(city, np.nan)
    reason = 'Base+Growth'
    if pd.notna(avg_att) and pd.notna(cap) and cap > 0:
        ratio = (avg_att * attendance_growth) / cap
        if ratio > 1.6:
            nights = max(nights, 5)
            reason = 'Massive demand'
        elif ratio > 1.3:
            nights = max(nights, 3)
            reason = 'High demand'
        elif ratio > 1.1:
            nights = max(nights, 2)
            reason = 'Increased demand'
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

        next_city = min(cont_cities, key=lambda c: geodesic(last_coords, city_coords[c]).km if last_coords and city_coords.get(c) else np.inf)
        row = predicted_df[predicted_df['City']==next_city].iloc[0]
        next_coords = city_coords.get(next_city)
        nights, reason = compute_nights(next_city)

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

        visited.add(next_city)
        remaining.remove(next_city)
        last_city = next_city
        last_coords = next_coords

        # Correct continent-gap logic
        continent_changed = last_continent != row['Continent']
        gap_days = 14 if continent_changed else avg_days_btwn_gap
        current_date += pd.Timedelta(days=nights + gap_days)
        last_continent = row['Continent']

        made_progress = True
        break
    
#output
tour_plan_df = pd.DataFrame(tour_plan)

pd.set_option('display.max_rows', 400)
print(tour_plan_df[['Start_Date','Venue','City','State','Country','Continent','Nights','Reason','Venue_Capacity', 'Latitude', 'Longitude']].to_string(index=False))

tour_plan_df.to_csv('Predicted_Showgirl_Tour.csv', index=False)
print("Predicted tour plan saved to Predicted_Showgirl_Tour.csv")

