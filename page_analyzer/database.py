import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def execute_query(query, data=None, commit=False, fetchall=False):
    """
    Execute a SQL query on the database.

    Args:
        query (str): The SQL query to be executed.
        data (tuple): The data to be passed to the query.
        commit (bool): If True, commit the changes to the database.
        fetchall (bool): If True, fetch all rows; if False, fetch one row.

    Returns:
        result: The result of the query execution.
    """
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, data)

            if commit:
                connection.commit()
                return

            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()

        return result


def get_urls_by_name(name):
    """
    Retrieve information about a URL by its name.

    Args:
        name (str): The name of the URL.

    Returns:
        result: Information about the URL.
    """
    query = 'SELECT * FROM urls WHERE name=(%s)'
    return execute_query(query, [name])


def get_urls_by_id(id):
    """
    Retrieve information about a URL by its ID.

    Args:
        id (int): The ID of the URL.

    Returns:
        result: Information about the URL.
    """
    query = 'SELECT * FROM urls WHERE id=(%s)'
    return execute_query(query, [id])


def get_checks_by_id(id):
    """
    Retrieve checks associated with a URL by its ID.

    Args:
        id (int): The ID of the URL.

    Returns:
        result: List of checks associated with the URL.
    """
    query = 'SELECT * FROM url_checks WHERE url_id=(%s) ORDER BY id DESC'
    return execute_query(query, [id], fetchall=True)


def get_urls_all():
    """
    Retrieve information about all URLs with the latest check information.

    Returns:
        result: List of URLs with the latest check information.
    """
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


def add_site(name):
    """
    Add a new website to the database.

    Args:
        name (dict): The dictionary containing the URL and creation timestamp.
    """
    query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    data = (name['url'], name['created_at'])
    execute_query(query, data, commit=True)


def add_check(check):
    """
    Add a new check result to the database.

    Args:
        check (dict): The dictionary containing check information.
    """
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
