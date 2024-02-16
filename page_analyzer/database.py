import os
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_all_urls() -> dict:
    """
    Query the database for all added URLs. Return only the last check info.

    Tables: urls, url_checks
    :return: Dict of all urls, its id's, last check dates and status codes.
    """

    conn = connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT DISTINCT ON (urls.id)
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
        cur.execute(q_select)
        urls = cur.fetchall()
    conn.close()

    return urls


def get_urls_by_id(id_: int) -> dict:
    """
    Query the database for one URL data based on its id.

    Tables: urls
    :param id_: URL id.
    :return: Dict containing one url data: id, name, creation date.
    """

    conn = connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
                    FROM urls
                    WHERE id=(%s)'''
        cur.execute(q_select, [id_])
        urls = cur.fetchone()
    conn.close()

    return urls


def get_urls_by_name(name: str) -> dict:
    """
    Query the database for one URL data based on its name.

    Tables: urls
    :param name: URL name.
    :return: Dict containing one url data: id, name, creation date.
    """

    conn = connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
                    FROM urls
                    WHERE name=(%s)'''
        cur.execute(q_select, [name])
        urls = cur.fetchone()
    conn.close()

    return urls


def get_checks_by_id(id_: int) -> dict:
    """
    Query the database for all URL checks.

    Tables: url_checks
    :param id_: URL id.
    :return: Dict containing checks info: id, status code, h1, title,
    description, check date.
    """

    conn = connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q_select = '''SELECT *
                    FROM url_checks
                    WHERE url_id=(%s)
                    ORDER BY id DESC'''
        cur.execute(q_select, [id_])
        checks = cur.fetchall()
    conn.close()

    return checks


def add_site(site: dict) -> None:
    """
    Insert into database new URL.

    Tables: urls
    :param site: Dict containing URL and its creation date.
    """

    conn = connect(DATABASE_URL)
    with conn.cursor() as cur:
        q_insert = '''INSERT
                    INTO urls (name, created_at)
                    VALUES (%s, %s)'''
        cur.execute(q_insert, (
            site['url'],
            site['created_at']
        ))
        conn.commit()
    conn.close()


def add_check(check: dict) -> None:
    """
    Insert into database new check data.

    Tables: url_checks
    :param check: Dict containing url check data: URL id, check status code, h1,
    title, description, check date
    """

    conn = connect(DATABASE_URL)
    with conn.cursor() as cur:
        q_insert = '''INSERT
                    INTO url_checks(
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)'''
        cur.execute(q_insert, (
            check['url_id'],
            check['status_code'],
            check['h1'],
            check['title'],
            check['description'],
            check['checked_at']
        ))
        conn.commit()
    conn.close()
