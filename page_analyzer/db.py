import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

connection = psycopg2.connect(DATABASE_URL)


def get_urls_by_name(name):
    with connection.cursor() as cur:
        select_by_name = '''SELECT *
                    FROM urls
                    WHERE name=(%s)'''
        cur.execute(select_by_name, [name])
        urls = cur.fetchone()
    connection.close()

    return urls
