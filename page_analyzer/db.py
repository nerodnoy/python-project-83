import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def execute_query(query, data=None, fetchall=False, commit=False):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, data)
            if commit:
                connection.commit()
                return  # Если есть commit, завершаем выполнение функции

            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()

        return result


def get_urls_by_name(name):
    query = 'SELECT * FROM urls WHERE name = %s'
    return execute_query(query, [name])


def get_urls_by_id(id):
    query = 'SELECT * FROM urls WHERE id = %s'
    return execute_query(query, [id])


def get_checks_by_id(id):
    query = 'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC'
    return execute_query(query, [id])


def get_urls_all():
    query = '''
        SELECT DISTINCT ON (urls.id)
            urls.id AS id,
            urls.name AS name,
            url_checks.created_at AS last_check,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
            AND url_checks.id = (
                SELECT MAX(id)
                FROM url_checks
                WHERE url_id = urls.id
            )
        ORDER BY urls.id DESC;
    '''
    return execute_query(query, fetchall=True)


def add_website(name):
    query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    data = (name['url'], name['created_at'])
    execute_query(query, data, commit=True)


def add_check(check):
    query = '''
        INSERT INTO url_checks (
            url_id,
            status_code,
            h1,
            title,
            description,
            created_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
    '''
    data = (
        check['url_id'],
        check['status_code'],
        check['h1'],
        check['title'],
        check['description'],
        check['checked_at']
    )
    execute_query(query, data, commit=True)
