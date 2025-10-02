import pandas as pd

# Eras sheet has latitude/longitude data from a previous project I did
ErasStadiumCol = ['City', 'State', 'Country', 'Stadium', 'Latitude', 'Longitude']
ErasStadium = pd.read_csv('TaylorSwift_ErasTour_DatesStadiums_Geo.csv'
                          , usecols = ErasStadiumCol)
ErasStadium = ErasStadium.drop_duplicates()
ErasStadium = ErasStadium.rename(columns = {'Stadium' : 'Venue'})
ErasStadium['Country'] = ErasStadium['Country'].replace('United States of America', 'United States')
#print(ErasStadium.head())

#other tours does not have this information
StadiumColumnsPre = ['City', 'Country', 'Venue']

FearlessStadium = pd.read_csv('FearlessTour.csv', usecols=StadiumColumnsPre)
SpeakNowStadium = pd.read_csv('SpeakNowTour.csv', usecols=StadiumColumnsPre)
RedStadium = pd.read_csv('RedTour.csv', usecols=StadiumColumnsPre)
Stadium1989 = pd.read_csv('1989Tour.csv', usecols=StadiumColumnsPre)
ReputationStadium = pd.read_csv('ReputationTour.csv', usecols=StadiumColumnsPre)

StadiumsCombinedPre1 = pd.concat([FearlessStadium, SpeakNowStadium, RedStadium, Stadium1989, ReputationStadium]
                             , ignore_index = True)
StadiumsPreCount1 = len(StadiumsCombinedPre1)

# remove duplicates
StadiumsCombinedUn = StadiumsCombinedPre1.drop_duplicates()
StadiumsPreCount2 = len(StadiumsCombinedUn)

#add columns so the shape matches Eras
StadiumsCombinedUn['Latitude'] = ''
StadiumsCombinedUn['Longitude'] = ''

StadiumsPreCount3 = len(ErasStadium)

StadiumsCombinedPre2 = pd.concat([ErasStadium, StadiumsCombinedUn], ignore_index = True)
StadiumsPreCount4 = len(StadiumsCombinedPre2)

#print(StadiumsCombinedPre2)
print(StadiumsPreCount1, StadiumsPreCount2, StadiumsPreCount3, StadiumsPreCount4) #= 2 + 3 = 4

StadiumsCombinedPre2.to_csv('StadiumInfo.csv', index = False, encoding = 'utf-8')

