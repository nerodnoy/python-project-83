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
from page_analyzer.valid import validate_url
from page_analyzer.db import (
    get_urls_by_name,
    get_urls_by_id,
    get_urls_all,
    add_website
)
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello():
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

            flash('Страница уже существует', 'fact')

            return redirect(url_for('url_by_id', id=id))
        else:
            flash('Некорректный URL', 'error')

            if error == 'URL length = 0':
                flash('URL обязателен', 'error')
            elif error == 'URL length > 255 ':
                flash('URL превышает 255 символов', 'error')

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

        flash('Страница успешно добавлена', 'success')
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


if __name__ == '__main__':
    app.run()
