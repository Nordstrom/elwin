import os
import json
from planout.ops.random import *
from planout.assignment import *

# Manages interactions with the storage layer.
class Storage:
    def __init__(self):
        self.useLocalStorage = True
        self.namespaces = {}
        self.experiments = {}
        self._load_namespaces()
        self._load_experiments()

    def _load_namespaces(self):
        if (self.useLocalStorage):
            namespaceRoot = "namespaces"
            for namespace in os.listdir(namespaceRoot):
                fileName = namespace.split(".")[0]
                teamName = fileName.split("_")[0]
                namespaceName = fileName.split("_")[1]

                namespaceData = json.loads(open(namespaceRoot + "/" + namespace).read())

                self.namespaces[teamName] = {}
                namespaceEntry = self.namespaces[teamName][namespaceName] = {}
                namespaceEntry["totalSegments"] = namespaceData["segments"]

                availableSegments = range(namespaceData["segments"])
                for experimentOp in namespaceData["experimentOps"]:
                    if (experimentOp["op"] == "add"):
                        assignment = Assignment(namespaceName)
                        assignment.sampled_segments = Sample(choices=availableSegments,
                                   draws=experimentOp["numSegments"],
                                   unit=experimentOp["experimentName"])

                        # assign each segment to the experiment name
                        for segment in assignment.sampled_segments:
                            namespaceEntry[segment] = experimentOp["experimentName"]
                            availableSegments.remove(segment)

            print self.namespaces

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

            print self.experiments
