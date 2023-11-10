from flask import (
    render_template,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
from page_analyzer.db import (
    get_urls_by_name,
    add_website,
)
from page_analyzer.const import (
    URL_EXISTS,
    URL_TOO_LONG,
    URL_INVALID,
    URL_EMPTY
)
from datetime import datetime


def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def handle_error(error, url):
    if error == URL_EXISTS:
        id = get_urls_by_name(url)['id']
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_by_id', id=id))

    elif error == URL_EMPTY:
        flash('URL обязателен', 'alert-danger')

    elif error == URL_INVALID:
        flash('Некорректный URL', 'alert-danger')

    elif error == URL_TOO_LONG:
        flash('URL превышает 255 символов', 'alert-danger')

    messages = get_flashed_messages(with_categories=True)

    return render_template('index.html', url=url, messages=messages), 422


def handle_success(url):
    website = {'url': url, 'created_at': format_timestamp()}
    add_website(website)

    id = get_urls_by_name(url)['id']

    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('url_by_id', id=id))