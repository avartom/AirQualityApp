"""OpenAq  Air Quality Dashboard with Flask."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
DB = SQLAlchemy(app)
api = openaq.OpenAQ()


class Record(DB.Model):
    """defines the table columns"""
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"date is {self.datetime} and value is {self.value}"


def get_results():
    """makes a list of datatime and value tuples"""
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    temp = []
    if status == 200:
        for i in range(len(body['results'])):
            utc_date = body['results'][i]['date']['utc']
            value = body['results'][i]['value']
            record = (utc_date, value)
            temp.append(record)
    return temp


@app.route('/')
def root():
    """Base view."""
    # record = get_results()
    y = Record.value >= 18
    rec = Record.query.filter(y).all()
    return f"{rec}"


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # Get data from OpenAQ, make Record objects with it
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    if status == 200:
        for j in range(len(body['results'])):
            utc = body['results'][j]['date']['utc']
            value = body['results'][j]['value']
            db_rec = Record(datetime=utc, value=value)
            DB.session.add(db_rec)
    DB.session.commit()
    return 'Data refreshed!'
