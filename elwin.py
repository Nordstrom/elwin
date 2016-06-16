# Copyright 2016 Nordstrom Inc., authors, and contributors <see AUTHORS file>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
def get_experiments_for_team():
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
    unit_type = request.args.getlist('unit-type')
    unit = request.args.getlist('unit')

    if not group_id or not unit_type or not unit:
        return "must supply group-id, unit-type, and unit", 400

    if not len(unit_type) == len(unit):
        return "must have equal number of unit-type and unit", 400

    try:
        out_dict = {}
        out_dict["experiments"] = experiments.get_experiment_params_for_team(
            group_id, unit_type, unit)
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
