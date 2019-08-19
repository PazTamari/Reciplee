import pymongo
from pymongo import MongoClient
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string


class Mongo(object):
    def __init__(self, uri="mongodb://reciplee:reciplee1@ds245532.mlab.com:45532/reciplee",
                  db="reciplee", port=45532, user="reciplee", password="reciplee1"):

        client = MongoClient(uri, port)
        self.db = client[db]
        try:
            self.authonticate = self.db.authenticate(user, password)
        except Exception as err:
            print("could not authonticate")
            self.authonticate = False

    def get_recipe(self, recipe):
        result = self.db.recipes.find_one({"name":recipe})
        return result

    def is_authonticate(self):
        if self.authonticate:
            return True
        return False

if __name__ == '__main__':
    m = Mongo()
    print(m.is_authonticate())
    print(m.db.recipes.find_one({"name":"lasagna"}))