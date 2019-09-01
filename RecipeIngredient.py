from database import database

class RecipeIngredient(object):
    def __init__(self, id, amount, measure, name):
        self.id = id
        self.amount = amount
        self.measure = measure
        self.name = name

    def to_json(self):
        return {"id": self.id,
                "amount": self.amount,
                "measure": self.measure,
                "name": self.name}

if __name__ == '__main__':
    db = database.Mongo()
    print(db.db.recipes.find_one({"name":"lasagna"}))
