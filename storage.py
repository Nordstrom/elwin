import os
import json

# Manages interactions with the storage layer.
class Storage:
    def __init__(self):
        self.useLocalStorage = True
        self.experiments = {}
        self._load_experiments()

    # Iterate through the filesystem to load all of the defined experiments.
    # TODO: Move this to S3 or DDB
    def _load_experiments(self):
        if (self.useLocalStorage):
            experimentRootFolder = "experiments"
            for teamName in os.listdir(experimentRootFolder):
                teamFolder = experimentRootFolder + "/" + teamName
                for exp in os.listdir(teamFolder):
                    name = exp.split(".")[0]
                    script = json.loads(open(teamFolder + "/" + exp).read())
                    self.experiments[name] = script

    # Return the requested experiment definition from the store.
    def get_experiment_def(self, experimentName):
        return self.experiments.get(experimentName, None)
