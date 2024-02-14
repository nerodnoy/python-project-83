from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
from page_analyzer.database import (
    get_urls_by_id,
    get_urls_all,
    get_checks_by_id,
    add_check,
    add_website,
    get_urls_by_name
)
from page_analyzer.handlers import (
    format_timestamp
)
from page_analyzer.constants import (
    URL_EXISTS,
    URL_TOO_LONG,
    URL_EMPTY
)
import os
from dotenv import load_dotenv
from requests import RequestException
from page_analyzer.validate import validate_url, get_url_data


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    """
    Render the index page.

        Returns:
            str: Rendered HTML template for the index page.
    """
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    """
    Add new URL. Check if there is one provided. Validate the URL.
    Add it to db if this URL isn't already there. Raise an error if any occurs.

        Returns:
             Redirect to one URL page if new URL added or it is already in db.
             Render index page with flash error if any.
    """

    url = request.form.get('url')
    check = validate_url(url)

    url = check['url']
    error = check['error']

    if error:
        if error == URL_EXISTS:

            id_ = get_urls_by_name(url)['id']

            flash('Страница уже существует', 'alert-info')
            return redirect(url_for(
                'url_by_id',
                id_=id_
            ))
        else:
            flash('Некорректный URL', 'alert-danger')

            if error == URL_EMPTY:
                flash('URL обязателен', 'alert-danger')
            elif error == URL_TOO_LONG:
                flash('URL превышает 255 символов', 'alert-danger')

            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'index.html',
                url=url,
                messages=messages
            ), 422

    else:
        site = {
            'url': url,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        add_website(site)

        id_ = get_urls_by_name(url)['id']

        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for(
            'url_by_id',
            id_=id_
        ))


@app.route('/urls/<int:id>')
def url_by_id(id):
    """
    Handle the request to display information about a
    specific URL and its checks.

        Args:
            id (int): The ID of the URL.

        Returns:
            str: Rendered HTML template with information about
            the URL and its checks.
    """
    try:
        url = get_urls_by_id(id)
        checks = get_checks_by_id(id)

        messages = get_flashed_messages(with_categories=True)

        return render_template(
            'url.html',
            url=url,
            checks=checks,
            messages=messages
        )
    except IndexError:
        return render_template(
            'error.html'
        ), 404


@app.get('/urls')
def urls_get():
    """
    Handle the GET request to retrieve all URLs.

        Returns:
            str: Rendered HTML template with a list of URLs.
    """
    urls = get_urls_all()

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'urls.html',
        urls=urls,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    """
    Handle the POST request to perform a check on a specific URL.

        Args:
            id (int): The ID of the URL.

        Returns:
            str: Redirects to the URL details page after performing the check.
        """
    url = get_urls_by_id(id)['name']

    try:
        check = get_url_data(url)

        check['url_id'] = id
        check['checked_at'] = format_timestamp()

        add_check(check)

        flash('Страница успешно проверена', 'alert-success')

    except RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')

    return redirect(url_for(
        'url_by_id',
        id=id
    ))


@app.errorhandler(404)
def get_error(error):
    """
    Handle the 404 Internal Server Error.

        Args:
            error: The error information.

        Returns:
            str: Rendered HTML template for the error page.
    """
    return render_template(
        'error.html'
    ), 404


if __name__ == '__main__':
    app.run()
