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

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.mongo = database.Mongo()

# initialize the flask app
app = FlaskApp(__name__)
assist = Assistant(app, route='/')
ingredient_string_template = "Ok you need {amount} {measure} of {name}\n"

AWESOME_LIST = ["Awesome", "Great", "Wonderful", "What a"]
@assist.action('get-recipe')
def get_recipe(recipe, participants):
    print(app.mongo.get_ingredient(1))
    recipeDoc = app.mongo.get_recipe(recipe)
    print(recipeDoc)
    #final = participants/recipeDoc['amount']

    context_manager.add("make-food", lifespan=10)
    first_step = 0
    if recipeDoc:
        context_manager.set("make-food", "recipe", recipe)
        context_manager.set("make-food", "step", first_step)
        context_manager.set("make-food", "participants", participants)
        speech = ""
        for i in recipeDoc['ingredients']:
            print(get_ingredient_string(i))
            speech = speech.join(get_ingredient_string(i))
            print(speech)

        print(speech)
        return tell(speech)
    else:
        speech = "Could not find a recipe for {}. Do you want to search different recipe?".format(recipe)
        return ask(speech)
    recipe = Recipe(recipe_doc)
    context_manager.add("make-food", lifespan=LIFESPAN)
    context_manager.set("make-food", "recipe", json.dumps(recipe_doc))
    context_manager.set("make-food", "step", FIRST_STEP)


    speech = "{random} choice! We found {recipe}".format(random=choice(AWESOME_LIST), recipe=recipe)
    return tell(speech)


@assist.action('next-step')
def next_step():
    context = context_manager.get('make-food')
    current_step = context.parameters['step']
    recipeDoc = app.mongo.get_recipe(context.parameters['recipe'])
    print(recipeDoc)
    if recipeDoc:
        speech = recipeDoc['steps'][int(current_step)]['description']
        context_manager.set('make-food', 'step', int(current_step) + 1)
        return tell(speech)
    else:
        speech = "Could not find a recipe for {}. Do you want to search different recipe?".format(context.parameters['recipe'])
        return ask(speech)
    recipe_doc = json.loads(recipe_context)
    speech = str(recipe_doc.get("steps")[int(current_step)].get('description'))
    context_manager.set('make-food', 'step', int(current_step) + 1)
    return tell(speech)

def get_ingredient_string(ingredient):
    return (ingredient_string_template .format(amount=ingredient['amount'],measure=ingredient['measure'],name=app.mongo.get_ingredient(ingredient['id'])['name']))




# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
