from flask import *
from storage import Storage
from experiments import Experiments

storage = Storage()
experiments = Experiments()

# Create the application, elastic beanstalk expects the name "application"
application = Flask(__name__)

# Return the parameters relevant to a specific experiment
@application.route("/<teamName>/<experimentName>/<userId>")
def get__experiment_response(teamName, experimentName, userId):

    # Get the experiment definition from storage
    script = storage.get_experiment_def(experimentName)

    # Get the params for the instance of the experiment
    experimentParams = experiments.get_experiment_params(experimentName, script, userId = userId)

    # Build the response object and return it as json
    outDict = {}
    outDict[experimentName] = experimentParams
    return jsonify(outDict)

# run the app.
if __name__ == "__main__":
    application.run(debug=True)
