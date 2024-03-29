import requests
import datetime
from tokens import BETS_API_KEY, ODDS_API_KEY

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

def parseTime(timeStamp):
    try:
        dt = datetime.datetime.utcfromtimestamp(int(timeStamp))
        formatted_time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return formatted_time
    except Exception as e:
        return timeStamp

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
        self.API_KEY = ODDS_API_KEY
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
        activeEvents = self.getActiveEvents(sport_name)
        all_keys = [event['sport_key'] for sport in activeEvents['active events'] for event in sport['active events']]
        return { 
                "source" : self.name,
                "sport name" : sport_name,
                "all keys" : list(set(all_keys))
            }
    def getScores(self, sport_name, event_key):
        response = requests.get(f'https://api.the-odds-api.com/v4/sports/{event_key}/scores/?apiKey={self.API_KEY}').json()
        return { 
            "source" : self.name,
            "sport name" : sport_name,
            "scores" : response
        }   
    def getMatch(self, sport_name, event_key, match_id):
        activeEventsList = self.getActiveEvents('Cricket').get('active events')
        response =  { 
            "source" : self.name,
            "sport name" : sport_name,
            "match" : None
        }
        for mainEvent in activeEventsList:
            print("Entered for loop")
            if mainEvent.get("active events")[0].get("sport_key") == event_key:
                print("Entered if")
                for event in mainEvent.get("active events"):
                    print("Entered for 2")
                    if event.get("id") == match_id:
                        print("Entered if 2")
                        response.update({ "match" : event})
                        return response
        # response.update({ "msg" : f"Requested match of {event_key} not found" })
        return False
       
class BetsAPI():
    def __init__(self) -> None:
        self.API_KEY = BETS_API_KEY
        self.name = "BetsAPI"
        self.SportsID_Dict = {
            'Cricket' : '3',
            'Soccer' : '1',
            'Tennis' : '13',
            'Horse Racing' : '2',
            'Greyhounds' : '4'
        }
        # self.sampleLink = f"https://api.b365api.com/v1/events/inplay?sport_id=3&token={self.API_KEY}"
        self.sampleLink = f"https://api.b365api.com/v1/bet365/inplay_filter?sport_id=3&token={self.API_KEY}"
    def isWorking(self):
        response = requests.get(self.sampleLink)    
        if response.status_code == 200:
            return True
        else:
            return False
    def getActiveEvents(self, sport_name):
        sport_id = self.SportsID_Dict.get(sport_name)
        link = f'https://api.b365api.com/v1/bet365/inplay_filter?sport_id={sport_id}&token={self.API_KEY}'
        print(f"Link for events {link}")
        # response = requests.get(f'https://api.b365api.com/v3/events/inplay?sport_id={sport_id}&token={self.API_KEY}').json()
        response = requests.get(link).json()
        if response.get("success") == 1:
            # customResponse = [ { "event_key" : result.get("league").get("id"), "title" : result.get("league").get("name") } for result in response.get("results") ]
            customResponse = [ 
                { 
                    "event_key" : result.get("id"), 
                    "event title" : result.get("league").get("name"),
                    "home" : result.get("home"),
                    "away" : result.get("away"),
                    "commence_time" : parseTime(result.get("time")), 
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
    
    def getScores(self, sport_name, event_key):
        sport_id = self.SportsID_Dict.get(sport_name)
        response = requests.get(f'https://api.b365api.com/v1/bet365/result?token={self.API_KEY}&event_id={sport_id}').json()
        return { 
            "source" : self.name,
            "sport name" : sport_name,
            "scores" : response
        } 
    def getUpcommingEvents(self, sport_name):
        sport_id = self.SportsID_Dict.get(sport_name)
        response = requests.get(f'https://api.b365api.com/v1/bet365/upcoming?sport_id={sport_id}&token={self.API_KEY}').json()
        return { 
            "source" : self.name,
            "sport name" : sport_name,
            "upcomming events" : response
        }
    def getMatch(self, sport_name, event_key):
        activeEventsList = self.getActiveEvents('Cricket').get('active events')
        response = { 
            "source" : self.name,
            "sport name" : sport_name,
            "match" : None
        }
        for event in activeEventsList:
            if event.get("event_key") == event_key:
                response.update({ "match" : event})
                return response
        # response.update({ "msg" : f"Requested match of {event_key} not found" })
        return None