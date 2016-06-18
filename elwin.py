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

    if not group_id:
        return "must supply group-id", 400

    if len(request.args) == 1:
        return "must supply other params", 400

    try:
        exps = experiments.get_experiment_params_for_team(
            group_id, request.args)
    except ValueError as e:
        return str(e), 404
    except Exception, e:
        return jsonify({"error": str(e)}), 500
    else:
        out_dict = {}
        out_dict["experiments"] = exps
        return jsonify(out_dict), 200

@app.route("/healthz")
def get_health():
    """
    get_health returns a health status for load balancer
    """
    return "OK", 200

# run the app.
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0")
