# Copyright 2016 Nordstrom Inc., authors, and contributors <see AUTHORS file>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import random
from bson import BSON, json_util
from pymongo import MongoClient
from abc import ABCMeta, abstractmethod

class centralStorage(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, path, **kwargs):
        #create connection to db
        pass
    
    @abstractmethod
    def add_namespace(self, database, namespace_name, group_id, num_segments):
        pass
    
    @abstractmethod
    def remove_namespace(self, database, namespace_name):
        pass
    
    @abstractmethod
    def move_namespace(self, namespace_name, initial_db, final_db):
        pass
    
    @abstractmethod
    def add_group_to_namespace(self, database, namespace_name, group_id):
        pass
    
    @abstractmethod
    def remove_group_from_namespace(self, database, namespace_name, group_id):
        pass
    
    @abstractmethod
    def add_experiment(self, database, namespace_name, exp_name, exp_num_segments, exp_definition):
        pass
    
    @abstractmethod
    def remove_experiment(self, database, namespace_name, exp_name):
        pass
    
    @abstractmethod
    def move_experiment(self, namespace_name, exp_name, initial_db, final_db):
        pass
    
class mongoStorage(centralStorage):
    __metaclass__ = ABCMeta
    
    def __init__(self, path, **kwargs):
        self.client = MongoClient(path)
        self.db = self.client.test_database
        
    def add_namespace(self, database, namespace_name, group_id, units, num_segments):
        result = self.db[database].insert_one(
            {
                "name": namespace_name,
                "group_ids": [group_id],
                "units": units,
                "num_segments": num_segments,
                "available_segments": range(num_segments),
                "experiments": []
            }
        )
        return result
    
    def remove_namespace(self, database, namespace_name):
        result = self.db[database].delete_one({"name": namespace_name})
        return result
    
    def move_namespace(self, namespace_name, initial_db, final_db):
        doc = self.db[initial_db].find_one({"name": namespace_name})
        result_insert = self.db[final_db].insert_one(doc)
        result_delete = self.db[initial_db].delete_one({"name": namespace_name})
        return [result_insert, result_delete]
    
    def add_group_to_namespace(self, database, namespace_name, group_id):
        result = self.db[database].update_one({"name": namespace_name}, {"$addToSet": {"group_ids": group_id}})
        return result
    
    def remove_group_from_namespace(self, database, namespace_name, group_id):
        result = self.db[database].update_one({"name": namespace_name}, {"$pull": {"group_ids": group_id}})
        return result
    
    def add_experiment(self, database, namespace_name, exp_name, exp_num_segments, exp_definition):
        # randomly pull segments from available segments
        doc = self.db[database].find_one({"name": namespace_name})
        # TODO: add error handling for when there aren't enough available segments
        exp_segments = random.sample(doc['available_segments'], exp_num_segments)
        
        # add experiment name and definition
        exp_result = self.db[database].update_one({"name": namespace_name}, 
             {
                 "$push": {
                 "experiments": {
                     "name": exp_name,
                     "definition": exp_definition,
                     "segments": exp_segments
                      }
                 }
             })
        
        seg_del_result = self.db[database].update_one({"name": namespace_name},
                                             {"$pullAll": {"available_segments": exp_segments}})
        
    def remove_experiment(self, database, namespace_name, exp_name):
        # TODO: fix this
        segments = [a for a in self.db[database].find_one({"name": namespace_name, "experiments.name": exp_name})['experiments'] if a == exp_name][0]['segments']
        seg_return_result = self.db[database].update_one({"namespace_name": namespace_name},
                                             {"$pushAll": {"available_segments": segments}})
        exp_remove_result = self.db[database].update_one({"namespace_name": namespace_name},
                                                   {"$unset": {exp_name: "$all"}})
        
    def move_experiment(self, namespace_name, exp_name, initial_db, final_db):
        exp_segments = self.db[initial_db].find_one({"namespace_name": namespace_name}, 
                                         {exp_name + ".segments": "$all"})[exp_name][0]['segments']
        
        release_segments = self.db[initial_db].update_one({"namespace_name": namespace_name},
                                             {"$pushAll": {"available_segments": exp_segments}})
        
        remove_fl_segments = self.db[final_db].update_one({"namespace_name": namespace_name},
                                             {"$pullAll": {"available_segments": exp_segments}})
        
        exp_definition = self.db[initial_db].find_one({"namespace_name": namespace_name}, 
                                         {exp_name + ".exp_definition": "$all"})[exp_name][0]['exp_definition']
        
        add_exp_result = self.db[final_db].update_one({"namespace_name": namespace_name}, 
                                             {"$push": {exp_name: {"exp_definition": exp_definition,
                                                                     "segments": exp_segments}}})
        
        exp_remove_result = self.db[initial_db].update_one({"namespace_name": namespace_name},
                                                   {"$unset": {exp_name: "$all"}})
