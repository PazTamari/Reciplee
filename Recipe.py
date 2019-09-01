from database import database
from RecipeIngredient import RecipeIngredient

class Recipe(object):
    def __init__(self, recipe_doc, participants):
        self.recipe_doc = recipe_doc
        self.name = recipe_doc.get("name")
        self.amount = participants
        self.ingredients = self.get_list_of_ingredients(recipe_doc.get("ingredients"), participants)

    def get_list_of_ingredients(self, ingredients_doc, participants):
        ingredients_list = []
        for ingredient in ingredients_doc:
            new_amount = self.fix_amount(ingredient.get("amount"), participants)
            new_measure = self.fix_measure(ingredient.get("measure"), new_amount)
            ingredients_list.append(RecipeIngredient(ingredient.get("id"), new_amount, new_measure,
                                                     ingredient.get("name")))
        return ingredients_list

    @staticmethod
    def fix_amount(amount, participants):
        new_amount = amount * participants
        return int(new_amount) if float(new_amount).is_integer() else new_amount

    @staticmethod
    def fix_measure(measure, amount):
        if amount > 1:
            return measure+"s"
        return measure

    def list_of_ingredients_to_json(self):
        res = []
        for ingredient in self.ingredients:
            res.append(ingredient.to_json())

    def __str__(self):
        return  "{name} recipe for {amount} people, including {ingredients}".format(name=self.name, amount=self.amount,
                                                                                    ingredients=self.ingredient_list())
    def ingredient_list(self):
        txt = ""
        for ingredient in self.ingredients:
            txt = txt + "{amount} {measure} of {name}, ".format(amount=ingredient.amount,
                                                                measure=ingredient.measure,
                                                                name=ingredient.name)
        li = txt.rsplit(",", 1)
        return " and ".join(li)

    def to_json(self):
        return {"name": self.name,
                "amount": self.amount,
                "ingredient": self.list_of_ingredients_to_json()
                }

if __name__ == '__main__':
    db = database.Mongo()
    lasagna = db.get_translated_recipe("lasagna")
    r = Recipe(lasagna)
    print(r)
