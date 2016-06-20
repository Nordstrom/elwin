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

'''
experiments defines functions for determining experiments to show
'''
import os
from planout.experiment import SimpleInterpretedExperiment
from planout.assignment import Assignment, RandomInteger
from storage import queryMongoStorage

def get_segment(name, num_segments, **units):
    # randomly assign primary unit to a segment
    ass = Assignment(name)
    ass.segment = RandomInteger(min=0, max=num_segments - 1, **units)
    return ass.segment

def get_unit_dict(units, args):
    d = {}
    for u in units:
        d[u] = args.get(u)
    return d

def get_unit_arr(units, args):
    return [args.get(u) for u in units]

# Thin layer in front of planout.
class Experiments:
    def __init__(self):
        host = os.getenv('DB_CONN', 'mongodb://elwin-storage:27017')
        self.storage = queryMongoStorage(host, 'test')

    def get_experiment_params_for_team(self, team_name, args):
        """Get experiment params for a given team and unit type.

        get_experiment_params_for_team checks the storage and gets all matching
        experiments for the given group-id and units.

        Args:
            team_name string: group-id to search for.
            args ImmutableDict: the query params to use as units and inputs.
        Returns:
            A dict of experiments.
        Throws:
            ValueError if no experiments are found.
        """

        units = [u for u in args.keys() if u != "group-id"]
        namespaces = self.storage.get_exps_params_by_group_id(team_name, units)
        res = {}
        for ns in namespaces:
            u_arr = get_unit_arr(ns['units'], args)
            u_dict = get_unit_dict(ns['units'], args)
            seg = get_segment(ns['name'], ns['num_segments'], unit=u_arr)
            good = (exp for exp in ns['experiments'] if seg in exp['segments'])
            for g in good:
                exp = SimpleInterpretedExperiment(**u_dict)
                exp.name = g['name']
                exp.script = g['definition']
                exp.set_auto_exposure_logging(False)

                params = exp.get_params()
                res[exp.name] = params
        if not res:
            raise ValueError("Not found, group-id: %s, unit-type: %s" % (team_name, args))
        return res
