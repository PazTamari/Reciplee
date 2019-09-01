import json
from pymongo import MongoClient

class Mongo(object):
    def __init__(self, uri="mongodb://reciplee:reciplee1@ds245532.mlab.com:45532/reciplee",
                  db="reciplee", port=45532, user="reciplee", password="reciplee1"):

        client = MongoClient(uri, port)
        self.db = client[db]
        try:
            self.authonticate = self.db.authenticate(user, password)
        except Exception as err:
            print("could not authenticate")
            self.authonticate = False

    def get_recipe(self, recipe):
        result = self.db.recipes.find_one({"name": recipe})
        # result["_id"] = ""  # Remove _id to support recipe in flask context (could not convert to JSON with _id)
        return result

    def get_ingredient(self, ingredient_id):
        result = self.db.ingredients.find_one({"id": ingredient_id})
        return result

    def get_translated_recipe(self, recipe):
        recipe_doc = self.get_recipe(recipe)
        if not recipe_doc:
            return ""
        ingredients_list = recipe_doc.get("ingredients")
        for ingredient in ingredients_list:
            ingredient["name"] = self.db.ingredients.find_one({"id": ingredient.get("id")}).get("name")
        return recipe_doc

    def is_authonticate(self):
        if self.authonticate:
            return True
        return False

if __name__ == '__main__':
    m = Mongo()
    lasagna = m.get_translated_recipe("lasagna")
    print(lasagna)
    print(json.dumps(lasagna, sort_keys=True))
    # print(lasagna)