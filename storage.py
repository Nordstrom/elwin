import json
from bson import BSON, json_util
from pymongo import MongoClient
from abc import ABCMeta, abstractmethod


class queryCentralStorage(object):
    __metaclass__ = ABCMeta

    def __init__(self, path, dataset):
        #create connection to db
        pass

    @abstractmethod
    def get_exp_params_by_exp_name(self, exp_name):
        pass

    @abstractmethod
    def get_exps_params_by_group_id(self, group_id):
        pass


'''
queryMongoStorage uses pymongo client to retreive the params

data format:
    Namespace {
        name               string
        group_ids          []string
        num_segments       int
        available_segments []int
        experiments        []Experiment
    }
    Experiment {
        name       string
        definition string
        segments   []int
    }
'''


class queryMongoStorage(queryCentralStorage):
    __metaclass__ = ABCMeta

    def __init__(self, path, dataset):
        self.client = MongoClient(path)
        self.db = self.client.test_database
        self.dataset = dataset

    def get_exp_params_by_exp_name(self, team_name, exp_name):
        query = self.db[self.dataset].find_one({"group_ids": team_name, "experiments.name": exp_name})
        return (query['name'], query['num_segments'], query['experiments'])

    def get_exps_params_by_group_id(self, group_id):
        namespaces = self.db[self.dataset].find({"group_ids": group_id})
        return ((ns['name'], ns['num_segments'], ns['experiments'])
                for ns in namespaces if ns['experiments'])
