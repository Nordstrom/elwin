"""
myapp runs planout as a service
"""
from flask import Flask, jsonify, request
from experiments import Experiments

experiments = Experiments()

# Create the application, elastic beanstalk expects the name "application"
app = Flask(__name__)


# Return the parameters relevant to a specific experiment
@app.route("/<team_name>/<experiment_name>/<unit>")
def get_experiment_response(team_name, experiment_name, unit):
    """Return JSON of a specific experiment

    Args:
        team_name: name of the team (group_id)
        experiment_name: name of the experiment
        unit: unique identifier for user

    Returns:
        JSON string of experiment
    """

    # Get the params for the instance of the experiment
    try:
        # Build the response object and return it as json
        out_dict = {}
        out_dict['experiments'] = experiments.get_experiment_params(
            team_name, experiment_name, unit)
        return jsonify(out_dict), 200
    except:
        return jsonify({"error": "Experiment Not Found"}), 500


@app.route("/")
def get_experiments_for_team(team_name, unit):
    """Return JSON for team's experiments

    get_expirments_for_team returns experiments json of all experiments
    associated with a team

    Args:
        team_name: name of the team (group_id)
        unit: unique identifier for user

    Returns:
        JSON string of experiments
    """

    group_id = request.args.get('group-id')
    unit_type = request.args.get('unit-type')
    unit = request.args.get('unit')

    if not (group_id and unit):
        return "ur a turd", 400

    try:
        out_dict = {}
        out_dict["experiments"] = experiments.get_experiment_params_for_team(
            group_id, unit-type, unit)
        return jsonify(out_dict), 200
    except:
        return jsonify({"error": "Team Name Not Found"}), 500


@app.route("/healthz")
def get_health():
    """
    get_health returns a health status for load balancer
    """
    return "OK", 200

# run the app.
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0")
