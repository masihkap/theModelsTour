import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Eras sheet has latitude/longitude data from a previous project I did
ErasStadiumCol = ['City', 'State', 'Country', 'Stadium', 'Latitude', 'Longitude']
ErasStadium = pd.read_csv('TaylorSwift_ErasTour_DatesStadiums_Geo.csv'
                          , usecols = ErasStadiumCol)
ErasStadium = ErasStadium.drop_duplicates()
ErasStadium = ErasStadium.rename(columns = {'Stadium' : 'Venue'})
ErasStadium['Country'] = ErasStadium['Country'].replace('United States of America', 'United States')
ErasStadium['Venue'] = ErasStadium['Venue'].replace("'Roger's Centre'", 'Rogers Centre')
#print(ErasStadium.head())

#other tours does not have this information
StadiumColumnsPre = ['City', 'Country', 'Venue']

FearlessStadium = pd.read_csv('FearlessTour.csv', usecols=StadiumColumnsPre)
SpeakNowStadium = pd.read_csv('SpeakNowTour.csv', usecols=StadiumColumnsPre)
RedStadium = pd.read_csv('RedTour.csv', usecols=StadiumColumnsPre)
Stadium1989 = pd.read_csv('1989Tour.csv', usecols=StadiumColumnsPre)
ReputationStadium = pd.read_csv('ReputationTour.csv', usecols=StadiumColumnsPre)


##had to find which files had these values since I did not know so took different approach from earlier
find_value_Am = 'Amsterdamn'
if find_value_Am in ErasStadium['City'].values:
    ErasStadium.replace(find_value_Am, 'Amsterdam', inplace = True)
else:
    print(f'{find_value_Am} was not found')

## Post run check
# if find_value in ErasStadium['City'].values:
#     print(f'{find_value} was found')
# else:
#     print(f'{find_value} was not found')

find_value_Wash = 'Washington'
if find_value_Wash in SpeakNowStadium['City'].values:
    SpeakNowStadium.replace(find_value_Wash, '"Washington, D.C."', inplace = True)
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

##update country based off of city; again different approach from either above
England_Cities = ['Liverpool', 'London']
ErasStadium.loc[ErasStadium['City'].isin(England_Cities), 'Country'] = 'England'
ErasStadium.loc[ErasStadium['City'] == 'Edinburg', 'Country'] = 'Scotland'
ErasStadium.loc[ErasStadium['City'] == 'Cardiff', 'Country'] = 'Wales'


StadiumsCombined = pd.concat([FearlessStadium, SpeakNowStadium, RedStadium, Stadium1989, ReputationStadium]
                             , ignore_index = True)
StadiumsCombinedCount1 = len(StadiumsCombined)

# remove duplicates
StadiumsCombined = StadiumsCombined.drop_duplicates()
StadiumsPreCountDupDrop = len(StadiumsCombined)

#add columns so the shape matches Eras
StadiumsCombined['Latitude'] = ''
StadiumsCombined['Longitude'] = ''

StadiumsCountEras = len(ErasStadium)

#combine all lists
StadiumList = pd.concat([ErasStadium, StadiumsCombined], ignore_index = True).drop_duplicates()

#add primary key
StadiumList.insert(0, "Venue_ID", range(1, len(StadiumList) + 1))

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
        'GEHA FIELD AT ARROWHEAD STADIUM', 'Sprint Center', 'Staples Center',
        'Cardinal Stadium', 'American Airlines Arena', 'Mercedes-Benz Superdome',
        'New Orleans Arena', 'Chesapeake Energy Arena', 'Ford Center',
        'CenturyLink Center Omaha', 'Qwest Center Omaha', 'Amway Center',
        'Wachovia Center', 'Heinz Field', 'Rose Garden Arena', 'PNC Arena', 'RBC Center',
        'Power Balance Pavilion', 'Sleep Train Arena', 'CenturyLink Field',
        'Scottrade Center', 'St. Pete Times Forum', 'Tampa Bay Times Forum',
        'Verizon Center', 'Verizon Center', 'University of Phoenix', 'FedExField',
        'VELTINS-Arena'

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
        'Gelsenkirchen'
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
        'Germany'
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
        'Arena AufSchalke'
    ]
}

StadiumAltNames = pd.DataFrame(StadiumAltNames_dict)

#print(StadiumAltNames.shape[0])

geolocator = Nominatim(user_agent = 'GetLatLong', timeout = 10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1, max_retries = 3, error_wait_seconds = 5, swallow_exceptions = True)


#want to capture which method worked; may investigate the City one more
def get_locpath(row):
    alt_row = StadiumAltNames[StadiumAltNames['Venue'].str.lower() == row['Venue'].lower()]
    if not alt_row.empty:
        alt_name = alt_row['Alternate_Name'].values[0]
        alternative = f"{alt_name}, {row['City']}, {row['Country']}"
        loc = geocode(alternative)
        if loc:
            return loc, "Alternative"
       
    venue = f"{row['Venue']}, {row['City']}, {row['Country']}"
    loc = geocode(venue)
    if loc:
        return loc, "Venue"  
        
    City = f"{row['City']}, {row['Country']}"
    loc = geocode(City)
    if loc:
        return loc, "City"
    
    return None, "Fail"

results = StadiumList.apply(lambda row: get_locpath(row), axis = 1)
StadiumList['Location'] = results.apply(lambda x: x[0])
StadiumList['Method'] = results.apply(lambda x: x[1])


StadiumList['Latitude'] = StadiumList['Location'].apply(lambda loc: loc.latitude if loc else None)
StadiumList['Longitude'] = StadiumList['Location'].apply(lambda loc: loc.longitude if loc else None)





#Create file
StadiumList.to_csv("StadiumList.csv", index = False, encoding = 'utf-8')
