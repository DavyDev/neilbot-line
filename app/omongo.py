from flask_pymongo import PyMongo
from random import randint

def add(db, collection, data, many=0):
    if many == 1:
        db[collection].insert_many(data)
        print('[LOG] inserted multiple documents.')
    else:
        result = db[collection].insert_one(data)
        print('[LOG] inserted document id "{}"'.format(result.inserted_id))
    return


def read(mongoid, collection):
    if collection not in mongoid.list_collection_names():
        print('[ERROR] collection "{}" doesn\'t exist!.'.format(collection))
        return 0
    else:
        for x in mongoid[collection].find():
            print(x)
        return
