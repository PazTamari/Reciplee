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
import SpoonacularUtils


logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

FIRST_STEP = 0
LIFESPAN = 100
AWESOME_LIST = ["Awesome", "Great", "Wonderful", "What a"]
RECIPES_TO_PULL = 10
DEFAULT_OFFSET = 0


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.mongo = database.Mongo()


# initialize the flask app
app = FlaskApp(__name__)
assist = Assistant(app, route='/', project_id="reciplee-iubkfl")
ingredient_string_template = "Ok you need {amount} {measure} of {name}\n"

@assist.action('get-recipes')
def get_recipes(recipe, participants, diet=None, excludeIngredients=None, intolerances=None, type=None):
    # print(app.mongo.get_ingredient(1))
    # recipe_doc = app.mongo.get_translated_recipe(recipe)
    # final = participants/recipe_doc['amount']

    recipes = SpoonacularUtils.get_recipes(diet, excludeIngredients, intolerances, RECIPES_TO_PULL, DEFAULT_OFFSET,
                                              type, recipe)

    if len(recipes) == 0:
        context_manager.clear_all()
        return tell(recipe_not_exist(recipe))

    context_manager.add("make-food", lifespan=LIFESPAN)
    context_manager.set("make-food", "recipes", recipes)
    context_manager.set("make-food", "current_recipe_index", -1)
    context_manager.set("make-food", "participants", participants)

    return choose_another()


@assist.action('get-recipe.choose-current')
def choose_current():
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index'))
    recipe_id = int(recipes[current_recipe]['id'])

    ingredients_response = SpoonacularUtils.get_ingredients(recipe_id)
    steps_response = SpoonacularUtils.get_steps(recipe_id)

    context_manager.set("make-food", "recipe_steps", steps_response.text)
    speech = "{random} choice! We found a recipe for {recipe}. The ingredients are: {ingredients}." \
             " Do you want to start making it?".format(
        random=choice(AWESOME_LIST),
        recipe=recipes[current_recipe]['title'],
        ingredients=get_ingredients_to_speech(eval(ingredients_response.text)['ingredients']))
    return ask(speech)

@assist.action('get-recipe.choose-another')
def choose_another():
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index') + 1)
    context_manager.set("make-food", "current_recipe_index", current_recipe)
    recipe_id = int(recipes[current_recipe]['id'])
    print (len(recipes))
    print(current_recipe)

    if len(recipes) <= current_recipe + 1:
        return tell("Sorry but I don't have any more recipes to make, please ask for another recipe")

    # RECIPE WITH 2 STEPS SECTIONS: recipe_id = 324694
    if not is_recipe_has_single_step_section(recipe_id):
        choose_another()

    context_manager.set("make-food", "current_recipe_index", current_recipe)
    speech = "Do you want to make {choice}?".format(choice=recipes[current_recipe]['title'])
    return ask(speech)

@assist.action('get-recipe.choose-current - yes')
def start_recipe():
    context_manager.set("make-food", "next_step", FIRST_STEP)
    return next_step()

@assist.action('next-step')
def next_step():
    context = context_manager.get('make-food')
    next_step = get_next_step()
    steps = json.loads(str(context.parameters.get('recipe_steps')))

    if int(next_step) >= len(steps[0].get("steps")):
       # no more steps
       speech = "You finished the recipe! bonappetit"
       context_manager.clear_all()
       return tell(speech)

    context_manager.set('make-food', 'next_step', int(next_step) + 1)
    pre_speach = ""
    if int(next_step) == 0:
        pre_speach = "Now, I will now tell you how to make this recipe. " \
                     "You can ask for the next, previous or current step. Let's start with the first step! \n"
    print (int(next_step))
    return tell(pre_speach + steps[0].get("steps")[int(next_step)].get("step"))

@assist.action('previous-step')
def previous_step():
    context = context_manager.get('make-food')
    next_step = get_next_step()

    if next_step == 1:
        return repeat_step()

    steps = json.loads(str(context.parameters.get('recipe_steps')))
    context_manager.set('make-food', 'next_step', int(next_step) - 1)
    return tell(steps[0].get("steps")[int(next_step - 2)].get("step"))



@assist.action('repeat-step')
def repeat_step():
    # TODO: make repeat step
    return next_step()

def is_recipe_has_single_step_section(recipe_id):
    steps_response = SpoonacularUtils.get_steps(recipe_id)
    steps_list = eval(steps_response.text)
    if len(steps_list) == 1:
        return True
    return False

#  TRY TO CLEAR CONTEXT
# @assist.action('clear-contex')
# def clear_contex():
#     context = context_manager.get('make-food')
#     print(dir(context))
#     context.lifespan=0
#     context_manager.update([{"name":"/contexts/make-food"}])
#
#     context = context_manager.add('test_clean')
#
#     # context.lifespan = 0
#     # context_manager.clear_all()
#     if context != None:
#         return tell("exist!")
#     else:
#         return tell("not exist")





@assist.action('get-recipe - yes - yes - more')
def more():
    context_manager.set('make-food', 'next_step', int(get_next_step()) + 1)
    return next_step()





def get_next_step():
    context = context_manager.get('make-food')
    try:
        next_step = context.parameters.get('next_step')
    except Exception:
        speech = "Hold your horses! please ask for a recipe first. Please try something like how to make lasagna for 2 people?"
        return tell(speech)
    return next_step

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
