# from flask import (
#     render_template,
#     flash,
#     get_flashed_messages,
#     url_for,
#     redirect
# )
# from page_analyzer.database import (
#     get_urls_by_name,
#     add_website,
# )
# from page_analyzer.constants import (
#     URL_EXISTS,
#     URL_TOO_LONG,
#     URL_INVALID,
#     URL_EMPTY
# )
from datetime import datetime


def format_timestamp():
    """
    Format the current timestamp as a string.

        Returns:
            str: Formatted timestamp string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# def handle_error(error, url):
#     """
#     Handle errors during URL validation and processing.
#
#         Args:
#             error (str): The error code indicating the type of error.
#             url (str): The URL causing the error.
#
#         Returns:
#             tuple: Tuple containing rendered HTML template,
#              HTTP status code (422).
#         """
#     if error == URL_EXISTS:
#         id = get_urls_by_name(url)['id']
#         flash('Страница уже существует', 'alert-info')
#         return redirect(url_for('url_by_id', id=id))
#
#     elif error == URL_EMPTY:
#         flash('URL обязателен', 'alert-danger')
#
#     elif error == URL_INVALID:
#         flash('Некорректный URL', 'alert-danger')
#
#     elif error == URL_TOO_LONG:
#         flash('URL превышает 255 символов', 'alert-danger')
#
#     messages = get_flashed_messages(with_categories=True)
#
#     return render_template('index.html', url=url, messages=messages), 422
#
#
# def handle_success(url):
#     """
#     Handle successful URL validation and addition.
#
#         Args:
#             url (str): The validated URL.
#
#         Returns:
#             str: Redirects to the details page of the added URL.
#     """
#     website = {'url': url, 'created_at': format_timestamp()}
#     add_website(website)
#
#     id = get_urls_by_name(url)['id']
#
#     flash('Страница успешно добавлена', 'alert-success')
#     return redirect(url_for('url_by_id', id=id))
