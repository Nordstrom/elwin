from planout.experiment import SimpleInterpretedExperiment

class Experiments:
    def __init__(self):
        # nothing right now
        pass

    def get_experiment_params(self, experimentName, script, **units):
        print "getting params"
        e = SimpleInterpretedExperiment(**units) # this allows us to create an expermeint object from a json definition
        e.name = experimentName # give it a name, this is used in hashing so these need to be unique
        e.script = script # will pull in the json definition here
        e.set_auto_exposure_logging(False)
        params = e.get_params()
        print "returning: " + str(params)
        return params
