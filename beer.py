'''
Course:        DCS 211 Winter 2021 Module D
Assignment:    Final Project
Topic:         Mapping US Breweries
Purpose:       Use Python libraries and the Open Brewery DB API to find,
               organize, and visualize data on breweries in the United States.

Written by: Kona Lindsey

'''
###############################################################################

# importing libraries
import requests
import json
import pandas as pd
import time
import us
import os
from progress.bar import Bar
import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster
import geopy.geocoders
from geopy.geocoders import Nominatim
geopy.geocoders.options.default_user_agent = "dcs211_klindse2/1"
geopy.geocoders.options.default_timeout = 10

###############################################################################

def getBrews():
    '''
    scrapes and stores data on US breweries using the Open Brewery DB api

    Parameters
    ----------
        None

    Returns
    -------
    beer_dict : dictionary
        a dictionary containing states as keys and companies as values
    '''

    url = 'https://api.openbrewerydb.org/breweries?per_page=50' # store api url for requests
    fname = "beer.json" # store filename to use
    beer_dict = {} # make dictionary for storing brewery data

    if os.path.exists(fname): # conditional for local file use
        with open(fname, "r") as infile: # opening local file for reading
            data = infile.read() # read in local data
        beer_dict = json.loads(data) # storing local data as python dictionary

    else:
        bar = Bar("Finding Breweries: ", max = 50)
        for state in us.STATES: # iterating through US states
            state = str(state) # changing type to string

            inputs = { "by_state" : state } # setting inputs for data request

            response = requests.get(url, params = inputs) # requesting and storing data
            time.sleep(1)

            if not response.ok: # conditional for bad request
                print(response.reason) # print error statemen

            else:
                beer_dict[state] = response.json() # storing brewery values to state keys

            bar.next()
            time.sleep(1)
        bar.finish()

        with open(fname, 'w') as outfile: # opening file for writing
            json.dump(beer_dict, outfile) # dump dictionary json to local file

    return beer_dict # return dictionary of US brewery data

###############################################################################

def write_csv(beer_dict):
    '''
    writes a CSV file containing data on US breweries

    Parameters
    ----------
    beer_dict : dictionary
        a dictionary containing states as keys and companies as values

    Returns
    -------
        None
    '''

    with open('breweries.csv', 'w') as outfile: # opening file for writing
        outfile.write("Brewery,Type,Street Address,City,State,ZIP Code,Phone Number,Website \n") # write to local file

        for state in beer_dict: # iterating through state keys in dictionary
            for brew in beer_dict[state]: # iterating through breweries in each state

                company = brew['name'].replace(",", "") # storing and cleaning brewery name
                type = brew['brewery_type'] # storing brewery type
                address = str(brew['street']) # storing and changing type of brewery address
                if "," in address: # conditional for comma existence
                    address = address.replace("," , "") # storing and cleaning brewery address
                city = brew['city'] # storing brewery city
                state = brew['state'] # storing brewery state
                zip = brew['postal_code'] # storing brewery zip code
                phone = brew['phone'] # storing brewery phone number
                url = brew['website_url'] # storing brewery website

                outfile.write(f"{company},{type},{address},{city},{state},{zip},{phone},{url} \n") # write brewery info to local csv file

###############################################################################

def plot_map(beer_dict):
    '''
    plots a map of US breweries with clickable markers

    Parameters
    ----------
    beer_dict : dictionary
        a dictionary containing states as keys and companies as values

    Returns
    -------
        None
    '''

    map = folium.Map(location = [44.1057,-70.2022], titles = 'cartodbpositron', zoom_start = 5) # setting map parameters
    mc = MarkerCluster() # calling and storing marker cluster function

    bar = Bar("Mapping Breweries: ", max = 50)
    for state in beer_dict: # iterating through state keys in dictionary
        for brew in beer_dict[state]: # iterating through breweries in each state
            latitude = brew['latitude'] # storing brewery latitude
            longitude = brew['longitude'] # storing brewery longitude
            address = str(brew["street"]) # storing and changing type of brewery address
            state = brew['state'] # storing brewery state
            place = f'{address},{state}' # storing place for geolocator use

            if latitude and longitude != None: # conditional for coordinates type
                mc.add_child(Marker([latitude, longitude], popup = f"{brew['name']}: {brew['city']}, {state} {brew['website_url']} ph: {brew['phone']}")) # storing brewery info to map marker
                map.add_child(mc)

            elif address != 'None': # conditional for address type
                geolocator = Nominatim(user_agent = "google_maps") # storing geolocator using Nominatim
                location = geolocator.geocode(place) # storing location found using geolocator
                location1 = str(location) # storing type change of location

                if location1 != "None": # conditional for location type
                    latitude = location.latitude # storing geolocator latitude
                    longitude = location.longitude # storing geolocator longitude

                    mc.add_child(Marker([latitude, longitude], popup = f"{brew['name']}: {brew['city']}, {state} {brew['website_url']} ph: {brew['phone']}")) # storing brewery info to map marker
                    map.add_child(mc) # adding cluster to map

        bar.next()
        time.sleep(1)
    bar.finish()

    map.save("map.html") # save interactive map as a file

###############################################################################

def main():

    write_csv(getBrews())
    plot_map(getBrews())

###############################################################################

if __name__ == "__main__":

    main()
    print("main")
