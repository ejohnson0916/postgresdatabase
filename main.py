import psycopg2
from sqlalchemy import (Table, Column, String,
                        Integer, Boolean, Date, MetaData)
import sqlalchemy
import pandas as pd
import requests
import json
# Be sure to import datetime in this order and format
from datetime import datetime
import datetime
import sqlite3
from sqlalchemy import create_engine

# not sure why I need database location at the moment might change to my postgres database
DATABASE_LOCATION = "postgresql+psycopg2://"
# sqlalchemy formula dialect+driver://username:password@host:port/database
# Spotify username
USER_NAME = "1269375672"
# token from https://developer.spotify.com/console/get-recently-played/?limit=50&after=1484811043509&before=
TOKEN = 'BQBWFxdDFo1RVhuCA9xTNpFZR3-S4JRQXJsrzkPZHHEqO7W8X3YTNSIPhfEmMYOfz8fXJ7waoDfgpV-FNnWH0wyrybBfzipid-jQQMIgebblN8shhb3z4gPg2mil_p6qpX_xlS9tcHJc9PqefQA_n_GlJnAE3fA'

# Function to validate data. This is the "L" (Load) part of ETL
# Loading is not importing or exporting data its validation.

# docstring that says the input of this function should be a dataframe
def check_if_valid_data(
        df: pd.DataFrame) -> bool:  # -> adds docstring that says the function should return a boolean value.

    # Check if dataframe is empty
    if df.empty:
        print("The dataframe is empty! Likely no songs downloaded")
        return False

    # Primary Key: Played_at
    # Primary key constraint, all primary keys must be different.
    # If violated duplicates
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception('Primary key constraint violated')

    # Check for NULL values
    # NULL values are objects that cant be used in mathematical computation
    # Whereas NAs are floats that can be used in computation
    if df.isnull().values.any():
        Exception("NULL Values")

    # In this case we only want data from the last 24 hours
    # Ensure data is not older than 24 hours

    # Subtract one day from now to get 24 hours ago datetime
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

    # Remove hour/min/seconds
    yesterday = yesterday.replace(hour=0, minute=0, microsecond=0)

    # Convert the timestamp column of df to string then back to list
    timestamps = df['timestamp'].astype(str).tolist()

    # This is a string
    type(timestamps[0])

    # For each timestamp in the list
    for timestamp in timestamps:
        # Parse each string timestamp as a date time in this format. If it is less than 'yesterday' value raise the
        # Exception
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') < yesterday:
            print(timestamp)
            raise Exception("Songs being imported are older than set date")
    return True


# Authorization is where the token goes, Not sure what Accept and Content Type args do
header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {token}'.format(token=TOKEN)
}

# Get today's date and time
today_ = datetime.datetime.now()

# We want what I listened to yesterday so subtract the date/time right now by one day to get past 24hrs
yesterday_ = today_ - datetime.timedelta(days=1)

# Convert to unix format because that is what the Spotify API is in Unixtimne - number of seconds since epoch  ( 1
# Jan 1970 ), Javascript "Data" object expects the number of milliseconds since the epoch, Hence multiply by 1000
yesterday_unix_timestamp = int(yesterday_.timestamp()) * 1000

r = requests.get(
    'https://api.spotify.com/v1/me/player/recently-played?after{time}'.format(time=yesterday_unix_timestamp),
    headers=header)
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

    # Code not right. Need to convert to datetime before we enter it into the dataframe
    played_at_list.append(song['played_at'])
    timestamps.append(song['played_at'][0:10])

# Converting the time lists into datetime format before entering into dictionary
# timestamps = [time.replace('-', '') for time in timestamps] list comprehension, kind of like mutate in dplyr
timestamps = pd.to_datetime(timestamps)
played_at_list = pd.to_datetime(played_at_list)

# Turn the lists into a dictionary
song_dict = {
    'song_name': song_names,
    'artist_name': artist_names,
    'timestamp': timestamps,
    'played_at': played_at_list
}

# Put it all into a dataframe
song_df = pd.DataFrame(song_dict)

# Validate
if check_if_valid_data(song_df):
    print("Data valid, proceed to load stage")

# Connect Python to AWS Postgres database

database = ''
username = ''
password = ''
host = 'eanj.cnsiydz9iplc.us-east-2.rds.amazonaws.com'
port = '5432'

# Formula dialect_driver://<username>{0}:<password>{1}@<host>:<port>/database
engine = sqlalchemy.create_engine('postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(username, password, host, port, database))
connection = engine.connect()

metadata = MetaData()
spotify = Table('spotify', metadata,
                Column('song_name', String(255)),
                Column('artist_name', String(255)),
                Column('timestamp', Date()),
                Column('played_at', String(255), primary_key=True, unique=True))

metadata.create_all(engine)

# Insert Data into Database!
song_df.to_sql(name='spotify', con=connection, if_exists='replace')
