import os
import json

class Storage:
    def __init__(self):
        print "creating storage"
        self.useLocalStorage = True
        self.experiments = {}
        self._load_experiments()

    def _load_experiments(self):
        print "loading experiments"
        if (self.useLocalStorage):
            experimentRootFolder = "experiments"
            for teamName in os.listdir(experimentRootFolder): #read in the experiment definitions, maybe store these in dynamo or something
                teamFolder = experimentRootFolder + "/" + teamName
                for exp in os.listdir(teamFolder):
                    name = exp.split(".")[0]
                    script = json.loads(open(teamFolder + "/" + exp).read())
                    self.experiments[name] = script

    def get_experiment_def(self, experimentName):
        print "getting experiment: " + experimentName
        return self.experiments.get(experimentName, None)
