import validators
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from page_analyzer.constants import *
from page_analyzer.database import get_urls_by_name


def validate_url(url):
    """
    Validate a URL for various criteria.

        Args:
            url (str): The URL to be validated.

        Returns:
            dict: A dictionary containing the validated URL and
             any potential error.
    """

    error = None

    if len(url) == 0:
        error = URL_NOT_FOUND
    elif len(url) > 255:
        error = URL_TOO_LONG
    elif not validators.url(url):
        error = URL_INVALID
    else:
        parsed_url = urlparse(url)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        found = get_urls_by_name(norm_url)

        if found:
            error = URL_EXISTS

        url = norm_url

    valid = {'url': url, 'error': error}

    return valid


def get_url_data(url):
    """
    Retrieve data from a URL, including the HTTP status code, h1 tag, title tag,
    and meta description tag.

        Args:
            url (str): The URL to retrieve data from.

        Returns:
            dict: A dictionary containing data retrieved from the URL.
    """
    r = requests.get(url)

    if r.status_code != 200:
        raise requests.RequestException

    check = {'status_code': r.status_code}

    soup = BeautifulSoup(r.text, 'html.parser')

    h1_tag = soup.find('h1')
    title_tag = soup.find('title')
    description_tag = soup.find('meta', attrs={'name': 'description'})

    check['h1'] = h1_tag.text.strip() if h1_tag else ''
    check['title'] = title_tag.text.strip() if title_tag else ''
    check['description'] = description_tag['content'].strip() \
        if description_tag else ''

    return check
