from urllib.parse import urlparse
from page_analyzer.db import get_urls_by_name
import validators


def validate_url(url):
    error = None

    if len(url) == 0:
        error = 'URL length cannot be zero'
    elif len(url) > 255:
        error = 'URL length should be shorter than 255 characters'
    elif not validators.url(url):
        error = 'Invalid URL name'
    else:
        parsed_url = urlparse(url)
        valid_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        same_url_found = get_urls_by_name(valid_url)

        if same_url_found:
            error = 'This URL already exists'

        url = valid_url

    valid = {'url': url, 'error': error}

    return valid