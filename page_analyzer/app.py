from flask import (
    Flask,
    render_template
)
from dotenv import load_dotenv
import os

# import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def hello():
    return render_template(
        'index.html'
    )


if __name__ == '__main__':
    app.run()
