import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
Stations = Base.classes.stations
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Avalable Routes:<br/>"
        
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"

        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"

        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"

        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"

        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Query for the dates and precipitation observations from the last year."""
    prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    prcp_totals = []
    for rain in prcp:
        row = {}
        row["date"] = prcp[0]
        row["prcp"] = prcp[1]
        prcp_totals.append(row)

    return jsonify(prcp_totals)


@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    results = session.query(Stations.station, Stations.name).all()
    
    # Create a dictionary from the row data and append to a list of stations
    station_total = []
    for station in results:
        row = {}
        row["station"] = results[0]
        row["name"] = results[1]
        station_total.append(row)

    return jsonify(station_total)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Query for the dates and temperature observations from the last year."""
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
        group_by(Measurement.date).all()

# Create a list of dicts with `date` and `tob` as the keys and values
    tobs_total = []
    for temp in results:
        row = {}
        row["date"] = results[0]
        row["tob"] = results[1]
        tobs_total.append(row)

    return jsonify(tobs_total)


@app.route("/api/v1.0/<start>")
def temp(start):

 # last year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end_year = dt.date(2017, 8, 23)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_year).all()

    temp = list(np.ravel(results))
    
    return jsonify(temp)

@app.route("/api/v1.0/<start>/<end_date>")
def trip_temp(start, end_date):
    start_date_dt= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date_dt= dt.datetime.strptime(end_date,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date_dt - last_year
    end_date = end_date_dt - last_year

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end_date).all()

    trip_temp = list(np.ravel(results))

    return jsonify(trip_temp)


if __name__ == '__main__':
    app.run(debug=True)
