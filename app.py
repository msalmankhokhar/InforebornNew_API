from flask import Flask, render_template, request, redirect, jsonify
import json
from util import OddsAPI, BetsAPI, keysDict, valid_sport_names, listToText, sports_from_ODDSAPI, sports_from_BETSAPI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'salmankhokhar'

try:
    with open("settings.json", "rt") as file:
        app_settings = json.load(file)
except Exception as error:
    print(error)
    with open("/home/salman138/mysite/settings.json", "rt") as file:
        app_settings = json.load(file)

external_URL = app_settings.get("external_URL")
GithubReadmelink = app_settings.get("Github Readme link")
oddsAPI = OddsAPI()
betsAPI = BetsAPI()

use_both_APIs = True

def makeResponseJSON(content):
    return jsonify({
        "success" : True,
        "response" : content
        })
def makeErrorJSON(msg):
    return jsonify({ "success" : False, "msg" : msg })

@app.route("/", methods=["GET"])
def home():
    return redirect('/docs')
    # return redirect(GithubReadmelink)

@app.route('/docs', methods=['GET'])
def docs():
    return render_template("index.html", base_URL=external_URL, oddsAPI=oddsAPI, GithubReadmelink=GithubReadmelink)

@app.route('/get-readme', methods=['GET'])
def getReadme():
    with open('readme.md', 'rt') as file:
        readmeText = file.read()
    return readmeText

@app.route("/events/<string:sport_name>", methods=["GET"])
def events(sport_name):
    if sport_name in valid_sport_names:
         if use_both_APIs:
             listOFResponses = [ oddsAPI.getActiveEvents(sport_name), betsAPI.getActiveEvents(sport_name) ]
             return makeResponseJSON(listOFResponses)
         elif sport_name in sports_from_BETSAPI:
             return makeResponseJSON(betsAPI.getActiveEvents(sport_name))
         elif sport_name in sports_from_ODDSAPI:
             return makeResponseJSON(oddsAPI.getActiveEvents(sport_name))
         elif sport_name == "all":
             listOFResponses = []
             for sportname in valid_sport_names:
                 if sportname in sports_from_BETSAPI:
                     listOFResponses.append(betsAPI.getActiveEvents(sport_name=sportname))
                 elif sportname in sports_from_ODDSAPI:
                     listOFResponses.append(oddsAPI.getActiveEvents(sport_name=sportname))                                     
             return makeResponseJSON(listOFResponses)
    else:
        return makeErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_names)}. 'all' means all sports")

@app.route("/odds/<string:sport_name>/<string:event_key>", methods=["GET"])
def data(sport_name, event_key):
    keysInOddsAPI = oddsAPI.getAllEventsKeys(sport_name).get("all keys")
    keysInBetsAPI = betsAPI.getAllEventsKeys(sport_name).get("all keys")
    if event_key.isdigit():
        if betsAPI.isWorking():
            if event_key in keysInBetsAPI:
                return makeResponseJSON(betsAPI.getData(event_key=event_key))
            else:
                return makeErrorJSON(f"Invalid event key. Get a velid event key from here {external_URL}/events/{sport_name}")
        else:
            return makeErrorJSON("BetsAPI is not working. May be the trial or suscription is over. Please resubscribe or buy the trial again.")
    elif event_key[0].isalpha():
        if event_key in keysInOddsAPI:
            return makeResponseJSON(betsAPI.getData(event_key=event_key))
        else:
            return makeErrorJSON(f"Invalid event key. Get a velid event key from here {external_URL}/events/{sport_name}")
    else:
        return makeErrorJSON("Invalid event key")