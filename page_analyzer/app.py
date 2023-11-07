from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
from dotenv import load_dotenv
from page_analyzer.valid import validate_url, get_url_data
from page_analyzer.db import (
    get_urls_by_name,
    get_urls_by_id,
    get_urls_all,
    add_website,
    add_check
)
import os
from datetime import datetime
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    validate = validate_url(url)

    url = validate['url']
    error = validate['error']

    if error:
        if error == 'URL already exists':
            id = get_urls_by_name(url)['id']

            flash('Страница уже существует', 'alert-fact')

            return redirect(url_for('url_by_id', id=id))
        else:
            flash('Некорректный URL', 'alert-warning')

            if error == 'URL length = 0':
                flash('URL обязателен', 'alert-warning')
            elif error == 'URL length > 255 ':
                flash('URL превышает 255 символов', 'alert-warning')

            messages = get_flashed_messages(with_categories=True)

            return render_template('index.html',
                                   url=url,
                                   messages=messages
                                   ), 422
    else:
        website = {
            'url': url,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        add_website(website)

        id = get_urls_by_name(url)['id']

        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for(
            'url_by_id',
            id=id
        ))


@app.get('/urls')
def urls_get():
    urls = get_urls_all()

    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'urls.html',
        urls=urls,
        messages=messages
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        '404.html'
    ), 404


@app.route('/urls/<int:id>')
def url_by_id(id):
    try:
        url = get_urls_by_id(id)

        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'url.html',
            url=url,
            messages=messages
        )
    except IndexError:
        return render_template(
            '404.html'
        ), 404


@app.post('/urls/<int:id>/checks')
def url_check(id):
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
