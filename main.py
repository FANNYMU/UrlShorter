from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from random import choices
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(6), unique=True, nullable=False)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(choices(characters, k=6))
    link = URL.query.filter_by(short_url=short_url).first()

    if link:
        return generate_short_url()
    return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url()
        new_link = URL(original_url=original_url, short_url=short_url)
        db.session.add(new_link)
        db.session.commit()
        return f'Shortened URL: <a href="/{short_url}">{request.host}/{short_url}</a>'
    return '''
        <form method="POST">
            Original URL: <input type="text" name="original_url">
            <input type="submit" value="Shorten">
        </form>
    '''

@app.route('/<short_url>')
def redirect_to_original(short_url):
    link = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
