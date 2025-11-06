#https://medium.com/bitgrit-data-science-publication/get-continent-names-from-coordinates-using-python-8560cdcfdfbb#:~:text=Load%20libraries%20*%20geopy%20%E2%80%94%20A%20Python,*%20tqdm%20%E2%80%94%20progress%20bar%20for%20Python.
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pycountry_convert as pc

from pprint import pprint
from typing import Tuple
from tqdm import tqdm

tqdm.pandas()

StadiumLocation = pd.read_csv('StadiumList.csv')
TestLocation = StadiumLocation[['Latitude', 'Longitude']].values[0]
print(TestLocation)

locator = Nominatim(user_agent = 'GetCountryInfo', timeout = 10)
location = locator.reverse('33.527283, -112.263275', language = 'en')
print(location)

continent = pc.country_alpha2_to_continent_code('US')
print(continent)

def get_continent_name(continent_code: str) -> str:
    continent_dict = {
        "NA": "North America",
        "SA": "South America",
        "AS": "Asia",
        "AF": "Africa",
        "OC": "Oceania",
        "EU": "Europe",
        "AQ" : "Antarctica"
    }
    return continent_dict[continent_code]

get_continent_name("EU")
