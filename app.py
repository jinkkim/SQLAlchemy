# A Flask API based on the hawaii database

# Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template
import numpy as np

import datetime as dt


# Create engine connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# get the date of one year from the latest date
last_day = list(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
last_day_str = ''.join(last_day)
last_day_datetime = dt.datetime.strptime(last_day_str,'%Y-%m-%d')
one_year_ago = last_day_datetime -dt.timedelta(days=365)
one_year_ago_str = dt.datetime.strftime(one_year_ago,'%Y-%m-%d')

# Flask Setup
app = Flask(__name__)

# Routes
@app.route("/")
def welcome():
    #return (
    #    f"Available Routes:<br/>"
    #    f"/api/v1.0/precipitation<br/>"
    #    f"/api/v1.0/stations<br/>"
    #    f"/api/v1.0/tobs<br/>"
    #    f"/api/v1.0/&ltstart_date&gt (date example: YYYY-MM-DD)<br/>"
    #    f"/api/v1.0/&ltstart_date&gt/&ltend_date&gt (date example: YYYY-MM-DD)"
    #)
    return render_template('index.html')

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, func.sum(Measurement.prcp).label('total_precipitation')).group_by(Measurement.date).all()
    precipitate_all = []
    for a in results:
        precipitate_dict = {}
        precipitate_dict[a.date] = a.total_precipitation
        precipitate_all.append(precipitate_dict)
    return jsonify(precipitate_all)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station).all()
    station_all = []
    for b in results:
        station_dict = {}
        station_dict["station"] = b.station
        station_dict["name"] = b.name
        station_dict["latitude"] = b.latitude
        station_dict["longitude"] = b.longitude
        station_dict["elevation"] = b.elevation
        station_all.append(station_dict)
    return jsonify(station_all)


@app.route("/api/v1.0/tobs")
def temperature():
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago_str).all()

    temp_all = []
    for c in results:
        temp_dict = {}
        temp_dict[c.date] = c.tobs
        temp_all.append(temp_dict)

    return jsonify(temp_all)


@app.route("/api/v1.0/<start>")
def temp_start(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_result =[
        {"The lowest temperature" : results[0][0]},
        {"Average temperature" : results[0][1]},
        {"The highest temperature" : results[0][2]}
    ]
        
    return jsonify(temp_result)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
                filter(Measurement.date >= start). \
                filter(Measurement.date <= end). \
                all()

    temp_result =[
        {"The lowest temperature" : results[0][0]},
        {"Average temperature" : results[0][1]},
        {"The highest temperature" : results[0][2]}
    ]
        
    return jsonify(temp_result)

if __name__ == '__main__':
    app.run(debug=True)