# import flask dependencies
from flask import Flask
from database import database
from flask_assistant import Assistant, tell, ask

import logging
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.mongo = database.Mongo()

# initialize the flask app
app = FlaskApp(__name__)
assist = Assistant(app, route='/')

@assist.action('get-recipe')
def get_recipe(recipe):
    recipeDoc = app.mongo.get_recipe(recipe)
    if recipeDoc:
        speech = "We found recipe for {}, Please ask Tom and Paz".format(recipe)
        return tell(speech)
    else:
        speech = "Could not find a recipe for {}. Do you want to search different recipe?".format(recipe)
        return ask(speech)



# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
