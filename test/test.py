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

import centralStorageClass
import os

path = os.getenv('DB_CONN', 'mongodb://elwin-storage:27017')

csc = centralStorageClass.mongoStorage(path)

csc.db['test'].remove({})

csc.add_namespace('test', 'epe-1', 'epe', ['userid'], 10)
csc.add_namespace('test', 'epe-2', 'epe', ['userid', 'test'], 10)
csc.add_namespace('test', 'loy-1', 'loy', ['userid'], 10)
csc.add_namespace('test', 'snb-1', 'search', ['userid'], 1000)

csc.add_experiment('test', 'snb-1', 'searchResultTest', 1000, {
    "op": "seq",
    "seq": [
        {
            "op": "set",
            "value": {
                "choices": {
                    "op": "array",
                    "values": [
                        99,
                        66,
                        45,
                        33
                    ]
                },
                "op": "uniformChoice",
                "unit": {
                    "op": "get",
                    "var": "unit"
                }
            },
            "var": "resultCount"
        }
    ]
})
csc.add_experiment('test', 'epe-1', 'imageTest', 10, {
    "op": "seq",
    "seq": [
        {
            "op": "set",
            "var": "version",
            "value": {
                "choices": {
                    "op": "array",
                    "values": [
                        "availabilityInfo"
                    ]
                },
                "unit": {
                    "op": "get",
                    "var": "unit"
                },
                "op": "uniformChoice"
            }
        }
    ]
})

csc.add_experiment('test', 'epe-2', 'colorTest', 8, {
    "op": "seq",
    "seq": [
        {
            "op": "set",
            "var": "colorSwatchTest",
            "value": {
                "choices": {
                    "op": "array",
                    "values": [
                        "control",
                        "circle"
                    ]
                },
                "unit": {
                    "op": "get",
                    "var": "unit"
                },
                "op": "uniformChoice"
            }
        }
    ]
})

csc.add_experiment('test', 'loy-1', 'checkoutTest', 10, {
    "op": "seq",
    "seq": [
        {
            "op": "set",
            "var": "nontenderCheckoutCopy",
            "value": {
                "choices": {
                    "op": "array",
                    "values": [
                        "Control",
                        "var1",
                        "var2"
                    ]
                },
                "unit": {
                    "op": "get",
                    "var": "unit"
                },
                "op": "uniformChoice"
            }
        }
    ]
})

cur = csc.client.test_database.test.find()
for doc in cur:
    print(doc)
