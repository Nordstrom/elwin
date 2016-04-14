import os
import json
from planout.ops.random import *
from planout.assignment import *

# Manages interactions with the storage layer.
class Storage:
    def __init__(self):
        self.namespaces = {}
        self.experiments = {}
        self._load_namespaces()
        self._load_experiments()

    # Iterate through the defined namespaces and load the corresponding data
    # into a hash table.
    def _load_namespaces(self):
        namespaceRoot = "namespaces"
        for namespace in os.listdir(namespaceRoot):

            # Files have the format <teamName>_<namespaceName>.json
            fileName = namespace.split(".")[0]
            teamName = fileName.split("_")[0]
            namespaceName = fileName.split("_")[1]

            namespaceData = json.loads(open(namespaceRoot + "/" + namespace).read())

            # Get or create an entry for the team for easier access
            teamNamespaces = self.namespaces.get(teamName, None)
            if (teamNamespaces == None):
                teamNamespaces = self.namespaces[teamName] = {}

            # Save the total number of segments to be used when hashing
            namespaceEntry = teamNamespaces[namespaceName] = {}
            namespaceEntry["totalSegments"] = namespaceData["segments"]

            availableSegments = range(namespaceData["segments"])
            for experimentOp in namespaceData["experimentOps"]:

                # Sample the available segments and assign the experiment to them.
                # This is done randomly but deterministically using a hash function
                # which makes it repeatable.
                if (experimentOp["op"] == "add"):
                    assignment = Assignment(namespaceName)
                    assignment.sampled_segments = Sample(choices=availableSegments,
                               draws=experimentOp["numSegments"],
                               unit=experimentOp["experimentName"])

                    for segment in assignment.sampled_segments:
                        namespaceEntry[segment] = experimentOp["experimentName"]
                        availableSegments.remove(segment)

                # Reset all entries for the experiment to be removed and add the
                # segment back into the pool of available segments.  Finally,
                # sort the list of segments to return to the original state.
                elif (experimentOp["op"] == "remove"):
                    for segment in namespaceEntry:
                        if (namespaceEntry[segment] == experimentOp["experimentName"]):
                            namespaceEntry[segment] = ""
                            availableSegments.append(segment)

                    availableSegments.sort()

    # Iterate through the filesystem to load all of the defined experiments.
    # TODO: Move this to S3 or DDB
    def _load_experiments(self):
        experimentRootFolder = "experiments"
        for teamName in os.listdir(experimentRootFolder):
            teamFolder = experimentRootFolder + "/" + teamName
            for exp in os.listdir(teamFolder):
                name = exp.split(".")[0]
                script = json.loads(open(teamFolder + "/" + exp).read())
                self.experiments[name] = script
