## Author: Karina Masih-Hudson
## Date: September 22, 2025
## Comment: Could not find this data so created data frames to capture necessary information
## https://en.wikipedia.org/wiki/List_of_Taylor_Swift_live_performances
## https://en.wikipedia.org/wiki/The_Eras_Tour
## https://screenrant.com/taylor-swift-album-order/

import pandas as pd
from IPython.display import display
from datetime import datetime

TourInfo = pd.DataFrame({'Tour_ID': [1, 2, 3, 4, 5, 6, 7]
    , 'Tour_Name': ['Fearless Tour', 'Speak Now World Tour', 'The Red Tour', 'The 1989 World Tour', 'Reputation Stadium Tour'
                    , 'The Eras Tour - Pre The Tortured Poets Department', 'The Eras Tour - Post The Tortured Poets Department']
    , 'Revenue' : ['66839126.00', '123678576.00', '150184971.00', '250733097.00', '345675146.00', '1039263762.00', '1038354960.00']
    , 'Tour_StartDate': ['2009-04-23', '2011-02-09', '2013-03-13', '2015-05-05', '2018-05-08', '2023-03-17', '2024-05-09']
    , 'Tour_EndDate': ['2010-07-10', '2012-03-18', '2014-06-12', '2015-12-12', '2018-11-21', '2024-03-09', '2024-12-08']
})

TourInfo['Tour_StartDate'] = pd.to_datetime(TourInfo['Tour_StartDate'], errors = 'coerce')
TourInfo['Tour_EndDate'] = pd.to_datetime(TourInfo['Tour_EndDate'], errors = 'coerce')

AlbumInfo = pd.DataFrame({'Album_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    , 'Album_Name': ['Taylor Swift'
                    , 'Fearless'
                    , 'Speak Now'
                    , 'Red'
                    , '1989'
                    , 'Reputation'
                    , 'Lover'
                    , 'folklore', 'evermore'
                    , 'Midnights'
                    , 'The Tortured Poets Department'
                    , 'The Life of a Showgirl']

    , 'Album_ReleaseDate': ['2006-10-24'
                            , '2008-11-11'
                            , '2010-10-25'
                            , '2012-10-22'
                            , '2014-10-27'
                            , '2017-11-10'
                            , '2019-08-23'
                            , '2020-07-24', '2020-12-11'
                            , '2022-10-21'
                            , '2024-04-19'
                            , '2025-10-03']
    , 'Tour_ID': [0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 7, -1]
 })

AlbumInfo['Album_ReleaseDate'] = pd.to_datetime(AlbumInfo['Album_ReleaseDate'], errors = 'coerce')
 
# display(TourInfo)
# display(AlbumInfo)

Album_Tours = pd.merge(AlbumInfo, TourInfo, on='Tour_ID', how='left')
Album_Tours['DateDiff_AlbumRel_TourStart'] = (Album_Tours['Tour_StartDate'] - Album_Tours['Album_ReleaseDate']).dt.days


Album_Tours.to_csv("ToursPerAlbum.csv", index = False, encoding = 'utf-8')
print(Album_Tours)

