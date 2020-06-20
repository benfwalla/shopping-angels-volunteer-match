import os
import json
import gspread
import pandas as pd
import geopy.distance
from tabulate import tabulate


def miles_between(row, client_lat, client_long):
    '''
    A helper function thagt finds the miles between a volunteer's coordinates and a client's coordinates
    :param row: a row in the pd.Dataframe in find_nearest_volunteers()
    :param client_lat: an Integer of a Latitude point
    :param client_long: an Integer of a Longitude point
    :return: the distance between the two points in miles
    '''

    volunteer_coords = (row['Latitude'], row['Longitude'])
    client_coords = (client_lat, client_long)
    return round(geopy.distance.VincentyDistance(volunteer_coords, client_coords).miles, 2)


def find_nearest_volunteers(lat_long, state, key, gc, tablefmt):
    '''
    Returns a list of the nearest volunteers in the state to the given client's coordinates
    :param lat_long: the client's coordinates (i.e. '40.23893, -80.32871')
    :param state: the client's state (i.e. 'Pennsylvania')
    :param key: the key to the Google Sheet of all Volunteers
    :param gc: an instance of the the gspread python library
    :param tablefmt: (Optional) a String of the supported table format type for a pretty text output (https://github.com/astanin/python-tabulate#table-format)
    Do not write in anything for JSON output
    :return: a Dictionary of the the 10 nearest volunteers, including their names, emails, and miles from client
    '''

    # Get volunteer mastersheet from Google Sheets
    sh = gc.open_by_key(key)
    ws = sh.worksheet('MasterVolunteer')
    ws_vals = ws.get_all_values()

    # Filter only volunteers in same state as client
    df = pd.DataFrame(data=ws_vals[1:], columns=ws_vals[0])
    df = df[df['What is your state?'] == state]
    df['Latitude'] = df['Latitude/Longitude'].str.split(', ').str[0]
    df['Longitude'] = df['Latitude/Longitude'].str.split(', ').str[1]

    # Client Coordinates
    client_lat = lat_long.split(", ")[0]
    client_long = lat_long.split(", ")[1]

    # Calculate miles between volunteers and client
    df['Miles from Client'] = df.apply(miles_between, axis=1, args=(client_lat, client_long))

    # Get 10 closest volunteers
    df['Name'] = df['What is your first name?'].astype(str) + ' ' + df['What is your last name?'].astype(str)
    df.rename(columns={'What is your e-mail address?': 'E-mail'}, inplace=True)
    df = df[['Name', 'E-mail', 'Miles from Client']]
    df = df.drop_duplicates()
    df = df.sort_values(by=['Miles from Client'], ascending=True).head(10)

    # Export important fields to dictionary
    volunteer_dict = df.to_dict('records')

    if tablefmt:
        return tabulate(volunteer_dict, headers="keys", tablefmt=tablefmt)
    else:
        return volunteer_dict
