import centralStorageClass

path = 'mongodb://elwin-storage:27017'

csc = centralStorageClass.mongoStorage(path)


csc.remove_namespace('test', 'epe-1')
csc.remove_namespace('test', 'epe-2')
csc.remove_namespace('test', 'loy-1')
csc.add_namespace('test', 'epe-1', 'epe', 10)
csc.add_namespace('test', 'epe-2', 'epe', 10)
csc.add_namespace('test', 'loy-1', 'loy', 10)

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
                "var": "userId"
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
                    "var": "userId"
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
     "var": "userId"
    },
    "op": "uniformChoice"
   }
  }
 ]
})

cur = csc.client.test_database.test.find()
for doc in cur:
    print(doc)
