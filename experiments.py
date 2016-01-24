from planout.experiment import SimpleInterpretedExperiment

# Thin layer in front of planout.
class Experiments:
    def __init__(self):
        # nothing right now
        pass

    # Get the parameters of a planout experiment.
    def get_experiment_params(self, experimentName, script, **units):
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
