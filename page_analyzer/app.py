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
from validator import validate_url
from page_analyzer.db import get_urls_by_name
import os


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
        if error == 'This URL already exists':
            id = get_urls_by_name(url)['id']

            flash('Странница с таким URL уже существует', 'error')

            return redirect(url_for('url_show', id=id))
        else:
            flash('Некорректный URL адрес', 'error')

            if error == 'URL length cannot be zero':
                flash('URL адрес не может быть пустым', 'error')
            elif error == 'URL length should be shorter than 255 characters':
                flash('Длина URL адреса превышает 255 символов', 'error')

            messages = get_flashed_messages(with_categories=True)

            return render_template('index.html',
                                   url=url,
                                   messages=messages
                                   ), 422




if __name__ == '__main__':
    app.run()
