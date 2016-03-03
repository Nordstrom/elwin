from flask import *
from experiments import Experiments

experiments = Experiments()

# Create the application, elastic beanstalk expects the name "application"
application = Flask(__name__)

# Return the parameters relevant to a specific experiment
@application.route("/<teamName>/<experimentName>/<userId>")
def get_experiment_response(teamName, experimentName, userId):

    # Get the params for the instance of the experiment
    try:
        # Build the response object and return it as json
        outDict = {}
        outDict[experimentName] = experiments.get_experiment_params(experimentName, userId = userId)
        return jsonify(outDict), 200
    except:
        return jsonify({"error": "Experiment Not Found"}), 500

@application.route("/<teamName>/<userId>")
def get_experiments_for_team(teamName, userId):

    try:
        outDict = {}
        outDict["experiments"] = experiments.get_experiment_params_for_team(teamName, userId)
        return jsonify(outDict), 200
    except:
        return jsonify({"error": "Team Name Not Found"}), 500

# run the app.
if __name__ == "__main__":
    application.run()
