# import flask dependencies
from flask import Flask
from flask_assistant import Assistant, tell, ask

import logging
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

# initialize the flask app
app = Flask(__name__)
assist = Assistant(app, route='/')

@assist.action('get-recipe')
def get_recipe(recipe):
    speech = "Do you want {}?".format(recipe)
    return ask(speech)

# run the app
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
