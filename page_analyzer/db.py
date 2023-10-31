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


def get_all_urls():
    with connection.cursor() as cur:
        select_all = '''SELECT DISTINCT ON (urls.id)
                        urls.id AS id,
                        urls.name AS name,
                        url_checks.created_at AS last_check,
                        url_checks.status_code AS status_code
                    FROM urls
                    LEFT JOIN url_checks ON urls.id = url_checks.url_id
                    AND url_checks.id = (SELECT MAX(id)
                                        FROM url_checks
                                        WHERE url_id = urls.id)
                    ORDER BY urls.id DESC;'''
        cur.execute(select_all)
        urls = cur.fetchall()
    connection.close()

    return urls


def add_website(name):
    with connection.cursor() as cur:
        insert_new_website = '''INSERT
                    INTO urls (name, created_at)
                    VALUES (%s, %s)'''
        cur.execute(insert_new_website, (
            name['url'],
            name['created_at']
        ))
        connection.commit()
    connection.close()