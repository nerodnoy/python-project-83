import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_urls_by_name(name):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        select = '''SELECT *
                    FROM urls
                    WHERE name=(%s)'''
        cur.execute(select, [name])
        urls = cur.fetchone()
    connection.close()

    return urls


def get_urls_by_id(id):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        select_by_id = '''SELECT *
                    FROM urls
                    WHERE id=(%s)'''
        cur.execute(select_by_id, [id])
        urls = cur.fetchone()
    connection.close()

    return urls


def get_urls_all():
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
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


def get_checks_by_id(id):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        select = '''SELECT *
                    FROM url_checks
                    WHERE url_id=(%s)
                    ORDER BY id DESC'''
        cur.execute(select, [id])
        checks = cur.fetchall()
    connection.close()

    return checks


def add_website(name):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as cur:
        insert = '''INSERT
                    INTO urls (name, created_at)
                    VALUES (%s, %s)'''
        data = (
            name['url'],
            name['created_at']
        )
        cur.execute(insert, data)
        connection.commit()
    connection.close()


def add_check(check):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as cur:
        insert = '''INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)'''
        data = (
            check['url_id'],
            check['status_code'],
            check['h1'],
            check['title'],
            check['description'],
            check['checked_at']
        )
        cur.execute(insert, data)
        connection.commit()
    connection.close()
