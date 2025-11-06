import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pycountry_convert as pc
import pycountry
from tqdm import tqdm
import us
import os
import json

tqdm.pandas() #status bar progress



# Eras sheet has latitude/longitude data from a previous project I did

ErasStadium = pd.read_csv('ErasTour_Post.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
ErasStadium_PostCleanse = ErasStadium.copy()
StadiumList_Eras = ErasStadium.drop(['Date', 'Opening acts', 'Attendance', 'Tour_ID'], axis = 1, errors = 'ignore')
#print(ErasStadium.head())

#other tours does not have this information
FearlessStadium = pd.read_csv('FearlessTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
SpeakNowStadium = pd.read_csv('SpeakNowTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
RedStadium = pd.read_csv('RedTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
Stadium1989 = pd.read_csv('1989Tour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
ReputationStadium = pd.read_csv('ReputationTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)


##had to find which files had these values since I did not know so took different approach from earlier
find_value_Tiger = 'Tiger Stadium'
if find_value_Tiger in FearlessStadium['Venue'].values:
    FearlessStadium.replace(find_value_Tiger, 'LSU Tiger Stadium', inplace = True)
else:
    print(f'{find_value_Tiger} was not found')

# if find_value_Tiger in FearlessStadium['Venue'].values:
#     print(f'{find_value_Tiger} was found')
# else:
#     print(f'{find_value_Tiger} was not found')

# ##update country based off of city; again different approach from either above
# England_Cities = ['Liverpool', 'London']
# ErasStadium.loc[ErasStadium['City'].isin(England_Cities), 'Country'] = 'England'
# ErasStadium.loc[ErasStadium['City'] == 'Edinburg', 'Country'] = 'Scotland'
# ErasStadium.loc[ErasStadium['City'] == 'Cardiff', 'Country'] = 'Wales'

ErasStadium_PostCleanse.to_csv('ErasTour_PostCleanse.csv', index = False, encoding = 'utf-8')
FearlessStadium.to_csv('FearlessTour_PostCleanse.csv', index = False, encoding = 'utf-8')
SpeakNowStadium.to_csv('SpeakNowTour_PostCleanse.csv', index = False, encoding = 'utf-8')
RedStadium.to_csv('RedTour_PostCleanse.csv', index = False, encoding = 'utf-8')
Stadium1989.to_csv('1989Tour_PostCleanse.csv', index = False, encoding = 'utf-8')
ReputationStadium.to_csv('ReputationTour_PostCleanse.csv', index = False, encoding = 'utf-8')
print(f'Stadium, City and country name cleansing complete.')

#Washington, D.C. keeps formatting oddly
stadium_dfs = [SpeakNowStadium, FearlessStadium, RedStadium, Stadium1989, ReputationStadium, ErasStadium]
for df in stadium_dfs:
    if 'City' in df.columns:
        df['City'] = (
            df['City']
            .astype(str)
            .str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", '', regex=False)
            .str.replace(r'(?i)^washington(\s*,?\s*d\.?c\.?)?$', 'Washington, D.C.', regex=True)
        )


StadiumsCombined = pd.concat([FearlessStadium, SpeakNowStadium, RedStadium, Stadium1989, ReputationStadium]
                             , ignore_index = True)
StadiumsCombined.drop(['Date', 'Opening acts', 'Attendance', 'Tour_ID', 'Revenue'], axis = 1, inplace = True, errors = 'ignore')
StadiumsCombinedCount1 = len(StadiumsCombined)

# remove duplicates
# StadiumsCombined = StadiumsCombined.drop_duplicates()
# StadiumsPreCountDupDrop = len(StadiumsCombined)

#add columns so the shape matches Eras
StadiumsCombined['Latitude'] = None
StadiumsCombined['Longitude'] = None

#StadiumsCountEras = len(ErasStadium)

#I keep adding this everywhere 
for df in [ErasStadium, StadiumsCombined]:
    for col in ['State', 'Latitude', 'Longitude', 'Country']:
        if col not in df.columns:
            df[col] = np.nan


#combine all lists
StadiumList = pd.concat([StadiumList_Eras, StadiumsCombined], ignore_index = True).drop_duplicates()
print(f'Stadium List has been created')

#cities not matching
city_fixes = {
    'las vegas': 'Paradise'
    , 'los angeles': 'Inglewood'
}

StadiumList['City'] = StadiumList['City'].str.strip().str.lower()
StadiumList['City'] = StadiumList['City'].replace(city_fixes)

# ##may need in the future based on deprecation warning
# StadiumList_Pre = [ErasStadium, StadiumsCombined]
# StadiumList_Pre = [df.dropna(axis=1, how='all') for df in StadiumList_Pre]
# StadiumList = pd.concat(StadiumList_Pre, ignore_index=True).drop_duplicates()


StadiumAltNames_dict = {
    'Venue': [
        'Etihad Stadium', 'nib Stadium', 'Acer Arena', 'Allphones Arena', 'ANZ Stadium',
        'Scotiabank Place', 'Air Canada Centre', 'Investors Group Field', 'MTS Centre',
        'Manchester Arena', 'Manchester Evening News Arena', '3Arena', 'The O2',
        'Mount Smart Stadium', 'Vector Arena', 'Palacio de los Deportes', 'Cowboys Stadium',
        'Philips Arena', 'BJCC Arena', 'CenturyLink Center', 'CenturyTel Center',
        'FirstEnergy Stadium', 'Quicken Loans Arena', 'Sports Authority Field at Mile High',
        'Gila River Arena', 'Jobing.com Arena', 'Minute Maid Park',
        'Bankers Life Fieldhouse', 'Conseco Fieldhouse',
        'GEHA Field at Arrowhead Stadium', 'Sprint Center', 'Staples Center',
        'Cardinal Stadium', 'American Airlines Arena', 'Mercedes-Benz Superdome',
        'New Orleans Arena', 'Chesapeake Energy Arena', 'Ford Center',
        'CenturyLink Center Omaha', 'Qwest Center Omaha', 'Amway Center',
        'Wachovia Center', 'Heinz Field', 'Rose Garden Arena', 'PNC Arena', 'RBC Center',
        'Power Balance Pavilion', 'Sleep Train Arena', 'CenturyLink Field',
        'Scottrade Center', 'St. Pete Times Forum', 'Tampa Bay Times Forum',
        'Verizon Center', 'Verizon Center', 'University of Phoenix', 'FedExField',
        'VELTINS-Arena',
        'Paris La Defense Arena', 'BT Murrayfield Stadium', "Caesar's Superdome", 'BC Place',
        'Roberts Municipal Stadium', 'Jacksonville Veterans Memorial Arena',
        'Mandalay Bay Events Center', 'BamaJam Farms', 'Amphitheatre Concert Grounds',
        'Big Valley Park', 'Country Thunder Festival', 'Cheyenne Frontier Days Arena',
        'Barnett Arena', 'North Dakota State Fair Grandstand', 'Wachovia Spectrum',
        'Soo Pass Ranch', 'Arena at Gwinnett Center', 'Bi-Lo Center',
        'Time Warner Cable Arena', 'Verizon Arena', 'Mellon Arena',
        'Amway Arena', 'BankAtlantic Center', 'American Bank Center Arena',
        'The Palace of Auburn Hills', 'Wells Fargo Arena', 'iWireless Center',
        'LSU Tiger Stadium', 'Imperial Ballroom', 'Cavendish Beach Festival Grounds',
        'Olympic Gymnastics Arena', 'AsiaWorld–Arena', 'Sportpaleis van Ahoy',
        'LG Arena', 'Burswood Dome', 'MEIS Ancol', 'City of Rock',
        'SSE Hydro', 'Melbourne Cricket Ground'
    ],
    'City': [
        'Melbourne', 'Perth', 'Sydney', 'Sydney', 'Sydney',
        'Ottawa', 'Toronto', 'Winnipeg', 'Winnipeg',
        'Manchester', 'Manchester', 'Dublin', 'Dublin',
        'Auckland', 'Auckland', 'Madrid', 'Arlington',
        'Atlanta', 'Birmingham', 'Bossier City', 'Bossier City',
        'Cleveland', 'Cleveland', 'Denver',
        'Glendale', 'Glendale', 'Houston',
        'Indianapolis', 'Indianapolis',
        'Kansas City', 'Kansas City', 'Los Angeles',
        'Louisville', 'Miami', 'New Orleans',
        'New Orleans', 'Oklahoma City', 'Oklahoma City',
        'Omaha', 'Omaha', 'Orlando',
        'Philadelphia', 'Pittsburgh', 'Portland', 'Raleigh', 'Raleigh',
        'Sacramento', 'Sacramento', 'Seattle',
        'St. Louis', 'Tampa', 'Tampa',
        'Washington', 'Washington, D.C.', 'Glendale', 'Landover',
        'Gelsenkirchen',
        'Paris', 'Edinburgh', 'New Orleans', 'Vancouver',
        'Evansville', 'Jacksonville', 'Paradise', 'New Brockton',
        'Cadott', 'Craven', 'Twin Lakes', 'Cheyenne',
        'Rapid City', 'Minot', 'Philadelphia', 'Detroit Lakes',
        'Duluth', 'Greenville', 'Charlotte', 'North Little Rock',
        'Pittsburgh', 'Orlando', 'Sunrise', 'Corpus Christi',
        'Auburn Hills', 'Des Moines', 'Moline', 'Baton Rouge',
        'Nassau', 'Cavendish', 'Seoul', 'Hong Kong',
        'Rotterdam', 'Birmingham', 'Perth', 'Jakarta',
        'Winchester', 'Glasgow', 'Melbourne'
    ],
    'Country': [
        'Australia', 'Australia', 'Australia', 'Australia', 'Australia',
        'Canada', 'Canada', 'Canada', 'Canada',
        'England', 'England', 'Ireland', 'Ireland',
        'New Zealand', 'New Zealand', 'Spain', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'Germany',
        'France', 'United Kingdom', 'United States', 'Canada',
        'United States', 'United States', 'United States', 'United States',
        'United States', 'Canada', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'United States', 'United States', 'United States', 'United States',
        'The Bahamas', 'Canada', 'South Korea', 'China',
        'Netherlands', 'England', 'Australia', 'Indonesia',
        'United States', 'Scotland', 'Australia'
    ],
    'Alternate_Name': [
        'Marvel Stadium', 'HBF Park', 'Qudos Bank Arena', 'Qudos Bank Arena', 'Accor Stadium',
        'Canadian Tire Centre', 'Scotiabank Arena', 'Princess Auto Stadium', 'Canada Life Centre',
        'AO Arena', 'AO Arena', 'The O2', '3Arena',
        'Go Media Stadium', 'Spark Arena', 'Movistar Arena', 'AT&T Stadium',
        'State Farm Arena', 'Legacy Arena', 'Brookshire Grocery Arena', 'Brookshire Grocery Arena',
        'Huntington Bank Field', 'Rocket Arena', 'Empower Field At Mile High',
        'Desert Diamond Arena', 'Desert Diamond Arena', 'Daikin Park',
        'Gainbridge Fieldhouse', 'Gainbridge Fieldhouse',
        'Arrowhead Stadium', 'T-Mobile Center', 'Crypto.com Arena',
        'L&N Federal Credit Union Stadium', 'Kaseya Center', 'Caesars Superdome',
        'Smoothie King Center', 'Paycom Center', 'Paycom Center',
        'CHI Health Center', 'CHI Health Center', 'Kia Center',
        'Xfinity Mobile Arena', 'ACRISURE STADIUM', 'Moda Center', 'Lenova Center', 'Lenova Center',
        'ARCO Arena', 'ARCO Arena', 'Lumen Field',
        'Enterprise Center', 'Benchmark International Arena', 'Benchmark International Arena',
        'Capital One Arena', 'Capital One Arena', 'State Farm Stadium', 'Northwest Stadium',
        'Arena AufSchalke',
        'Paris La Défense Arena', 'Murrayfield Stadium', 'Caesars Superdome', 'BC Place Stadium',
        'Roberts Stadium', 'VyStar Veterans Memorial Arena', 'Michelob ULTRA Arena',
        'BamaJam Farms, Enterprise', 'Rock Fest Grounds', 'Country Thunder Saskatchewan Grounds',
        'Country Thunder Wisconsin Grounds', 'Frontier Park Arena',
        'The Monument (Barnett Arena)', 'ND State Fairgrounds Grandstand', 'The Spectrum',
        'We Fest Grounds', 'Gas South Arena', 'Bon Secours Wellness Arena',
        'Spectrum Center', 'Simmons Bank Arena', 'Civic Arena',
        'Amway Center', 'Amerant Bank Arena', 'American Bank Center',
        'The Palace of Auburn Hills', 'Wells Fargo Arena (Iowa Events Center)',
        'Vibrant Arena at The MARK', 'Tiger Stadium', 'Imperial Ballroom Atlantis',
        'Cavendish Beach Events Centre', 'KSPO Dome', 'AsiaWorld–Arena',
        'Rotterdam Ahoy', 'Resorts World Arena', 'Burswood Dome',
        'JIExpo Kemayoran', 'MGM Resorts Festival Grounds', 'OVO Hydro', 'MCG'
    ]
}

StadiumAltNames = pd.DataFrame(StadiumAltNames_dict)
altname_to_current = dict(
    zip(StadiumAltNames['Alternate_Name'].str.strip().str.lower(),
        StadiumAltNames['Venue'].str.strip())
)
StadiumList['Venue'] = StadiumList['Venue'].replace(altname_to_current)

StadiumList['Venue'] = StadiumList['Venue'].astype(str).replace('nan', '').str.strip().str.lower()

StadiumList['Venue'] = StadiumList['Venue'].str.title()

#add if stadium is open
ClosedStadium = ['Frank Erwin Center', 'Georgia Dome', 'The Palace of Auburn Hills', 'Roberts Municipal Stadium', 'Bradley Center'
                 , 'Burswood Dome', 'Wachovia Spectrum', 'Mellon Arena', 'Power Balance Pavilion', 'Sleep Train Arena']
StadiumList['Operational'] = np.where(StadiumList['Venue'].isin(ClosedStadium), 'Closed', 'Open')

#if same stadium has multiple capacities, use the one with the highest - lat/long seemed safest since stadiums can share name/country
capacity_cols = [c for c in StadiumList.columns if 'capacity' in c.lower() or 'attendance' in c.lower()]
cap_col = capacity_cols[0] if capacity_cols else None

def consolidate_group(grp):
    # keep row with max capacity if available
    if cap_col and cap_col in grp.columns:
        grp = grp.sort_values(by=cap_col, ascending=False)
    row = grp.iloc[0].copy()
    # average coordinates to smooth slight differences
    if 'Latitude' in grp and 'Longitude' in grp:
        row['Latitude'] = grp['Latitude'].mean(skipna=True)
        row['Longitude'] = grp['Longitude'].mean(skipna=True)
    return row

before = len(StadiumList)
StadiumList = (
    StadiumList
    .groupby(['Venue', 'City', 'State', 'Country'], as_index=False, dropna=False)
    .apply(consolidate_group)
    .reset_index(drop=True)
)
after = len(StadiumList)

print(f"Consolidated {before - after} near-duplicate venues.")

##old fixing duplicates caused by attendance
# if cap_col:
#     before = len(StadiumList)
#     StadiumList.sort_values(by=[cap_col], ascending=False, inplace=True)
#     StadiumList = StadiumList.drop_duplicates(subset=['Venue', 'Latitude', 'Longitude'], keep='first')
#     after = len(StadiumList)
#     print(f"Removed {before - after} duplicate venue entries using coordinates.")


#add primary key
StadiumList.insert(0, "Venue_ID", range(1, len(StadiumList) + 1))

#skip ones that already have lat/long
StadiumList_missing = StadiumList[
    (StadiumList['Latitude'].isna()) | (StadiumList['Latitude'] == '') |
    (StadiumList['Longitude'].isna()) | (StadiumList['Longitude'] == '')
].copy()

print(f"{len(StadiumList_missing)} stadiums need geocoding "
      f"out of {len(StadiumList)} total.")

#start geo data

#print(StadiumAltNames.shape[0])

# #add state
# if 'State' not in StadiumList.columns:
#     StadiumList['State'] = np.nan


#fix empty strings for later script to pick up
make_columns_exist = ['State', 'Latitude', 'Longitude', 'Country']
existing_cols = [col for col in make_columns_exist if col in StadiumList.columns]
StadiumList[existing_cols] = StadiumList[existing_cols].replace({'': np.nan})

#received type warning
StadiumList['State'] = StadiumList['State'].astype('string')
StadiumList['Country'] = StadiumList['Country'].astype('string')

geolocator = Nominatim(user_agent = 'GetLatLong', timeout = 10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1, max_retries = 3, error_wait_seconds = 5, swallow_exceptions = True)
reverse_geocode = RateLimiter(geolocator.reverse, min_delay_seconds = 1)

#add geocache for speed
geo_cache_file = "StadiumList_GeoCache.json"
if os.path.exists(geo_cache_file):
    with open(geo_cache_file, "r", encoding="utf-8") as f:
        geo_cache = json.load(f)
else:
    geo_cache = {}

#fix missing key return to _PostCleanse
def cache_key(venue, city, country):
    return f"{str(venue).strip().lower()}|{str(city).strip().lower()}|{str(country).strip().lower()}"


#want to capture which method worked; may investigate the City one more
def get_location(row):
    key = cache_key(row['Venue'], row['City'], row.get('Country', ''))
    if key in geo_cache:
        return geo_cache[key]

    search_variants = [
        f"{row['Venue']}, {row['City']}, {row.get('Country', '')}",
        f"{row['City']}, {row.get('Country', '')}"
    ]

    for query in search_variants:
        try:
            loc = geocode(query)
        except Exception:
            loc = None
        if loc:
            addr = loc.raw.get('address', {})
            result = {
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'state': addr.get('state'),
                'country': addr.get('country')
            }
            geo_cache[key] = result

            with open(geo_cache_file, 'w', encoding = 'utf-8') as f:  #cache file
                json.dump(geo_cache, f, ensure_ascii = False, indent = 2)
            return geo_cache[key]

    result = {'latitude': None, 'longitude': None, 'state': None, 'country': None}
    geo_cache[key] = result
    with open(geo_cache_file, 'w', encoding = 'utf-8') as f:  #cache file
        json.dump(geo_cache, f, ensure_ascii = False, indent = 2)
    return result

# Run geocoding only for missing ones
missing_geo = (
    StadiumList['Latitude'].isna() |
    StadiumList['Longitude'].isna() |
    StadiumList['State'].isna() |
    StadiumList['Country'].isna()
)

if missing_geo.any():
    print(f"Running geocode for {missing_geo.sum()} missing locations...")
    results = StadiumList.loc[missing_geo].progress_apply(get_location, axis = 1)
    lat_series = results.apply(lambda d: d.get('latitude') if d else None)
    lon_series = results.apply(lambda d: d.get('longitude') if d else None)
    state_series = results.apply(lambda d: d.get('state') if d else None)
    country_series = results.apply(lambda d: d.get('country') if d else None)
    # fill where StadiumList has missing values (don't overwrite existing non-null values)
    StadiumList.loc[missing_geo, 'Latitude'] = StadiumList.loc[missing_geo, 'Latitude'].fillna(lat_series)
    StadiumList.loc[missing_geo, 'Longitude'] = StadiumList.loc[missing_geo, 'Longitude'].fillna(lon_series)
    StadiumList.loc[missing_geo, 'State'] = StadiumList.loc[missing_geo, 'State'].fillna(state_series)
    StadiumList.loc[missing_geo, 'Country'] = StadiumList.loc[missing_geo, 'Country'].fillna(country_series)
else:
    print('No missing locations')

#geocache
with open(geo_cache_file, 'w', encoding='utf-8') as f:
    json.dump(geo_cache, f, ensure_ascii = False, indent = 2)

#issues with missing data so adding reverse geocode to pick up stragglers
still_missing = (
    (StadiumList['State'].isna() | StadiumList['Country'].isna()) &
    StadiumList['Latitude'].notna() & StadiumList['Longitude'].notna()
)
if still_missing.any():
    print(f"Reverse-geocoding {still_missing.sum()} rows to fill missing state/country...")

    def from_coords(row):
        try:
            loc = reverse_geocode(f"{row['Latitude']}, {row['Longitude']}", language='en')
            if loc:
                addr = loc.raw.get('address', {})
                return {
                    'state': addr.get('state'),
                    'country': addr.get('country')
                }
        except Exception:
            return {'state': None, 'country': None}
        return {'state': None, 'country': None}

    temp = StadiumList.loc[still_missing].progress_apply(from_coords, axis=1)
    StadiumList.loc[still_missing, 'State'] = StadiumList.loc[still_missing, 'State'].fillna(temp.apply(lambda d: d.get('state')))
    StadiumList.loc[still_missing, 'Country'] = StadiumList.loc[still_missing, 'Country'].fillna(temp.apply(lambda d: d.get('country')))


#get state abbreviations
def abbreviate_state(state, country):
    if pd.isna(state) or state.strip() == '':
        return state
    state = state.strip()
    if country == 'United States':
        s = us.states.lookup(state)
        return s.abbr if s else state
    elif country == 'Canada':
        for sub in pycountry.subdivisions.get(country_code='CA'):
            if sub.name.lower() == state.lower():
                return sub.code.split('-')[-1]  # ON, QC, etc.
        return state
    return state

StadiumList['State'] = StadiumList.apply(lambda x: abbreviate_state(x['State'], x['Country']), axis=1)


#get continents
country_to_continent_cache = {}

country_fixes = {
    'England': 'United Kingdom',
    'Scotland': 'United Kingdom',
    'Wales': 'United Kingdom',
    'Northern Ireland': 'United Kingdom',
    'United States of America': 'United States',
    'The Bahamas': 'Bahamas'
}

def get_continent_from_country(country: str) -> str:
    if not isinstance(country, str) or country.strip() == '':
        return 'Unknown'
    
    country = country_fixes.get(country.strip(), country.strip())
    if country in country_to_continent_cache:
        return country_to_continent_cache[country]
    
    try:
        country_code = pc.country_name_to_country_alpha2(country, cn_name_format = 'default')
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
    except Exception:
        continent_name = 'Unknown'

    country_to_continent_cache[country] = continent_name
    return continent_name

StadiumList['Continent'] = StadiumList['Country'].progress_apply(get_continent_from_country)

#total from concert csv; drop it
StadiumList = StadiumList[~(
    (StadiumList['Venue'].str.lower() == 'total') & (StadiumList['City'].str.lower() == 'total') & (StadiumList['Country'].str.lower() == 'total')
)]


#Create file
StadiumList.to_csv("StadiumList.csv", index = False, encoding = 'utf-8', doublequote = False)  ##fix Washington, D.C. duplicated with extra ""
print(f'StadiumList CSV created')

#geocache save
with open(geo_cache_file, 'w', encoding = 'utf-8') as f:  #cache file
                json.dump(geo_cache, f, ensure_ascii = False, indent = 2)


#Venue PK
def add_venue_id(tour, stadium, output_file):
    tour_files = pd.read_csv(tour)
    stadium_df = pd.read_csv(stadium)

    for col in ['Venue', 'City', 'Country']:
        if col in tour_files.columns:
            tour_files[col] = tour_files[col].astype(str).str.strip().str.lower()
        if col in stadium_df.columns:
            stadium_df[col] = stadium_df[col].astype(str).str.strip().str.lower()

    merged = tour_files.merge(stadium_df[['Venue_ID', 'Venue', 'City', 'Country']],
                              on = ['Venue', 'City', 'Country'],
                              how = 'left')
    merged.to_csv(output_file, index = False, encoding = 'utf-8')
    print(f'{tour} merged')
    return merged

tours = ['FearlessTour.csv', 'SpeakNowTour.csv', 'RedTour.csv', '1989Tour.csv', 'ReputationTour.csv', 'ErasTour_Post.csv']

for t in tours:
    if t.endswith('_Post.csv'):
        output = t.replace('_Post.csv', '_PostCleanse.csv')
    else:
        output = t.replace('.csv', '_PostCleanse.csv')
    add_venue_id(t, 'StadiumList.csv', output)



    


# add_venue_id('FearlessTour.csv', StadiumList, 'FearlessTour_PostCleanse.csv')
# add_venue_id('SpeakNowTour.csv', StadiumList, 'SpeakNowTour_PostCleanse.csv')
# add_venue_id('RedTour.csv', StadiumList, 'RedTour_PostCleanse.csv')
# add_venue_id('1989Tour.csv', StadiumList, '1989Tour_PostCleanse.csv')
# add_venue_id('ReputationTour.csv', StadiumList, 'ReputationTour_PostCleanse.csv')
# add_venue_id('ErasTour.csv', StadiumList, 'ErasTour_PostCleanse.csv')
print('Venue ID Added, files created.')
