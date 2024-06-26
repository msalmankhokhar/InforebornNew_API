from flask import Flask, render_template, request, redirect, jsonify, make_response, url_for
from flask_cors import CORS
from flask_caching import Cache
import json
from urllib.parse import urljoin
from util import OddsAPI, BetsAPI, makePathforPAW, keysDict, valid_sport_params, valid_sport_names, listToText, sports_from_ODDSAPI, sports_from_BETSAPI, isInternetConnected
import waitress

app = Flask(__name__)
app.config['SECRET_KEY'] = 'salmankhokhar'
cors = CORS(app)

cache = Cache(app=app, config={'CACHE_TYPE': 'SimpleCache', "CACHE_DEFAULT_TIMEOUT": 120})

try:
    with open(makePathforPAW('settings.json'), "rt") as file:
        app_settings = json.load(file)
except Exception as error:
    with open("./settings.json", "rt") as file:
        app_settings = json.load(file)

external_URL = app_settings.get("external_URL")
GithubReadmelink = app_settings.get("Github Readme link")
oddsAPI = OddsAPI()
betsAPI = BetsAPI()

use_both_APIs = True

def checkURLParam(param):
    if param == None or str(param).strip() == '':
        return False
    else:
        return True

def makeResponseJSON(content):
    return {
        "success" : True,
        "response" : content
        }

class ErrorJSON():
    def __init__(self, msg, status=400) -> None:
        self.msg = msg
        self.status = status
        self.json = { "success" : False, "msg" : msg }
        self.response = (self.json, status)
    def add(self, content):
        self.json.update(content)

@app.before_request
def checkInternet():
    status = isInternetConnected()
    if status != True:
        resp = ErrorJSON('Sever is not connected to the Internet. Cannot access external APIs', 503)
        resp.add({ "error" : str(status) })
        return resp.response

@app.route("/", methods=["GET"])
def home():
    return redirect('/docs')

@app.route('/docs', methods=['GET'])
def docs():
    return render_template("index.html", base_URL=external_URL, oddsAPI=oddsAPI, GithubReadmelink=GithubReadmelink)

@app.route('/get-readme', methods=['GET'])
def getReadme():
    try:
        with open('/home/salman138/mysite/readme.md', 'rt') as file:
            readmeText = file.read()
    except Exception as error:
        print(error)
        with open('./readme.md', 'rt') as file:
            readmeText = file.read()
    return readmeText

@app.route("/events/<string:sport_name>", methods=["GET"])
@cache.cached()
def events(sport_name):
    if sport_name in valid_sport_params:
        if sport_name == "all":
            finalResponse = []
            print("sportname")
            for sportname in valid_sport_names:
                if use_both_APIs:
                    events_from_both_APIs = { sportname : [ oddsAPI.getActiveEvents(sportname), betsAPI.getActiveEvents(sportname) ] }
                    finalResponse.append(events_from_both_APIs)
                else:
                    if sportname in sports_from_BETSAPI:
                        finalResponse.append(betsAPI.getActiveEvents(sport_name=sportname))
                    elif sportname in sports_from_ODDSAPI:
                        finalResponse.append(oddsAPI.getActiveEvents(sport_name=sportname))
            return makeResponseJSON(finalResponse)
        elif use_both_APIs:
            finalResponse = [ oddsAPI.getActiveEvents(sport_name), betsAPI.getActiveEvents(sport_name) ]
            return makeResponseJSON(finalResponse)
        else:
            if sport_name in sports_from_BETSAPI:
                finalResponse = betsAPI.getActiveEvents(sport_name)
                return makeResponseJSON(finalResponse)
            elif sport_name in sports_from_ODDSAPI:
                finalResponse = oddsAPI.getActiveEvents(sport_name)
                return makeResponseJSON(finalResponse)
    else:
        return ErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_params)}. 'all' means all sports").response

@app.route("/events/betfair", methods=["GET"])
@cache.cached()
def betfair_events():
    variant = request.args.get('variant')
    if variant and variant.strip() != '':
        return makeResponseJSON(betsAPI.getBetfairActiveEvents(variant=variant))
    else:
        return makeResponseJSON(betsAPI.getBetfairActiveEvents())

@app.route("/odds/<string:sport_name>/<string:event_key>", methods=["GET"])
@cache.cached(20)
def data(sport_name, event_key):
    if sport_name in valid_sport_params:
        keysInOddsAPI = oddsAPI.getAllEventsKeys(sport_name).get("all keys")
        keysInBetsAPI = betsAPI.getAllEventsKeys(sport_name).get("all keys")
        print(keysInOddsAPI)
        print(keysInBetsAPI)
        if event_key.isdigit():
            print("key is digit")
            if betsAPI.isWorking():
                if event_key in keysInBetsAPI:
                    return makeResponseJSON(betsAPI.getData(event_key=event_key, sport_name=sport_name))
                else:
                    if len(keysInBetsAPI) == 0:
                        return ErrorJSON(f"Currently no events are being recieved from betsapi. Check all events of {sport_name} returned by OddsAPI and BetsAPI at {request.host_url}events/{sport_name}").response
                    else:
                        return ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host}events/{sport_name}").response
            else:
                return ErrorJSON("BetsAPI is not working. May be the trial or suscription is over. Please resubscribe or buy the trial again.").response
        elif event_key[0].isalpha():
            if event_key in keysInOddsAPI:
                return makeResponseJSON(oddsAPI.getData(event_key=event_key, sport_name=sport_name))
            else:
                response = ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}, or you can use any of the given valid event keys")
                response.add({ "valid event keys" : oddsAPI.getAllEventsKeys(sport_name).get("all keys") + betsAPI.getAllEventsKeys(sport_name).get("all keys") })
                return response.response
        else:
            return ErrorJSON("Invalid event key").response
    else:
        return ErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_params)}. 'all' means all sports").response

@app.route("/fancy/<string:variant>/<string:event_key>", methods=["GET"])
@cache.cached(timeout=20)
def fancy(variant, event_key):
    if variant in [ 'ex', 'sb' ]:
        return makeResponseJSON(betsAPI.getFancyOdds(event_key=event_key, variant=variant))
    else:
        return ErrorJSON('Invalid betfair variant. Choose from sb (sportsbook) or ex (exchange)').response
    
@app.route("/match/<string:sport_name>/<string:event_key>", methods=["GET"])
@cache.cached()
def match(sport_name, event_key):
    if sport_name in valid_sport_params:
        keysInOddsAPI = oddsAPI.getAllEventsKeys(sport_name).get("all keys")
        keysInBetsAPI = betsAPI.getAllEventsKeys(sport_name).get("all keys")
        if event_key.isdigit():
            if betsAPI.isWorking():
                if event_key in keysInBetsAPI:
                    funcResponse = betsAPI.getMatch(event_key=event_key, sport_name=sport_name)
                    if funcResponse == False:
                        response = ErrorJSON(
                            msg=f"Requested match of {sport_name} with event key {event_key} not found",
                            status=404
                            )
                        return response.response
                    return makeResponseJSON(funcResponse)
                else:
                    if len(keysInBetsAPI) == 0:
                        return ErrorJSON(f"Currently no events are being recieved from betsapi. Check all events of {sport_name} returned by OddsAPI and BetsAPI at {request.host_url}events/{sport_name}").response
                    else:
                        return ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}").response
            else:
                return ErrorJSON("BetsAPI is not working. May be the trial or suscription is over. Please resubscribe or buy the trial again.").response
        elif event_key[0].isalpha():
            match_id = request.args.get("match_id")
            if not match_id or match_id == '':
                response = ErrorJSON(f"Missing or invalid match_id. Provide a match_id in URL params such as {urljoin(request.host_url, url_for('match', sport_name=sport_name, event_key=event_key))}?match_id=<match_id here>, You only need to provide match_id if you want to access a match from odds API. Get a match_id from {request.host_url}events/{sport_name} and pass as URL param in /match endpoint ")
                return response.response
            if event_key in keysInOddsAPI:
                funcResponse = oddsAPI.getMatch(event_key=event_key, sport_name=sport_name, match_id=match_id)
                if funcResponse == False:
                    response = ErrorJSON(
                        msg=f"Requested match of {sport_name} with event key {event_key} and match_id {match_id} not found",
                        status=404
                        )
                    return response.response
                return makeResponseJSON(funcResponse)
            else:
                response = ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}, or you can use any of the given valid event keys")
                response.add({ "valid event keys" : oddsAPI.getAllEventsKeys(sport_name).get("all keys") + betsAPI.getAllEventsKeys(sport_name).get("all keys") })
                return response.response
        else:
            return ErrorJSON("Invalid event key").response
    else:
        return ErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_params)}. 'all' means all sports").response
    
@app.route('/scores/<string:sport_name>/<string:event_key>', methods=["GET"])
@cache.cached(timeout=20)
def scores(sport_name, event_key):
    if sport_name in valid_sport_params:
        keysInOddsAPI = oddsAPI.getAllEventsKeys(sport_name).get("all keys")
        keysInBetsAPI = betsAPI.getAllEventsKeys(sport_name).get("all keys")
        if event_key.isdigit():
            print("key is digit")
            if betsAPI.isWorking():
                if event_key in keysInBetsAPI:
                    return makeResponseJSON(betsAPI.getScores(sport_name=sport_name, event_key=event_key))
                else:
                    if len(keysInBetsAPI) == 0:
                        return ErrorJSON(f"Currently no events are being recieved from betsapi. Check all events of {sport_name} returned by OddsAPI and BetsAPI at {request.host_url}events/{sport_name}").response
                    else:
                        response = ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}, or you can use any of the given valid event keys")
                        response.add({ "valid event keys" : oddsAPI.getAllEventsKeys(sport_name).get("all keys") + betsAPI.getAllEventsKeys(sport_name).get("all keys") })
                        return response.response
            else:
                return ErrorJSON("BetsAPI is not working. May be the trial or suscription is over. Please resubscribe or buy the trial again.")
        elif event_key[0].isalpha():
            if event_key in keysInOddsAPI:
                return makeResponseJSON(oddsAPI.getScores(sport_name=sport_name, event_key=event_key))
            else:
                response = ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}, or you can use any of the given valid event keys")
                response.add({ "valid event keys" : oddsAPI.getAllEventsKeys(sport_name).get("all keys") + betsAPI.getAllEventsKeys(sport_name).get("all keys") })
                return response.response
        else:
            response = ErrorJSON(f"Invalid event key. Get a valid event key from here {request.host_url}events/{sport_name}, or you can use any of the given valid event keys")
            response.add({ "valid event keys" : oddsAPI.getAllEventsKeys(sport_name).get("all keys") + betsAPI.getAllEventsKeys(sport_name).get("all keys") })
            return response.response
    else:
        return ErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_params)}. 'all' means all sports").response
    
@app.route('/upcomming/<string:sport_name>', methods=["GET"])
@cache.cached(200)
def upcomming_events(sport_name):
    if sport_name in valid_sport_params:
        if sport_name == "all":
            finalResponse = []
            for sportname in valid_sport_names:
                upcomming_events = { sportname : [ betsAPI.getUpcommingEvents(sportname) ] }
                finalResponse.append(upcomming_events)
            return makeResponseJSON(finalResponse)
        else:
            finalResponse = []
            upcomming_events = { f"upcomming events of {sport_name}" : [ betsAPI.getUpcommingEvents(sport_name) ] }
            return makeResponseJSON(upcomming_events)
    else:
        return ErrorJSON(f"Invalid sport name. Valid Sports names are {listToText(valid_sport_params)}. 'all' means all sports").response

@app.route('/tokens', methods=['GET'])
def tokens():
    return {
        "Bets API" : betsAPI.API_KEY,
        "Odds API" : oddsAPI.API_KEY
        }

@app.errorhandler(404)
def not_found(e):
    return ErrorJSON(f"Endpoint not found(404), Please read API documentation at { urljoin( request.host_url, url_for('docs') ) }", 404).response

@app.errorhandler(500)
def internal_server_error(e):
    errorJson = ErrorJSON(str(e), 500)
    return errorJson.response

# app run settings
app_port = 80
debug = True

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=app_port, debug=debug)
    waitress.serve(app=app, host='0.0.0.0', port=80)