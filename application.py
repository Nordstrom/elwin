from flask import Flask
import flask
#from experiments.exp1 import ExampleExperiment
from planout.experiment import SimpleInterpretedExperiment
import json

# pull in json experiment definition.
class Exp1(SimpleInterpretedExperiment):
    def loadScript(self):
      self.script = json.loads(open("experiments/fredtest.json").read())

class Exp2(SimpleInterpretedExperiment):
    def loadScript(self):
      self.script = json.loads(open("experiments/compliments.json").read())

# return a dictionary with the experiment name and parameter for a userid
def get_response(userid = '2'):
    exp = Exp1(userid=userid)
    exp2 = Exp2(userid=userid)
    username = exp.get('name')
    compliment = exp2.get('compliment')
    outDict = {exp.name: username, exp2.name: compliment}
    return outDict

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda:
    flask.jsonify(get_response())))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<userid>', 'foo', (lambda userid:
    flask.jsonify(get_response(userid))))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()