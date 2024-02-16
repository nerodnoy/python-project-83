import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from page_analyzer.constants import *
from page_analyzer.validate import (
    validate_url,
    get_url_data
)
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from page_analyzer.database import (
    get_urls_all,
    get_urls_by_id,
    get_urls_by_name,
    get_checks_by_id,
    add_check,
    add_site
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.errorhandler(404)
def page_not_found(error):
    """
    Render 404 error page if the requested page is missing.

    :return: Render 404 error page.
    """

    return render_template(
        'error.html'
    ), 404


@app.route('/')
def index():
    """
    Render the index page.

        Returns:
            str: Rendered HTML template for the index page.
    """

    return render_template(
        'index.html',
    )


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


@app.post('/urls')
def urls_post():
    """
    Handle the POST request to add a new URL.

        Returns:
            str: Rendered HTML template for success or error page.
    """

    url = request.form.get('url')
    check = validate_url(url)

    url = check['url']
    error = check['error']

    if error:
        if error == URL_EXISTS:

            id = get_urls_by_name(url)['id']

            flash('Страница уже существует', 'alert-info')
            return redirect(url_for(
                'url_by_id',
                id=id
            ))
        else:
            flash('Некорректный URL', 'alert-danger')

            if error == URL_NOT_FOUND:
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

        add_site(site)

        id = get_urls_by_name(url)['id']

        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for(
            'url_by_id',
            id=id
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
            '404.html'
        ), 404


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
        check['checked_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        add_check(check)

        flash('Страница успешно проверена', 'alert-success')

    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')

    return redirect(url_for(
        'url_by_id',
        id=id
    ))


if __name__ == '__main__':
    app.run()
