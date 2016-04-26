from planout.experiment import SimpleInterpretedExperiment
from planout.assignment import *
from storage import queryMongoStorage

# Thin layer in front of planout.
class Experiments:
    def __init__(self):
        self.storage = queryMongoStorage('mongodb://elwin-storage:27017', 'test')

    # Get the parameters of a planout experiment.
    def get_experiment_params(self, experimentName, **units):
        # Attempt to get the script out of storage.  If it isn't found, the exception
        # will bubble up and get returned as a 500.
        (name, num_seg, experiments) = self.storage.get_exp_params_by_exp_name(experimentName)
        seg = self.get_segment(name, num_seg, **units)
        good = [exp for exp in experiments if seg in exp['segments'] and exp['name'] == experimentName]
        res = {}
        for g in good:
            e = SimpleInterpretedExperiment(**units)
            e.name = g['name']
            e.script = g['definition']
            e.set_auto_exposure_logging(False)

            params = e.get_params()
            res[e.name] = params
        return res

    def get_experiment_params_for_team(self, teamName, **units):
        namespaces = self.storage.get_exps_params_by_group_id(teamName)
        res = {}
        for name, num_seg, experiments in namespaces:
            seg = self.get_segment(name, num_seg, **units)
            good = [exp for exp in experiments if seg in exp['segments']]
            for g in good:
                e = SimpleInterpretedExperiment(**units)
                e.name = g['name']
                e.script = g['definition']
                e.set_auto_exposure_logging(False)

                params = e.get_params()
                res[e.name] = params
        return res

    def get_segment(self, name, num_segments, **units):
        # randomly assign primary unit to a segment
        a = Assignment(name)
        a.segment = RandomInteger(min=0, max=num_segments - 1,
                                  **units)
        return a.segment
