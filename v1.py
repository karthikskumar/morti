# This script will serve to make and test "Morti"

# Importing requirements
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import json

# Function accepts a string of location
def getLatLng(loc, url = 'https://maps.google.com/maps/api/geocode/json?address='):

    loc  = loc.replace(" ","%20")
    pageURL = url + loc
    page = urlopen(pageURL)
    html = page.read()

    latlng = json.loads(html)
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

    pageURL = url + lat + ',' + lng + '/' + unit
    page = urlopen(pageURL)
    html = page.read()

    soup = bs(html.decode(), 'html.parser')

    weather = {}

    temp = soup.find("span", {"class": "summary swap" })
    temp = temp.getText()
    temp = temp.replace('\xa0',' and ')

    weather['Temperature'] = temp

    dets = soup.find("div", {"id": "currentDetails"})
    det = dets.findChild()


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


# Function to get Location
def getLoc():

    url = 'http://ip-api.com/json'
    page = urlopen(url)
    html = page.read()

    loc = json.loads(html)
    return(loc)

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