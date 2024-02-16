from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
import os
from dotenv import load_dotenv
from datetime import datetime
import requests

from page_analyzer.validate import (
    validate_url,
    get_url_data
)
from page_analyzer.database import (
    get_all_urls,
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
    Render index page.

    :return: Render index page.
    """

    return render_template(
        'index.html',
    )


@app.get('/urls')
def urls_get():
    """
    Render all added URLs page with last check dates and status codes if any.

    :return: Render all URLs page.
    """

    urls = get_all_urls()

    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'urls.html',
        urls=urls,
        messages=messages
    )


@app.post('/urls')
def urls_post():
    """
    Add new URL. Check if there is one provided. Validate the URL.
    Add it to db if this URL isn't already there. Raise an error if any occurs.

    :return: Redirect to one URL page if new URL added or it is already in db.
    Render index page with flash error if any.
    """

    url = request.form.get('url')
    check = validate_url(url)

    url = check['url']
    error = check['error']

    if error:
        if error == 'exists':

            id_ = get_urls_by_name(url)['id']

            flash('Страница уже существует', 'alert-info')
            return redirect(url_for(
                'url_show',
                id_=id_
            ))
        else:
            flash('Некорректный URL', 'alert-danger')

            if error == 'zero':
                flash('URL обязателен', 'alert-danger')
            elif error == 'length':
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

        id_ = get_urls_by_name(url)['id']

        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for(
            'url_show',
            id_=id_
        ))


@app.route('/urls/<int:id_>')
def url_show(id_):
    """
    Render one URL page containing its parsed check data.

    :param id_: URL id.
    :return: Render page or raise 404 error.
    """

    try:
        url = get_urls_by_id(id_)
        checks = get_checks_by_id(id_)

        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'show.html',
            url=url,
            checks=checks,
            messages=messages
        )
    except IndexError:
        return render_template(
            '404.html'
        ), 404


@app.post('/urls/<int:id_>/checks')
def url_check(id_):
    """
    Check requested URL. Add data to db or raise error.

    :param id_: URL id.
    :return: Redirect to one URL show page adding check data to db or returning
    error if an error occured during check.
    """

    url = get_urls_by_id(id_)['name']

    try:
        check = get_url_data(url)

        check['url_id'] = id_
        check['checked_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        add_check(check)

        flash('Страница успешно проверена', 'alert-success')

    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')

    return redirect(url_for(
        'url_show',
        id_=id_
    ))


if __name__ == '__main__':
    app.run()