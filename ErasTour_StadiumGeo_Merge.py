import pandas as pd

# Eras sheet has latitude/longitude data from a previous project I did
ErasStadiumCol = ['City', 'State', 'Country', 'Stadium', 'Latitude', 'Longitude']
ErasStadium = pd.read_csv('TaylorSwift_ErasTour_DatesStadiums_Geo.csv', usecols = ErasStadiumCol
                          )
ErasStadium = ErasStadium.drop_duplicates()
ErasStadium = ErasStadium.rename(columns = {'Stadium' : 'Venue'})
ErasStadium['Country'] = ErasStadium['Country'].replace('United States of America', 'United States')
ErasStadium['Country'] = ErasStadium['Country'].replace('Canda', 'Canada')
ErasStadium['City'] = ErasStadium['City'].replace('Gelsenkirchsen', 'Gelsenkirchen')
ErasStadium['Venue'] = ErasStadium['Venue'].replace("'Roger's Centre'", 'Rogers Centre')
ErasStadium['Venue'] = ErasStadium['Venue'].replace("'Caesar's Superdome'", 'Caesars Superdome')
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

#load original file
ErasTourPre = pd.read_csv('ErasTour.csv')
ErasTourPre = ErasTourPre.rename(columns = {'Opening act(s)' : 'Opening acts'})


ErasStadium['City'] = ErasStadium['City'].replace('Las Vegas', 'Paradise')
ErasStadium['City'] = ErasStadium['City'].replace('Los Angeles', 'Inglewood')
ErasStadium['City'] = ErasStadium['City'].replace('Sao Paulo', 'São Paulo')
ErasStadium['City'] = ErasStadium['City'].replace('Lyon', 'Décines-Charpieu')
ErasStadium['City'] = ErasStadium['City'].replace('Miami', 'Miami Gardens')

ErasStadium['Venue'] = ErasStadium['Venue'].replace('Estadio Nilton Santos', 'Estádio Olímpico Nilton Santos')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('MCG', 'Melbourne Cricket Ground')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('National Stadium', 'Singapore National Stadium')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('Paris La Defense Arena', 'Paris La Défense Arena')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('Estadio da Luz', 'Estádio da Luz')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('Estadio Santiago Bernabeu', 'Estadio Santiago Bernabéu')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('BT Murrayfield Stadium', 'Murrayfield Stadium')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('Johan Cruijff Arena', 'Johan Cruyff Arena')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('Stadion Letzigrund Zurich', 'Letzigrund')
ErasStadium['Venue'] = ErasStadium['Venue'].replace('San Siro Stadium', 'San Siro')



ErasTourPre['Venue_lower'] = ErasTourPre['Venue'].str.lower()

ErasTour = pd.merge(ErasTourPre, ErasStadium[['Venue_lower', 'City', 'Country', 'Latitude', 'Longitude']]
                  , on = ['Venue_lower', 'City', 'Country']
                  , how = 'left'
)

ErasTour.drop('Venue_lower', axis = 1, inplace = True)
ErasTour.to_csv('ErasTour_Post.csv', index = False, encoding = 'utf-8')
print(ErasTour)
