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
    def get_exps_params_by_group_id(self, group_id, unit_type):
        pass


'''
queryMongoStorage uses pymongo client to retreive the params

data format:
    Namespace {
        name               string
        group_ids          []string
        units              []string
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
        # TODO(andrew.oneill@nordstrom.com): make mongo config env vars
        self.db = self.client.test_database
        self.dataset = dataset

    def get_exp_params_by_exp_name(self, exp_name):
        pass

    def get_exps_params_by_group_id(self, group_id, unit_type):
        namespaces = self.db[self.dataset].find({
            "group_ids": group_id,
            "units": {
                "$not": {
                    "$elemMatch": {
                        "$nin": unit_type
                        }
                    }
                }
            })
        return (ns for ns in namespaces if ns['experiments'])
