import requests

valid_sport_params = ["Cricket", "Tennis", "Soccer", "Horse Racing", "Greyhounds", "all"]
valid_sport_names = ["Cricket", "Tennis", "Soccer", "Horse Racing", "Greyhounds"]
sports_from_ODDSAPI = ["Tennis"]
sports_from_BETSAPI = ["Cricket","Soccer", "Horse Racing", "Greyhounds"]

def insert_kv(givenDict, key, value, position):
    items = list(givenDict.items())
    items.insert(position, (key, value))
    return dict(items)

def listToText(list):
    str = ""
    lastIndex = len(list) - 1
    for item in list:
        str += item
        if list.index(item) < lastIndex -1:
            str += ", "
        elif list.index(item) == lastIndex-1:
            str += " and "
    return str

keysDict = {
    "tennis_atp_aus_open_singles" : {
        "game" : "Tennis",
        "API" : "OODSAPI",
        "description" : "Tennis Australia Men"
    },
    "tennis_wta_aus_open_singles" : {
        "game" : "Tennis",
        "API" : "OODSAPI",
        "description" : "Tennis Australia Women"
    }
}

class OddsAPI():
    def __init__(self) -> None:
        self.name = "OddsAPI"   
        self.API_KEY = '7371cc45412eb97aa50cc37c49d2ec63'
        self.valid_sport_groups = [ "Cricket" , "Tennis" , "Soccer" , "American Football"]
        self.valid_oddsFormats = [ "american" , "decimal" ]
        self.valid_regions = [ "eu" , "us" , "us2" , "uk" , "au" ]
        self.valid_markets = [ "totals" , "spreads" , "h2h" ]
    def getActiveEvents(self, sport_name):
        all_active_events = requests.get(f'https://api.the-odds-api.com/v4/sports?apiKey={self.API_KEY}').json()     
        customResponse = [
            {
            "event title" : event["title"], 
            "description" : event["description"], 
            "active events" : requests.get(f'https://api.the-odds-api.com/v4/sports/{event["key"]}/events?apiKey={self.API_KEY}').json() 
            }
            for event in all_active_events if event["group"] == sport_name
                        ]
        return { 
            "source" : self.name,
            "sport name" : sport_name,
            "active events" : customResponse
        }
    def getData(self, event_key, sport_name, oddsFormat='decimal', region='uk', bookmakers='betfair_ex_uk', markets='h2h'):
        data = requests.get(f'https://api.the-odds-api.com/v4/sports/{event_key}/odds?regions={region}&oddsFormat={oddsFormat}&bookmakers={bookmakers}&markets={markets}&apiKey={self.API_KEY}').json()
        return { 
            "sport name" : sport_name,
            f"data from {self.name}" : data
        }
    def getAllEventsKeys(self, sport_name):
        eventList = self.getActiveEvents(sport_name).get("active events")
        return { 
            "source" : self.name,
            "sport name" : sport_name,
            "all keys" : [ event.get("active events")[0].get("sport_key") for event in eventList ]
        }
       
class BetsAPI():
    def __init__(self) -> None:
        self.API_KEY = '183417-CLoHWYawPQWhmA'
        self.name = "BetsAPI"
        self.SportsID_Dict = {
            'Cricket' : '3',
            'Soccer' : '1',
            'Tennis' : '13',
            'Horse Racing' : '2',
            'Greyhounds' : '4'
        }
    def isWorking(self):
        response = requests.get(f"https://api.b365api.com/v3/events/inplay?sport_id=3&token={self.API_KEY}")    
        if response.status_code == 200:
            return True
        else:
            return False
    def getActiveEvents(self, sport_name):
        sport_id = self.SportsID_Dict.get(sport_name)
        # response = requests.get(f'https://api.b365api.com/v3/events/inplay?sport_id={sport_id}&token={self.API_KEY}').json()
        response = requests.get(f'https://api.b365api.com/v1/bet365/inplay_filter?sport_id={sport_id}&token={self.API_KEY}').json()
        if response.get("success") == 1:
            # customResponse = [ { "event_key" : result.get("league").get("id"), "title" : result.get("league").get("name") } for result in response.get("results") ]
            customResponse = [ 
                { 
                    "event_key" : result.get("id"), 
                    "event title" : result.get("league").get("name"),
                    "home" : result.get("home"),
                    "away" : result.get("away")
                } 
            for result in response.get("results")
            ]
            return { 
                "success" : True,
                "source" : self.name,
                "sport name" : sport_name,
                "active events" : customResponse
            }
        else:
            return { 
                "source" : self.name,
                "sport name" : sport_name,
                "active events" : response
            }
    def getData(self, event_key, sport_name):
        # api_response = requests.get(f'https://api.b365api.com/v2/event/odds/summary?event_id={event_key}&token={self.API_KEY}').json()
        # api_response = requests.get(f'https://api.b365api.com/v2/event/odds?event_id={event_key}&token={self.API_KEY}').json()
        api_response = requests.get(f'https://api.b365api.com/v3/bet365/prematch?token={self.API_KEY}&FI={event_key}').json()
        api_response.update( { "results" : [ insert_kv(result, 'event name', self.getEventName(event_key), 0) for result in api_response.get('results') ] } )
        return { 
            "sport name" : sport_name,
            f"data from {self.name}" : api_response
        }
    def getAllEventsKeys(self, sport_name):
        activeEvents = self.getActiveEvents(sport_name)
        if activeEvents.get("success") == True:
            eventList = activeEvents.get("active events")
            return { 
                "source" : self.name,
                "sport name" : sport_name,
                "all keys" : [ event.get("event_key") for event in eventList ]
            }
        else:
            return { 
                "source" : self.name,
                "sport name" : sport_name,
                "all keys" : None
            }
    def getEventName(self, event_key):
        response = requests.get(f'https://api.b365api.com/v1/bet365/event?token={self.API_KEY}&FI={event_key}').json()
        return response.get('results')[0][0].get('CT')