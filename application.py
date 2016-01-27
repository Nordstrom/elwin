from flask import *
from experiments import Experiments

experiments = Experiments()

# Create the application, elastic beanstalk expects the name "application"
application = Flask(__name__)

# Return the parameters relevant to a specific experiment
@application.route("/<teamName>/<experimentName>/<userId>")
def get_experiment_response(teamName, experimentName, userId):

    # Get the params for the instance of the experiment
    experimentParams = experiments.get_experiment_params(experimentName, userId = userId)

    # Build the response object and return it as json
    outDict = {}
    outDict[experimentName] = experimentParams
    return jsonify(outDict)

@application.route("/<teamName>/<userId>")
def get_experiments_for_team(teamName, userId):
    outDict = experiments.get_experiment_params_for_team(teamName, userId = userId)
    return jsonify(outDict)

# run the app.
if __name__ == "__main__":
    application.run(debug=True)
