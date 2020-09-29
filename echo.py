# load Flask 
import flask
from googletrans import Translator
app = flask.Flask(__name__)
print("Now initiating...")

# define a predict function as an endpoint 
@app.route("/translate", methods=["GET","POST"])
def translate():
    data = {"success": False}
    # get the request parameters
    params = flask.request.json
    if (params == None):
        params = flask.request.args

    # if parameters are found, echo the msg parameter 
    if (params != None):
        data["input"] = params.get("msg")
        data["language"] = params.get("language")
        data["success"] = True
    # translate via google
    try:
        translator = Translator(service_urls=['translate.google.com'])
        data["translation"] = translator.translate(data["input"], dest=data["language"]).text
    except:
        pass
    # return a response in json format 
    return flask.jsonify(data)

# start the flask app, allow remote connections
app.run(host='0.0.0.0')