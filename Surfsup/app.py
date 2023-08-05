from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

# Create the Flask app
app = Flask(__name__)

# Create an engine to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the classes
station = Base.classes.station
measurement = Base.classes.measurement

# Home route to list all available routes
@app.route("/")
def home():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    prcp_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= last_year).all()
    session.close()

    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(station.station).all()
    session.close()

    stations_data = [{"station": station[0]} for station in station_list]
    return jsonify(stations_data)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]
    last_date = session.query(measurement.date).\
        filter(measurement.station == most_active_station).\
        order_by(measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    temp_obs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= last_year).all()
    session.close()

    temp_obs_dict = {date: temp for date, temp in temp_obs}
    return jsonify(temp_obs_dict)

# Start and end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    session = Session(engine)
    if end:
        temp_stats = session.query(func.min(measurement.tobs),
                                   func.avg(measurement.tobs),
                                   func.max(measurement.tobs)).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
    else:
        temp_stats = session.query(func.min(measurement.tobs),
                                   func.avg(measurement.tobs),
                                   func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
    session.close()

    temp_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temp_stats]
    return jsonify(temp_stats_list)

if __name__ == "__main__":
    app.run(debug=True)
