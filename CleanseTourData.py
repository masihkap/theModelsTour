import pandas as pd

def clean_string(df):
    return df.apply(
        lambda col: col.astype(str).str.replace(r'\[.*?\]', '', regex=True).str.strip()
        if col.dtype == 'object' else col
    )

def attendance_split(df):
    if 'Attendance' in df.columns:
        df['Attendance'] = df['Attendance'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
        split_cols = df['Attendance'].str.split('/', n=1, expand=True)
        df['Attendance'] = (
            split_cols[0]
            .str.replace(',', '', regex=False)
            .replace('—', '')
            .str.strip()
        )
        df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
        
        df['Venue Capacity'] = (
            split_cols[1]
            .str.replace(',', '', regex=False)
            .replace('—', '')
            .str.strip()
        )
        df['Venue Capacity'] = pd.to_numeric(df['Venue Capacity'], errors='coerce')
    return df


##Fearless
FearlessTour = pd.read_csv('tour-fearless.csv')

FearlessTour['Date'] = pd.to_datetime(FearlessTour['Date'], format='%B %d, %Y', errors='coerce')
FearlessTour = attendance_split(FearlessTour)
FearlessTour['Tour_ID'] = 1
FearlessTour = clean_string(FearlessTour)

FearlessTour.to_csv('FearlessTour.csv', index = False, encoding = 'utf-8')


##Speak Now
SpeakNow1 = pd.read_csv('tour-speak I.csv')
SpeakNow2 = pd.read_csv('tour-speak II.csv')
SpeakNow3 = pd.read_csv('tour-speak III.csv')
SpeakNow4 = pd.read_csv('tour-speak IV.csv')

#2011 dates I-III
SpeakNowTour2011 = pd.concat([SpeakNow1, SpeakNow2, SpeakNow3], axis = 0)
SpeakNowTour2011['Date (2011)'] = SpeakNowTour2011['Date (2011)'] + ', 2011'
SpeakNowTour2011 = SpeakNowTour2011.rename(columns = {'Date (2011)' : 'Date'})

#2012 dates IV
SpeakNow4['Date (2012)'] = SpeakNow4['Date (2012)'] + ', 2012'
SpeakNow4 = SpeakNow4.rename(columns = {'Date (2012)' : 'Date'})

#combine and cleanse
SpeakNowTour = pd.concat([SpeakNowTour2011, SpeakNow4], axis = 0)
SpeakNowTour['Date'] = pd.to_datetime(SpeakNowTour['Date'], format = '%B %d, %Y', errors = 'coerce')
SpeakNowTour = attendance_split(SpeakNowTour)
SpeakNowTour['Tour_ID'] = 2
SpeakNowTour = clean_string(SpeakNowTour)

SpeakNowTour.to_csv('SpeakNowTour.csv', index = False, encoding = 'utf-8')

##Red
Red1 = pd.read_csv('tour-red I.csv')
Red2 = pd.read_csv('tour-red II.csv')
Red3 = pd.read_csv('tour-red III.csv')
Red4 = pd.read_csv('tour-red IV.csv')

#2013 dates II-II
RedTour2013 = pd.concat([Red1, Red2], axis = 0)
RedTour2013['Date (2013)'] = RedTour2013['Date (2013)'] + ', 2013'
RedTour2013 = RedTour2013.rename(columns = {'Date (2013)' : 'Date'})


#2014 dates III-IV
RedTour2014 = pd.concat([Red3, Red4])
RedTour2014['Date (2014)'] = RedTour2014['Date (2014)'] + ', 2014'
RedTour2014 = RedTour2014.rename(columns = {'Date (2014)' : 'Date'})

#Combine and cleanse
RedTour = pd.concat([RedTour2013, RedTour2014], axis = 0)
RedTour['Date'] = pd.to_datetime(RedTour['Date'], format = '%B %d, %Y', errors = 'coerce')
RedTour = attendance_split(RedTour)
RedTour['Tour_ID'] = 3
RedTour = clean_string(RedTour)

RedTour.to_csv('RedTour.csv', index = False, encoding = 'utf-8')

##1989
Tour1989 = pd.read_csv('tour-1989.csv')
Tour1989['Date (2015)'] = Tour1989['Date (2015)'] + ', 2015'
Tour1989 = Tour1989.rename(columns = {'Date (2015)' : 'Date'})

#cleanse
Tour1989['Date'] = pd.to_datetime(Tour1989['Date'], format = '%B %d, %Y', errors = 'coerce')
Tour1989 = attendance_split(Tour1989)
Tour1989['Tour_ID'] = 4
Tour1989 = clean_string(Tour1989)

Tour1989.to_csv('1989Tour.csv', index = False, encoding = 'utf-8')


##Reputation
ReputationTour = pd.read_csv('tour-rep.csv')
ReputationTour['Date (2018)'] = ReputationTour['Date (2018)'] + ', 2018'
ReputationTour = ReputationTour.rename(columns = {'Date (2018)' : 'Date'})

#cleanse
ReputationTour['Date'] = pd.to_datetime(ReputationTour['Date'], format = '%B %d, %Y', errors = 'coerce')
ReputationTour = attendance_split(ReputationTour)
ReputationTour['Tour_ID'] = 5
ReputationTour = clean_string(ReputationTour)

ReputationTour.to_csv('ReputationTour.csv', index = False, encoding = 'utf-8')

