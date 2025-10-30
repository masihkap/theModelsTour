import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Eras sheet has latitude/longitude data from a previous project I did

ErasStadium = pd.read_csv('ErasTour_Post.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
ErasStadium.drop(['Date', 'Opening acts', 'Attendance', 'Tour_ID'], axis = 1, inplace = True, errors = 'ignore')
#print(ErasStadium.head())

#other tours does not have this information
FearlessStadium = pd.read_csv('FearlessTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
SpeakNowStadium = pd.read_csv('SpeakNowTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
RedStadium = pd.read_csv('RedTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
Stadium1989 = pd.read_csv('1989Tour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)
ReputationStadium = pd.read_csv('ReputationTour.csv').drop_duplicates(subset=['Venue', 'City', 'Country'], keep='first').reset_index(drop=True)


##had to find which files had these values since I did not know so took different approach from earlier
find_value_Wash = 'Washington'
if find_value_Wash in SpeakNowStadium['City'].values:
    SpeakNowStadium.replace(find_value_Wash, "Washington, D.C.", inplace = True)
else:
    print(f'{find_value_Wash} was not found')

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

ErasStadium.to_csv('ErasTour_PostCleanse.csv', index = False, encoding = 'utf-8')
FearlessStadium.to_csv('FearlessTour_PostCleanse.csv', index = False, encoding = 'utf-8')
SpeakNowStadium.to_csv('SpeakNowTour_PostCleanse.csv', index = False, encoding = 'utf-8')
RedStadium.to_csv('RedTour_PostCleanse.csv', index = False, encoding = 'utf-8')
Stadium1989.to_csv('1989Tour_PostCleanse.csv', index = False, encoding = 'utf-8')
ReputationStadium.to_csv('ReputationTour_PostCleanse.csv', index = False, encoding = 'utf-8')
print(f'Stadium, City and country name cleansing complete.')


StadiumsCombined = pd.concat([FearlessStadium, SpeakNowStadium, RedStadium, Stadium1989, ReputationStadium]
                             , ignore_index = True)
StadiumsCombined.drop(['Date', 'Opening acts', 'Attendance', 'Tour_ID', 'Revenue'], axis = 1, inplace = True, errors = 'ignore')
StadiumsCombinedCount1 = len(StadiumsCombined)

# remove duplicates
# StadiumsCombined = StadiumsCombined.drop_duplicates()
# StadiumsPreCountDupDrop = len(StadiumsCombined)

#add columns so the shape matches Eras
StadiumsCombined['Latitude'] = ''
StadiumsCombined['Longitude'] = ''

StadiumsCountEras = len(ErasStadium)

#combine all lists
StadiumList = pd.concat([ErasStadium, StadiumsCombined], ignore_index = True).drop_duplicates()
print(f'Stadium List has been created')

#add if stadium is open
ClosedStadium = ['Frank Erwin Center', 'Georgia Dome', 'The Palace of Auburn Hills', 'Roberts Municipal Stadium', 'Bradley Center'
                 , 'Burswood Dome', 'Wachovia Spectrum', 'Mellon Arena', 'Power Balance Pavilion', 'Sleep Train Arena']
StadiumList['Operational'] = np.where(StadiumList['Venue'].isin(ClosedStadium), 'Closed', 'Open')

#add primary key
StadiumList.insert(0, "Venue_ID", range(1, len(StadiumList) + 1))

#skip ones that already have lat/long
StadiumList_missing = StadiumList[
    (StadiumList['Latitude'].isna()) | (StadiumList['Latitude'] == '') |
    (StadiumList['Longitude'].isna()) | (StadiumList['Longitude'] == '')
].copy()

print(f"{len(StadiumList_missing)} stadiums need geocoding "
      f"out of {len(StadiumList)} total.")

geolocator = Nominatim(user_agent = 'GetLatLong', timeout = 10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1, max_retries = 3, error_wait_seconds = 5, swallow_exceptions = True)

cache = {}

def safe_geocode(query):
    if query in cache:
        return cache[query]
    loc = geocode(query)
    cache[query] = loc
    return loc

#start geo data
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
        'SSE Hydro'
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
        'Winchester', 'Glasgow'
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
        'United States', 'Scotland'
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
        'JIExpo Kemayoran', 'MGM Resorts Festival Grounds', 'OVO Hydro',
    ]
}

StadiumAltNames = pd.DataFrame(StadiumAltNames_dict)

#print(StadiumAltNames.shape[0])

#want to capture which method worked; may investigate the City one more
def get_locpath(row):
    alt_row = StadiumAltNames[StadiumAltNames['Venue'].str.lower() == row['Venue'].lower()]
    if not alt_row.empty:
        alt_name = alt_row['Alternate_Name'].values[0]
        alternative = f"{alt_name}, {row['City']}, {row['Country']}"
        loc = safe_geocode(alternative)
        if loc:
            return loc, "Alternative"
       
    venue = f"{row['Venue']}, {row['City']}, {row['Country']}"
    loc = safe_geocode(venue)
    if loc:
        return loc, "Venue"  
        
    City = f"{row['City']}, {row['Country']}"
    loc = safe_geocode(City)
    if loc:
        return loc, "City"
    
    return None, "Fail"

# Run geocoding only for missing ones
results = StadiumList_missing.apply(lambda row: get_locpath(row), axis=1)

StadiumList_missing['Location'] = results.apply(lambda x: x[0])
StadiumList_missing['Method'] = results.apply(lambda x: x[1])
StadiumList_missing['Latitude'] = StadiumList_missing['Location'].apply(lambda loc: loc.latitude if loc else None)
StadiumList_missing['Longitude'] = StadiumList_missing['Location'].apply(lambda loc: loc.longitude if loc else None)

StadiumList_missing.drop('Location', axis=1, inplace=True)

StadiumList.update(StadiumList_missing)
StadiumList = StadiumList.drop_duplicates(subset=['Venue', 'City'], keep='first').reset_index(drop=True)


#Create file
StadiumList.to_csv("StadiumList.csv", index = False, encoding = 'utf-8', doublequote = False)  ##fix Washington, D.C. duplicated with extra ""
print(f'StadiumList CSV created')


def add_venue_id(tour, stadium, output_file):
    tour_files = pd.read_csv(tour)

    merged = tour_files.merge(stadium[['Venue_ID', 'Venue', 'City', 'Country']],
                              on = ['Venue', 'City', 'Country'],
                              how = 'left')
    print(f'{tour} merged')
    merged.to_csv(output_file, index = False, encoding = 'utf-8')
    return merged

add_venue_id('FearlessTour.csv', StadiumList, 'FearlessTour_PostCleanse.csv')
add_venue_id('SpeakNowTour.csv', StadiumList, 'SpeakNowTour_PostCleanse.csv')
add_venue_id('RedTour.csv', StadiumList, 'RedTour_PostCleanse.csv')
add_venue_id('1989Tour.csv', StadiumList, '1989Tour_PostCleanse.csv')
add_venue_id('ReputationTour.csv', StadiumList, 'ReputationTour_PostCleanse.csv')
add_venue_id('ErasTour.csv', StadiumList, 'ErasTour_PostCleanse.csv')
print('Venue ID Added, files created.')
