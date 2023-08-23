# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
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

@app.route('/')
def home():
    return (
        f"Welcome to the Flask API!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Query the last 12 months of precipitation data
    one_year_ago = dt.datetime.strptime("2017-08-23", '%Y-%m-%d') - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query the list of station names
    station_data = session.query(Station.name).all()
    station_names = [name[0] for name in station_data]
    
    # Return a JSON list of station names
    return jsonify(station_names)

@app.route('/api/v1.0/tobs')
def tobs():
    # Query temperature observations for the most-active station
    most_active_station_id = "USC00519281"
    one_year_ago = dt.datetime.strptime("2017-08-23", '%Y-%m-%d') - dt.timedelta(days=365)
    temperature_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()
    temperature_list = [temp[0] for temp in temperature_data]
    
    # Return a JSON list of temperature observations
    return jsonify(temperature_list)

@app.route('/api/v1.0/<start>')
def temp_range_start(start):
    # Convert the input start date to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    
    # Query TMIN, TAVG, and TMAX for dates >= start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    # Return a JSON dictionary with the calculated temperatures
    return jsonify({"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][1], "TMAX": temperature_stats[0][2]})

@app.route('/api/v1.0/<start>/<end>')
def temp_range_start_end(start, end):
    # Convert the input start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
    # Query TMIN, TAVG, and TMAX for dates between start and end dates (inclusive)
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    # Return a JSON dictionary with the calculated temperatures
    return jsonify({"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][1], "TMAX": temperature_stats[0][2]})

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
