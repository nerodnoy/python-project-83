from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
from page_analyzer.db import (
    get_urls_by_id,
    get_urls_all,
    get_checks_by_id,
    add_check
)
from page_analyzer.handler import (
    handle_error,
    handle_success,
    format_timestamp
)
import os
from dotenv import load_dotenv
from requests import RequestException
from page_analyzer.valid import validate_url, get_url_data

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    submitted_url = request.form.get('url')
    validate = validate_url(submitted_url)

    url = validate['url']
    error = validate['error']

    # вынесены в отдельный модуль handlers
    if error:
        return handle_error(error, url)
    else:
        return handle_success(url)


@app.get('/urls')
def urls_get():
    urls = get_urls_all()

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'all_urls.html',
        urls=urls,
        messages=messages
    )


@app.route('/urls/<int:id>')
def url_by_id(id):
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
        ), 500


@app.post('/urls/<int:id>/checks')
def url_check(id):
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


@app.errorhandler(500)
def get_error(error):
    return render_template(
        'error.html'
    ), 500


if __name__ == '__main__':
    app.run()
