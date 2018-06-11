import datetime as dt
import numpy as np
import pandas as pd

import json

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

from flask_sqlalchemy import SQLAlchemy

import sqlalchemy 

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import func
from pprint import pprint

from sqlalchemy.ext.declarative import declarative_base

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Database Setup
#################################################
'''
Using a Declarative Base
'''
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DataSets/belly_button_biodiversity.sqlite"

db = SQLAlchemy(app)

class MetaData(db.Model):
    __tablename__ = 'samples_metadata'
    id = db.Column(db.Integer, primary_key=True)
    sampleid = db.Column(db.Integer)
    age = db.Column(db.Integer)
    bbtype = db.Column(db.String)
    gender = db.Column(db.String)
    ethnicity = db.Column(db.String)
    location = db.Column(db.String)
    wfreq = db.Column(db.Integer)

class OTU(db.Model):
    __tablename__ = 'otu'

    id = db.Column(db.Integer, primary_key=True)
    otu_id = db.Column(db.Integer)
    lowest_taxonomic_unit_found = db.Column(db.String)

'''
Using automap_base
'''

Base = automap_base()
engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")
Base.prepare(engine, reflect = True)
keys = Base.classes.keys()
print(keys)
Samples = Base.classes.samples
session = Session(engine)


# Create database tables
@app.before_first_request
def setup():
    db.create_all()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/names')
def names():
    sel = [MetaData.sampleid]
    sample_results = db.session.query(*sel).all()
    return jsonify(sample_results)
 
@app.route('/otu')
def otu():
    sel = [OTU.lowest_taxonomic_unit_found]
    otu_results = db.session.query(*sel).all()
    return jsonify(otu_results)
'''
@app.route('/metadata')
def metadata():
    sel = [MetaData.sampleid, MetaData.age, MetaData.bbtype, MetaData.gender, MetaData.location, MetaData.ethnicity]
    metadata_results = db.session.query(*sel).all()
    df = pd.DataFrame(metadata_results, columns = ['SAMPLEID','AGE','BBTYPE','GENDER','LOCATION','ETHNICITY'])
    return jsonify(df.to_dict(orient="records"))
'''
@app.route('/metadata/<sample>')
def metadata(sample):
    sel = [MetaData.sampleid, MetaData.age, MetaData.bbtype, MetaData.gender, MetaData.location, MetaData.ethnicity]
    result_dict = {}
    for sampleid, age, bbtype, gender, location, ethnicity in db.session.query(*sel).filter(MetaData.sampleid == int(sample)):
        result_dict = {'AGE':age, 'BBTYPE': bbtype, 'GENDER': gender, 'LOCATION': location, 'ETHNICITY': ethnicity}
    return jsonify(result_dict)

'''
@app.route('/wfreq')
def wfreq():
    sel = [MetaData.wfreq, MetaData.sampleid]
    wfreq_results = db.session.query(*sel).all()
    df = pd.DataFrame(wfreq_results, columns = ['WFREQ','SAMPLEID'])
    return jsonify(df.to_dict(orient="records"))
'''
@app.route('/wfreq/<sample>')
def wfreq(sample):
    sel = [MetaData.sampleid, MetaData.wfreq]
    result_wash = {}
    for sampleid, wfreq in db.session.query(*sel).filter(MetaData.sampleid == int(sample)):
        result_wash = {'SAMPLEID': sampleid, 'WFREQ': wfreq}
    return jsonify(result_wash)

@app.route('/samples')
def samples():
    sel = [OTU.otu_id, MetaData.sampleid]
    samples_list = db.session.query(*sel).all()
    df = pd.DataFrame(samples_list, columns = ['OTUID','SAMPLEID'])
    df = df.sort_values(by=['SAMPLEID'], ascending =False)  
    return df.to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=True)
