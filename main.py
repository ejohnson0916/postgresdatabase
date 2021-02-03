import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="eandb",
    user="postgres",
    password="postgres"
)

