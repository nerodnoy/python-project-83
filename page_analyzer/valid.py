from page_analyzer.const import (
    URL_EXISTS,
    URL_TOO_LONG,
    URL_INVALID,
    URL_EMPTY
)
import validators
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from page_analyzer.db import get_urls_by_name


def validate_url(url):
    error = None

    if len(url) == 0:
        error = URL_EMPTY
    elif len(url) > 255:
        error = URL_TOO_LONG
    elif not validators.url(url):
        error = URL_INVALID
    else:
        parsed_url = urlparse(url)
        valid_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        same_url_found = get_urls_by_name(valid_url)

        if same_url_found:
            error = URL_EXISTS

        url = valid_url

    valid = {'url': url, 'error': error}

    return valid


def get_url_data(url):
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
