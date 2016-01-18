from flask import Flask
import flask
from planout.experiment import SimpleInterpretedExperiment
import json
import os


# function that generates experiment objects

def genExperiment(name, script, **inputs):
    e = SimpleInterpretedExperiment(**inputs) # this allows us to create an expermeint object from a json definition
    e.name = name # give it a name, this is used in hashing so these need to be unique
    e.script = script # will pull in the json definition here
    e.set_auto_exposure_logging(False)
    return e

#read in experiment definitions

nameScriptDict = {}

for exp in os.listdir("experiments"): #read in the experiment definitions, maybe store these in dynamo or something
    name = exp.split(".")[0]
    script = json.loads(open("experiments/" + exp).read())
    nameScriptDict[name] = script

# return experiment with params

def get_response(experiment = 'atb_test', userid = 2):
    outDict = {}
    x = genExperiment(name = experiment, script = nameScriptDict[experiment], userid = userid).get_params()
    outDict[experiment] = x
    return outDict

# EB looks for an 'application' callable by default.
application = Flask(__name__)


# add a rule when the page is accessed with unit appended
application.add_url_rule('/<expname>/<userid>', 'exp', (lambda expname, userid:
    flask.jsonify(get_response(expname, userid))))

# run the app.
if __name__ == "__main__":
    application.run()
