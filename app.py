# import flask dependencies
from flask import Flask
from database import database
from flask_assistant import context_manager
from flask_assistant import Assistant, tell, ask
from Recipe import Recipe
from random import choice
import json

import logging
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

FIRST_STEP = 0
LIFESPAN = 100
AWESOME_LIST = ["Awesome", "Great", "Wonderful", "What a"]

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.mongo = database.Mongo()

# initialize the flask app
app = FlaskApp(__name__)
assist = Assistant(app, route='/')
ingredient_string_template = "Ok you need {amount} {measure} of {name}\n"

@assist.action('get-recipe')
def get_recipe(recipe, participants):
    # print(app.mongo.get_ingredient(1))
    recipe_doc = app.mongo.get_translated_recipe(recipe)
    # print(recipe_doc)
    # final = participants/recipe_doc['amount']

    context_manager.add("make-food", lifespan=10)

    if not recipe_doc:
        speech = "Could not find a recipe for {}. Do you want to search different recipe?".format(recipe)
        return ask(speech)
    recipeObj = Recipe(recipe_doc, participants)
    context_manager.add("make-food", lifespan=LIFESPAN)
    context_manager.set("make-food", "recipe", recipe)
    context_manager.set("make-food", "step", FIRST_STEP)
    context_manager.set("make-food", "participants", participants)

    speech = "{random} choice! We found a recipe for {recipe}. The ingredients are: {ingredients}".format(
        random=choice(AWESOME_LIST),
        recipe=recipe,
        ingredients=get_ingredients_to_speech(recipeObj))
    return tell(speech)

def get_ingredients_to_speech(recipeObj):
    last_ingredient = recipeObj.ingredients[-1]
    txt = ""
    # print (recipeObj.ingredients)
    for ingredient in recipeObj.ingredients:
        if ingredient.name == last_ingredient.name:
            txt = txt[0:-2] + " and {amount} {measure} of {name}".format(amount=ingredient.amount,
                                                                         measure=ingredient.measure,
                                                                         name=ingredient.name)
        else:
            txt = txt + "{amount} {measure} of {name}, ".format(amount=ingredient.amount,
                                                                measure=ingredient.measure,
                                                                name=ingredient.name)
    return txt

@assist.action('next-step')
def next_step():
    context = context_manager.get('make-food')
    current_step = context.parameters['step']
    recipe_doc = app.mongo.get_recipe(context.parameters['recipe'])
    print(recipe_doc)
    if recipe_doc:
        speech = recipe_doc['steps'][int(current_step)]['description']
        context_manager.set('make-food', 'step', int(current_step) + 1)
        return tell(speech)
    else:
        speech = "Could not find a recipe for {}. Do you want to search different recipe?".format(context.parameters['recipe'])
        return ask(speech)
    recipe_doc = json.loads(recipe_context)
    speech = str(recipe_doc.get("steps")[int(current_step)].get('description'))
    context_manager.set('make-food', 'step', int(current_step) + 1)
    return tell(speech)


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
