import json
from bson import BSON, json_util
from pymongo import MongoClient
from abc import ABCMeta, abstractmethod
from planout.experiment import SimpleInterpretedExperiment
from planout.assignment import *


class queryCentralStorage(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, path, **units):
        #create connection to db
        pass
    
    @abstractmethod
    def get_exp_params_by_exp_name(self, exp_name, **units):
        pass
    
#     @abstractmethod
#     def get_param_from_exp(self, exp_id, param, **units):
#         pass
    
    @abstractmethod
    def get_exps_params_by_group_id(self, dataset, group_id, units):
        pass
    
class queryMongoStorage(queryCentralStorage):
    __metaclass__ = ABCMeta
    
    def __init__(self, path, **units):
        self.client = MongoClient(path)
        self.db = self.client.test_database
        
    def get_exp_params_by_exp_name(self, database, exp_name, **units):
        
        exp_definition = self.db[database].find_one({"exp_names": exp_name}, 
                                         {exp_name + ".exp_definition": "$all"})[exp_name][0]['exp_definition']
        
        e = SimpleInterpretedExperiment(units)
        e.name = exp_name
        e.script = exp_definition
        e.set_auto_exposure_logging(False)
        
        params = e.get_params()
        return params
        
    def get_exps_params_by_group_id(self, dataset, group_id, units):
        namespaces = self.db[dataset].find({"group_ids": group_id})
        exps = [(ns['name'], ns['num_segments'], ns['experiments']) for ns in namespaces if len(ns['experiments']) > 0]
        res = []
        for name, num_seg, es in exps:
            seg = self.get_segment(name, num_seg, units)
            good = [e for e in es if seg in e['segments']]
            for g in good: 
                e = SimpleInterpretedExperiment(unit=units)
                e.name = g['name']
                e.script = g['definition']
                e.set_auto_exposure_logging(False)
                
                params = e.get_params()
                res.append((e.name, params))
        return res

    def get_segment(self, name, num_segments, unit):
        # randomly assign primary unit to a segment
        a = Assignment(name)
        a.segment = RandomInteger(min=0, max=num_segments - 1,
                                  unit = unit)
        return a.segment

'''
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
'''
