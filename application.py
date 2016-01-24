from flask import *
from storage import Storage
from experiments import Experiments

storage = Storage()
experiments = Experiments()

application = Flask(__name__)

# return experiment with params
@application.route("/<teamName>/<experimentName>/<userId>")
def get_response(teamName, experimentName, userId):
    outDict = {}

    script = storage.get_experiment_def(experimentName)
    experimentParams = experiments.get_experiment_params(experimentName, script, userId = userId)
    outDict[experimentName] = experimentParams

    print "returning " + str(outDict)
    return jsonify(outDict)

# run the app.
if __name__ == "__main__":
    application.run(debug=True)
