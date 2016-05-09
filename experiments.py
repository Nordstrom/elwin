'''
experiments defines functions for determining experiments to show
'''
import os
from planout.experiment import SimpleInterpretedExperiment
from planout.assignment import Assignment, RandomInteger
from storage import queryMongoStorage


# Thin layer in front of planout.
class Experiments:
    def __init__(self):
        host = os.getenv('DB_CONN', 'mongodb://elwin-storage:27017')
        self.storage = queryMongoStorage(host, 'test')

    # Get the parameters of a planout experiment.
    def get_experiment_params(self, team_name, experiment_name, unit):
        # Attempt to get the script out of storage.  If it isn't found, the exception
        # will bubble up and get returned as a 500.
        (name, num_seg, experiments) = self.storage.get_exp_params_by_exp_name(
            team_name, experiment_name)
        seg = self.get_segment(name, num_seg, unit=unit)
        good = (exp
                for exp in experiments
                if seg in exp['segments'] and exp['name'] == experiment_name)
        res = {}
        for g in good:
            exp = SimpleInterpretedExperiment(userId=unit, unit=unit)
            exp.name = g['name']
            exp.script = g['definition']
            exp.set_auto_exposure_logging(False)

            params = exp.get_params()
            res[exp.name] = params
        return res

    def get_experiment_params_for_team(self, teamName, unit):
        namespaces = self.storage.get_exps_params_by_group_id(teamName)
        res = {}
        for name, num_seg, experiments in namespaces:
            seg = self.get_segment(name, num_seg, unit=unit)
            good = (exp for exp in experiments if seg in exp['segments'])
            for g in good:
                exp = SimpleInterpretedExperiment(userId=unit, unit=unit)
                exp.name = g['name']
                exp.script = g['definition']
                exp.set_auto_exposure_logging(False)

                params = exp.get_params()
                res[exp.name] = params
        return res

    def get_segment(self, name, num_segments, **units):
        # randomly assign primary unit to a segment
        ass = Assignment(name)
        ass.segment = RandomInteger(min=0, max=num_segments - 1, **units)
        return ass.segment
