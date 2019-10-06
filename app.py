# import flask dependencies
from flask import Flask
from database import database
from flask_assistant import context_manager
from flask_assistant import Assistant, tell, ask
from random import choice
import json
import logging
import SpoonacularUtils

logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

FIRST_STEP = 0
LIFESPAN = 100
AWESOME_LIST = ["Awesome", "Great", "Wonderful", "What a"]
RECIPES_TO_PULL = 15
DEFAULT_OFFSET = 0


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.mongo = database.Mongo()


# initialize the flask app
app = FlaskApp(__name__)
assist = Assistant(app, route='/', project_id="reciplee-iubkfl")
ingredient_string_template = "Ok you need {amount} {measure} of {name}\n"

def handle_recipes(recipes, participants, recipe_name):

    context_manager.add("make-food", lifespan=LIFESPAN)
    context_manager.set("make-food", "recipes", recipes)
    context_manager.set("make-food", "current_recipe_index", -1)
    context_manager.set("make-food", "participants", participants)
    context_manager.set("make-food", "recipe_name", recipe_name)

    return choose_another()

@assist.action('get-recipes-by-ingredients')
def get_recipes_by_ingredients(ingredients, participants):
    print("with ingredients")
    recipes = SpoonacularUtils.get_recipes_by_ingridients(ingredients, RECIPES_TO_PULL)
    if len(recipes) == 0:
        context_manager.clear_all()
        return tell(recipe_not_exist("with {} ".format(','.join(ingredients))))
    return handle_recipes(recipes, participants, ingredients[0])

@assist.action('get-recipes')
def get_recipes(participants, recipe, diet=None, excludeIngredients=None, intolerances=None, type=None):
    recipes = SpoonacularUtils.get_recipes(diet, excludeIngredients, intolerances, RECIPES_TO_PULL, DEFAULT_OFFSET,
                                              type, recipe)
    if len(recipes) == 0:
        context_manager.clear_all()
        return tell(recipe_not_exist("for {} ".format(recipe)))
    return handle_recipes(recipes, participants, recipe)


@assist.action('next-step - no')
def finish():
    context_manager.clear_all()
    return tell("Have a {} day!".format(choice(AWESOME_LIST)))

@assist.action('get-recipe.choose-current')
def choose_current():
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index'))
    recipe_id = int(recipes[current_recipe]['id'])
    recipe_info_response = SpoonacularUtils.get_recipe_information(recipe_id)
    recipe_info = json.loads(r'' + recipe_info_response.text + '')
    context_manager.set("make-food", "chosen_recipe", recipe_info)

    amount_coefficient = get_amount_coefficient(recipe_info['servings'], context.parameters.get('participants'))
    # steps = re.split('[;.]', recipe_info['instructions'])
    print(recipe_id)
    steps_response = SpoonacularUtils.get_steps(recipe_id)
    context_manager.set("make-food", "recipe_steps", steps_response.text)

    speech = "{random} choice! We found a recipe for {recipe}. The ingredients are: {ingredients}." \
                 " Do you want to start making it?".format(
            random=choice(AWESOME_LIST),
            recipe=recipes[current_recipe]['title'],
            ingredients=get_ingredients_to_speech(recipe_info['extendedIngredients'], amount_coefficient))

    return ask(speech)

@assist.action('get-recipe.choose-another')
def choose_another():
    context = context_manager.get('make-food')
    recipes = context.parameters.get('recipes')
    current_recipe = int(context.parameters.get('current_recipe_index') + 1)
    context_manager.set("make-food", "current_recipe_index", current_recipe)
    recipe_id = int(recipes[current_recipe]['id'])
    if len(recipes) <= current_recipe + 1:
        return tell("Sorry but I don't have any more recipes to make, please ask for another recipe")

    # RECIPE WITH 2 STEPS SECTIONS: recipe_id = 324694
    if not is_recipe_has_single_step_section(recipe_id):
        return choose_another()

    speech = "Do you want to make {choice}?".format(choice=recipes[current_recipe]['title'])
    return ask(speech)

@assist.action('get-recipe.choose-current - yes')
def start_recipe():
    context_manager.set("make-food", "current_step", FIRST_STEP)
    return repeat_step()

@assist.action('next-step')
def next_step():
    try:
        return get_step(int(get_current_step() + 1))
    except:
        return tell("We encountered a problem, please ask for recipe again")

@assist.action('previous-step')
def previous_step():
    try:
        return get_step((get_current_step() - 1))
    except:
        return tell("We encountered a problem, please ask for recipe again")

@assist.action('repeat-step')
def repeat_step():
    try:
        return get_step(int(get_current_step()))
    except:
        return tell("We encountered a problem, please ask for recipe again")

@assist.action('wine-recommendation')
def wine_recommendation():
    context = context_manager.get('make-food')
    chosen_recipe = context.parameters.get('chosen_recipe')
    wine_response = SpoonacularUtils.get_wine(chosen_recipe)
    try:
        wine = json.loads(r'' + wine_response.text + '')['pairedWines'][0]
        if not wine:
            wine = "pinot noir"

    except:
        wine = 'gruener veltliner'
    return tell("{} will be perfect".format(wine))


def get_step(step_number):
    print("The step number to get is {}".format(step_number))
    context = context_manager.get('make-food')
    requested_step = step_number
    steps = json.loads(str(context.parameters.get('recipe_steps')))
    if int(requested_step) >= len(steps[0].get("steps")):
        # no more steps
        speech = "You finished the recipe! bonappetit. Can I help with anything else?"
        return ask(speech)
    if int(requested_step) < 0:
        requested_step = requested_step + 1

    context_manager.set('make-food', 'current_step', int(requested_step))
    pre_speach = ""
    if int(requested_step) == 0:
        pre_speach = "I will now tell you how to make this recipe. " \
                     "You can ask for the next, previous or current step. Let's start with the first step! \n"

    return ask(pre_speach + steps[0].get("steps")[int(requested_step)].get("step"))


def get_amount_coefficient(recipe_servings, requested_servings):
    return requested_servings/recipe_servings

def is_recipe_has_single_step_section(recipe_id):
    steps_response = SpoonacularUtils.get_steps(recipe_id)
    steps_list = eval(steps_response.text)
    if len(steps_list) == 1:
        return True
    return False

def fix_amount(amount, participants):
    new_amount = amount * participants
    return int(new_amount) if float(new_amount).is_integer() else str(round(new_amount, 2))

def get_current_step():
    context = context_manager.get('make-food')
    current_step = context.parameters.get('current_step')
    return current_step

def get_ingredients_to_speech(ingredients, amount_coefficient):
    last_ingredient = ingredients[-1]
    txt = ""
    for ingredient in ingredients:
        if ingredient['name'] == last_ingredient['name']:
            txt = txt[0:-2] + " and {amount} {measure} of {name}".format(
                amount=round(ingredient['amount'] * amount_coefficient, 2),
                measure=ingredient['unit'],
                name=ingredient['name'])
        else:
            txt = txt + "{amount} {measure} of {name}, ".format(
                amount=round(ingredient['amount'] * amount_coefficient, 2),
                measure=ingredient['unit'],
                name=ingredient['name'])
    return txt


def recipe_not_exist(recipe):
    return "Could not find a recipe for {}. Please search for a different recipe?".format(recipe)

def recipe_not_exist(recipe):
    return "Could not find a recipe {}. Please search for a different recipe?".format(recipe)

# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
