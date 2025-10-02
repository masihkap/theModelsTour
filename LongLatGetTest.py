#Testing on a smaller dataset before trying to larger, combined one

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


ReputationStadium = pd.read_csv('ReputationTour.csv')

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
        'Verizon Center', 'Verizon Center', 'University of Phoenix', 'FedExField'
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
        'Washington', 'Washington, D.C.', 'Glendale', 'Landover'
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
        'United States', 'United States', 'United States', 'United States'
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
        'Capital One Arena', 'Capital One Arena', 'State Farm Stadium', 'Northwest Stadium'
    ]
}

StadiumAltNames = pd.DataFrame(StadiumAltNames_dict)

#print(StadiumAltNames.shape[0])

geolocator = Nominatim(user_agent = 'GetLatLong')
geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1, max_retries = 2, error_wait_seconds = 2)

#want to capture which method worked; may investigate the City one more
def get_locpath(row):
    alt_row = StadiumAltNames[StadiumAltNames['Venue'].str.lower() == row['Venue'].lower()]
    if not alt_row.empty:
        alt_name = alt_row['Alternate_Name'].values[0]
        alternative = f"{alt_name}, {row['City'], row['Country']}"
        loc = geocode(alternative)
        if loc:
            return loc, "Alternative"
       
    venue = f"{row['Venue'], row['City'], row['Country']}"
    loc = geocode(venue)
    if loc:
        return loc, "Venue"  
        
    City = f"{row['City'], row['Country']}"
    loc = geocode(City)
    if loc:
        return loc, "City"
    
    return None, "Fail"

results = ReputationStadium.apply(lambda row: get_locpath(row), axis = 1)
ReputationStadium['Location'] = results.apply(lambda x: x[0])
ReputationStadium['Method'] = results.apply(lambda x: x[1])


ReputationStadium['Latitude'] = ReputationStadium['Location'].apply(lambda loc: loc.latitude if loc else None)
ReputationStadium['Longitude'] = ReputationStadium['Location'].apply(lambda loc: loc.longitude if loc else None)

print(ReputationStadium)

