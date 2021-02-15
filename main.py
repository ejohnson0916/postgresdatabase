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
TOKEN = 'BQA7oKCjvN4210f7uxWVXeE9ZSj4if_F-GevFBdaPVtx_xX_Vquenx6PRovQasn_AfjWyayvsPh7tCO54PqYpfoJpgL_sZ7F_rcq9fwPkWPRC-4dSHLmdTHSqWJwUIV9zqorYlYOnBjp-CFVdUDv'

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

# Convert to unix format because that is what the Spotify API is in

print(yesterday)




#r = requests.get('https://api.spotify.com/v1/me/player/recently-played', headers=header)

#print(r.json())

