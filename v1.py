# This script will serve to make and test "Morti"

# Importing requirements
from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import json

# Function to load Google Project Key from file
# File is called '.gKey' and located in home directory
def getKey(file = '.gKey'):
    keyPath = Path.home() / file
    openKey = keyPath.open()
    val = json.load(openKey)['key']
    return(val)

# Function to get Location (uses system's IP address)
# This can be inaccurate networks that use NATs
def getLoc():

    url = 'http://ip-api.com/json'
    page = urlopen(url)
    html = page.read()

    loc = json.loads(html)
    return(loc)


# Function accepts a string of location
def getLatLng(loc = None, url = 'https://maps.google.com/maps/api/geocode/json?address='):

    # If Loc is None get LatLong of current location
    if loc is None:
        loc = getLoc()
        lat = loc['lat']
        lng = loc['lon']

    else:
        # Replace any spaces in the location name with '%20'
        loc  = loc.replace(" ","%20")
        key = getKey()
        pageURL = f'{url}{loc}&key={key}'

        # Open the URL
        page = urlopen(pageURL)
        html = page.read()

        # Read page as json
        latlng = json.loads(html)

        # If page is empty (Reached google api limit) return empty list.
        if latlng['results'] == []:
            return(None)
        lat = latlng['results'][0]['geometry']['location']['lat']
        lng = latlng['results'][0]['geometry']['location']['lng']

    return {'lat': lat, 'lng': lng}

# Scraping DarkSky for weather info.
# Function accepts a string in the form of 'lat,lng'
def getDarkSky(loc = None, unit = 'ca12', url='https://darksky.net/forecast/'):

    '''For units:
        'ca12' = Celsius and km/h
        'si12' = Celsius and m/s
        'us12' = Farenheit and mi/h
        'uk212' = Celsius and mi/h
    '''

    # Use current location if no location is provided
    if loc is None or loc == '':
        print('Using current location from IP Address')
        location = getLoc()
        lat = str(location['lat'])
        lng = str(location['lon'])
    else:
        location = getLatLng(loc)
        if location is None:
            print('No result from Google Geocode')
            return(None)
        lat = str(location['lat'])
        lng = str(location['lng'])

    # Use lat and long in URL
    pageURL = url + lat + ',' + lng + '/' + unit

    # Open page
    page = urlopen(pageURL)
    html = page.read()

    # Soupify
    soup = bs(html.decode(), 'html.parser')

    # Empty weather dict to hold values
    weather = {}

    # Temperature (not temporary)
    temp = soup.find("span", {"class": "summary swap" })
    temp = temp.getText()
    temp = temp.replace('\xa0',' and ')

    weather['Temperature'] = temp

    # Other details
    # This is separate because of the DarkSky page structure
    dets = soup.find("div", {"id": "currentDetails"})
    det = dets.findChild()

    # Every Child of "currentDetails" has a name and value child
    # The name is the weather parameter and the num is the value
    while det is not None:

        namVal = det.text
        if namVal == '':
            det = det.find_next_sibling()
            namVal = det.text
        namVal = namVal.replace("\n","")
        namVal = namVal.split(":")
        weather[namVal[0]] = namVal[1]

        det = det.find_next_sibling()

    return weather

# Function to tell if it is getting dark outside
# Uses UV values as proxy for brightness.
def isDark(loc = None, threshold = 0):
    weather = getDarkSky(loc)
    if weather is None:
        return None
    uv = weather['UV Index']
    uv = int(uv)
    if uv <= threshold:
        print('Yes')
        return {'isDark': True, 'uv': uv}
    else:
        print('No')
        return {'isDark': False, 'uv': uv}