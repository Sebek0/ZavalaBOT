import os

from dotenv import load_dotenv

load_dotenv()
username = os.getenv('POSTGRESQL_USERNAME')
password = os.getenv('POSTGRESQL_PASSWORD')
ip_address = os.getenv('POSTGRESQL_HOST')
port = os.getenv('POSTGRESQL_PORT')
db_name = os.getenv('POSTGRESQL_DB_NAME')


def create_database_uri() -> str:
    # SCHEME: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DB_NAME>"
    
    DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}' \
        .format(username, password, ip_address, port, db_name)
    
    return DATABASE_URI