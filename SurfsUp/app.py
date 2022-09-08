from unicodedata import name
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


############################
# Data Set up
############################

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

#############################
# Flask Set up
#############################

# Create an app
app = Flask(__name__)

# Define static routes
@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate app!</h1>"  
        f"<h2>Please find below a list of all available routes</h2>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for Temperature observations: /api/v1.0/tobs<br/>"
        f"Temperature for latest date: /api/v1.0/start<br/>"
        f"Temperature for last year: /api/v1.0/start/end<br/>"
        )

# set app def for Precipitation 

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    selec = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*selec).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

# set app def for stations 

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    # Set query for stations.
    stations = session.query(Station.station, Station.name,
                             Station.latitude, Station.longitude, Station.elevation).all()   

    session.close()

# convert query to dictionary
 
    stations_list = []

    for station, name, latitude, longitude, elevation in station:
        station_dict ={}
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation

        stations_list.append(station_dict)

    return jsonify(stations_list)



# set app def for temperature observations

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)


    # query for timeframe required

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)


    # find most active station

    selec = [Measurement.station, func.count(Measurement.id)]
    active_station = session.query(*selec).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()

    station_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == active_station).filter(Measurement.date >= latestdate).all()

    session.close()

    # convert query results to dict

    temps = []

    for date, tobs in station_data:
        temps_dict = {}
        temps_dict['date'] = date
        temps_dict['tobs'] = tobs

        temps.append(temps_dict)

    return jsonify(temps)

# set app def for temperatures min, avg, max from start date. 

@app.route('/api/v1.0/<start>')
def start():
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)

    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= querydate).all()
    session.close()

    all_temps = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_temps.append(tobs_dict)

    return jsonify(all_temps)

# set app def for temperatures min, avg, max from start to end date. 
@app.route('/api/v1.0/<start>/<stop>')
def start_stop():
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)

    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= querydate).filter(Measurement.date <= recent_date).all()
    session.close()

    all_temps = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_temps.append(tobs_dict)

    return jsonify(all_temps)
    
# Define main behaviour
    if __name__ == '__main__':
        app.run(debug=True)