from planout.experiment import SimpleInterpretedExperiment
from planout.assignment import *
from storage import Storage

# Thin layer in front of planout.
class Experiments:
    def __init__(self):
        self.storage = Storage()

    # Get the parameters of a planout experiment.
    def get_experiment_params(self, experimentName, **units):
        # Attempt to get the script out of storage.  If it isn't found, the exception
        # will bubble up and get returned as a 500.
        script = self.storage.experiments[experimentName]

        # Create an experiment object with the inputs specific to the user.
        # TODO: investigate a pattern where a single experiment object is
        #       created which can generate the params using the units as input.
        e = SimpleInterpretedExperiment(**units)

        # ExperimentName is derived from the filename and must be unique as it
        # is used as a salt in hashing the inputs.
        e.name = experimentName

        # Set the deserialized json definition of the experiment to be used.
        e.script = script

        # Exposure logging is currently disabled unti a logging system can be
        # implemented.
        e.set_auto_exposure_logging(False)

        # Return the params of the experiment to the caller.
        params = e.get_params()
        return params

    def get_experiment_params_for_team(self, teamName, userId):
        teamNamespaces = self.storage.namespaces[teamName]
        retDict = {}

        for namespaceName in teamNamespaces:

            # Assign the user to a segment for this namespace
            a = Assignment(namespaceName)
            a.segment = RandomInteger(min=0,
                                    max=teamNamespaces[namespaceName]["totalSegments"] - 1,
                                    unit=userId)

            # Not all segments in a namespace will have experiment assigned to them,
            # So only get params for the user if they are given an experiment
            experimentName = teamNamespaces[namespaceName].get(a.segment, None)
            if (experimentName):
                retDict[experimentName] = self.get_experiment_params(experimentName, userId=userId)

        return retDict
