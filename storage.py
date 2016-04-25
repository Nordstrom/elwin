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

#     @abstractmethod
#     def get_param_from_exp(self, exp_id, param, **units):
#         pass

    @abstractmethod
    def get_exps_params_by_group_id(self, group_id):
        pass

class queryMongoStorage(queryCentralStorage):
    __metaclass__ = ABCMeta

    def __init__(self, path, dataset):
        self.client = MongoClient(path)
        self.db = self.client.test_database
        self.dataset = dataset

    def get_exp_params_by_exp_name(self, exp_name):
        query = self.db[self.dataset].find_one({"experiments.name": exp_name})
        return (query['name'], query['num_segments'], query['experiments'])

    def get_exps_params_by_group_id(self, group_id):
        namespaces = self.db[self.dataset].find({"group_ids": group_id})
        return [(ns['name'], ns['num_segments'], ns['experiments']) for ns in namespaces if len(ns['experiments']) > 0]
