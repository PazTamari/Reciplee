import requests
import json
INFORMATION_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/information"
SEARCH_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
INGREDIENTS_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/ingredientWidget.json"
STEPS_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/analyzedInstructions"
HEADERS = {
    'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
    'x-rapidapi-key': "0337527ffemsh1130c076beb971dp149cd5jsn1ec4dfe855bd"
}

def send_request(method, url, headers, querystring):
    return requests.request(method, url, headers=headers, params=querystring)

def get_recipes(diet, excludeIngredients, intolerances, number, offset, type, recipe):
    querystring = {"diet": diet, "excludeIngredients": excludeIngredients, "intolerances": intolerances, "number": number,
                   "offset": offset, "type": type, "query": recipe}
    response = send_request("GET", SEARCH_URL, HEADERS, querystring)
    return json.loads(r'' + response.text + '')['results']
def get_recipes_by_ingridients(ingridients):
    querystring = {"number":"10","ranking":"1","ignorePantry":"false","ingredients":','.join(ingridients)}
    response = send_request("GET", SEARCH_URL, HEADERS, querystring)
    return json.loads(r'' + response.text + '')['results']

def get_ingredients(id):
    return send_request("GET", INGREDIENTS_URL.format(id=id), HEADERS, None)

def get_steps(id):
    querystring = {"stepBreakdown": "false"}
    return send_request("GET", STEPS_URL.format(id=id), HEADERS, querystring)

def get_recipe_information(id):
    return send_request("GET", INFORMATION_URL.format(id=id), HEADERS, None)
