import openaq
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

def get_results(city='Los Angeles', parameter='pm25'):
    api = openaq.OpenAQ()
    status, response = api.measurements(city=city, parameter=parameter)
    if status == 200:
        utc_datetime = [(result['date']['utc'], result['value']) for result in response['results']]
        return (utc_datetime)

@app.route('/')
def index():
    """Base view"""
    results = get_results()
    return render_template('index.html', results=results)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)

class Record(DB.Model):
    '''Reassigning id, datetime and value attributes'''
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String())
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"<Record(datetime={self.datetime}, value={self.value})>"

@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # Get data from OpenAQ, make Record objects with it, and add to db

    results = get_results()
    for date_time, value in results:
        record = Record(datetime=date_time, value=value)
        DB.session.add(record)

    DB.session.commit()
    return 'Data refreshed!'

