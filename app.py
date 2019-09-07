# import flask dependencies
from flask import Flask
from database import database
from flask_assistant import context_manager
from flask_assistant import Assistant, tell, ask, event
from Recipe import Recipe
from random import choice
import json
import requests
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
def get_recipe(recipe, participants, diet=None, excludeIngredients=None, intolerances=None, type=None):
    # print(app.mongo.get_ingredient(1))
    recipe_doc = app.mongo.get_translated_recipe(recipe)
    # final = participants/recipe_doc['amount']
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"

    querystring = {"diet": diet, "excludeIngredients": excludeIngredients, "intolerances": intolerances, "number": "10",
                   "offset": "0", "type": type, "query": recipe}

    headers = {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': "0337527ffemsh1130c076beb971dp149cd5jsn1ec4dfe855bd"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    recipes = json.loads(r'' + response.text + '')['results']
    context_manager.add("make-food", lifespan=10)

    if len(recipes) == 0:
        context_manager.clear_all()
        return tell(recipe_not_exist(recipe))
    # recipeObj = Recipe(recipe_doc, participants)
    context_manager.add("make-food", lifespan=LIFESPAN)
    context_manager.set("make-food", "recipes", recipes)
    context_manager.set("make-food", "current_recipe_index", 0)
    # context_manager.set("make-food", "recipe", recipe)
    # context_manager.set("make-food", "next_step", FIRST_STEP)
    context_manager.set("make-food", "participants", participants)

    speech = "What a {choice} sounds like?".format(choice=recipes[0]['title'])
    # speech = "{random} choice! We found a recipe for {recipe}. The ingredients are: {ingredients}." \
    #         " Do you want to start making it?".format(
    #    random=choice(AWESOME_LIST),
    #    recipe=recipe,
    #    ingredients=get_ingredients_to_speech(recipeObj))
    return ask(speech)


@assist.action('get-recipe - yes')
def choose_current():
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index'))
    recipe_id = int(recipes[current_recipe]['id'])
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/ingredientWidget.json".format(id=recipe_id)

    headers = {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': "0337527ffemsh1130c076beb971dp149cd5jsn1ec4dfe855bd"
    }

    ingredients_response = requests.request("GET", url, headers=headers)

    context_manager.set("make-food", "next_step", FIRST_STEP)

    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/324694/analyzedInstructions"

    querystring = {"stepBreakdown": "false"}

    headers = {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': "0337527ffemsh1130c076beb971dp149cd5jsn1ec4dfe855bd"
    }

    steps_response = requests.request("GET", url, headers=headers, params=querystring)
    context_manager.set("make-food", "recipe_steps", eval(steps_response.text))
    speech = "{random} choice! We found a recipe for {recipe}. The ingredients are: {ingredients}." \
             " Do you want to start making it?".format(
        random=choice(AWESOME_LIST),
        recipe=recipes[current_recipe]['title'],
        ingredients=get_ingredients_to_speech(eval(ingredients_response.text)['ingredients']))
    return ask(speech)

@assist.action('get-recipe - yes - yes')
def next_step():
    context = context_manager.get('make-food')
    try:
        next_step = context.parameters.get('next_step')
    except Exception:
        speech = "Hold your horses! please ask for a recipe first. Please try something like how to make lasagna for 2 people?"
        return tell(speech)
    # recipe_doc = app.mongo.get_recipe(context.parameters.get('recipe'))
    steps = context.get('recipe_steps')
    print(steps)
    #if int(next_step) >= len(recipe_doc.get("steps")):
    #    # no more steps
    #    speech = "You finished the recipe! bonappetit"
    #    context_manager.clear_all()
    #    return tell(speech)

    #speech = recipe_doc.get('steps')[int(next_step)].get('description')
    #context_manager.set('make-food', 'next_step', int(next_step) + 1)
    #return tell(speech)

@assist.action('get-recipe - no')
def choose_another():
    # print(app.mongo.get_ingredient(1))
    # recipe_doc = app.mongo.get_translated_recipe(recipe)
    # print(recipe_doc)
    # final = participants/recipe_doc['amount']
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index') + 1)
    if len(recipes) <= current_recipe:
        return tell("I don't have another recepies")

    context_manager.set("make-food", "current_recipe_index", current_recipe)
    speech = "What a {choice} sounds like?".format(choice=recipes[current_recipe]['title'])
    return ask(speech)

def get_ingredients_to_speech(ingredients):
    last_ingredient = ingredients[-1]
    txt = ""

    for ingredient in ingredients:
        if ingredient['name'] == last_ingredient['name']:
            txt = txt[0:-2] + " and {amount} {measure} of {name}".format(amount=ingredient['amount']['metric']['value'],
                                                                         measure=ingredient['amount']['metric']['unit'],
                                                                         name=ingredient['name'])
        else:
            txt = txt + "{amount} {measure} of {name}, ".format(amount=ingredient['amount']['metric']['value'],
                                                                measure=ingredient['amount']['metric']['unit'],
                                                                name=ingredient['name'])
    return txt


def recipe_not_exist(recipe):
    return "Could not find a recipe for {}. Please search for a different recipe?".format(recipe)


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
