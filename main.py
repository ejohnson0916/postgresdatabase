import psycopg2
import sqlalchemy
import pandas as pd
import requests
import json
# Be sure to import datetime in this order and format
from datetime import datetime
import datetime
import sqlite3
import spotify_token as st

# not sure why I need database location at the moment might change to my postgres database
DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
#Spotify username
USER_NAME = "1269375672"
# token from https://developer.spotify.com/console/get-recently-played/?limit=50&after=1484811043509&before=
TOKEN = 'BQDYx2Z5Zl-nq3_9f__BUE_hLmN0JP20AAJTkQY2jOkvEBickykggNiVJAjlQVObcDOI1YAtPS8OLyvSD7-TaP7ITMiXZSPIZuYcBBuJGbL5SEldj0xbsIhSGghXXT1lWwUzu7mKjHuYN9srKzxk'

# Authorization is where the token goes, Not sure what Accept and Content Type args do
header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {token}'.format(token=TOKEN)
}

# Get today's date and time
today = datetime.datetime.now()

# We want what I listened to yesterday so subtract the date/time right now by one day to get past 24hrs
yesterday = today - datetime.timedelta(days=1)

# Convert to unix format because that is what the Spotify API is in Unixtimne - number of seconds since epoch  ( 1
# Jan 1970 ), Javascript "Data" object expects the number of milliseconds since the epoch, Hence multiply by 1000
yesterday_unix_timestamp = int(yesterday.timestamp())

r = requests.get('https://api.spotify.com/v1/me/player/recently-played?after{time}'.format(time=yesterday_unix_timestamp), headers=header)
data = r.json()

# Lists that will be merged for a dataframe
song_names = []
artist_names = []
played_at_list = []
timestamps = []

# I think this is basically looping through this object
# Remember this syntax. I think that this is possible on all JSON objects.
for song in data["items"]:
    song_names.append(song['track']['name'])
    artist_names.append(song['track']['album']['artists'][0]['name'])
    played_at_list.append(song['played_at'])
    timestamps.append(song['played_at'][0:10])

print(played_at_list)
# Turn the lists into a dictionary

song_dict = {
    'song_name': song_names,
    'artist_name': artist_names,
    'played_at': played_at_list,
    'time_stamps': timestamps
}

print(song_dict['played_at'])


# Put it all into a dataframe
song_df = pd.DataFrame(data=song_dict, columns=['song_name', 'artist_name', 'exact_play_time', 'date_played'])

#print(song_df.head())

