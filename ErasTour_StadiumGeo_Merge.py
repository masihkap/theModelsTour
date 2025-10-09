import pandas as pd

# Eras sheet has latitude/longitude data from a previous project I did
ErasStadiumCol = ['City', 'State', 'Country', 'Stadium', 'Latitude', 'Longitude']
ErasStadium = pd.read_csv('TaylorSwift_ErasTour_DatesStadiums_Geo.csv'
                          )
ErasStadium = ErasStadium.drop_duplicates()
ErasStadium = ErasStadium.rename(columns = {'Stadium' : 'Venue'})
ErasStadium['Country'] = ErasStadium['Country'].replace('United States of America', 'United States')
ErasStadium['Country'] = ErasStadium['Country'].replace('Canda', 'Canada')
ErasStadium['City'] = ErasStadium['City'].replace('Gelsenkirchsen', 'Gelsenkirchen')
ErasStadium['Venue'] = ErasStadium['Venue'].replace("'Roger's Centre'", 'Rogers Centre')
ErasStadium['Venue_lower'] = ErasStadium['Venue'].str.lower()

##had to find which files had these values since I did not know so took different approach from earlier
find_value_Am = 'Amsterdamn'
if find_value_Am in ErasStadium['City'].values:
    ErasStadium.replace(find_value_Am, 'Amsterdam', inplace = True)
else:
    print(f'{find_value_Am} was not found')

England_Cities = ['Liverpool', 'London']
ErasStadium.loc[ErasStadium['City'].isin(England_Cities), 'Country'] = 'England'
ErasStadium.loc[ErasStadium['City'] == 'Edinburg', 'Country'] = 'Scotland'
ErasStadium.loc[ErasStadium['City'] == 'Cardiff', 'Country'] = 'Wales'

ErasTourPre = pd.read_csv('ErasTour.csv')
ErasTourPre['Venue_lower'] = ErasTourPre['Venue'].str.lower()
ErasStadium['City'] = ErasStadium['City'].replace('Paradise', 'Las Vegas')

ErasTour = pd.merge(ErasTourPre, ErasStadium[['Venue_lower', 'City', 'Country', 'Latitude', 'Longitude']]
                  , on = ['Venue_lower', 'City', 'Country']
                  , how = 'left'
)

ErasTour.drop('Venue_lower', axis = 1, inplace = True)
ErasTour.to_csv('ErasTour_Post.csv', index = False, encoding = 'utf-8')
print(ErasTour)





#Album_Tours.to_csv("ToursPerAlbum.csv", index = False, encoding = 'utf-8')
