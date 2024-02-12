from util import OddsAPI, BetsAPI, valid_sport_names, listToText
import json
odds_API_KEY = '7371cc45412eb97aa50cc37c49d2ec63'
betsAPI_key = '182003-hDYxIZ431gPgIF'
def printJSON(JSON_Obj, intend=2):
    print(json.dumps(JSON_Obj, indent=intend))

"""
Sample odds api links:
OODSAPI
https://api.the-odds-api.com/v4/sports?apiKey=7371cc45412eb97aa50cc37c49d2ec63

BETSAPI
for getting events
https://api.b365api.com/v3/events/inplay?sport_id=3&token=182403-BLXmyARg5xtSAX
for getting event odds
"""
# Tennis Keys
# tennis_wta_aus_open_singles
# tennis_atp_aus_open_singles
# printJSON(OddsAPI().getActiveEvents(group="Soccer"))
# printJSON(OddsAPI().getData("tennis_atp_aus_open_singles"))
# printJSON(BetsAPI().getActiveEvents(sport_id=BetsAPI().SportsID_Dict['Cricket']))
# print(listToText(valid_sport_names))
# print("big_bash"[0].isalpha())

oddsAPI = OddsAPI()
betsAPI = BetsAPI()

printJSON(oddsAPI.getUpcommingEvents('Cricket', 'cricket_odi'))

# keysInOddsAPI = oddsAPI.getAllEventsKeys('Cricket').get("all keys")
# keysInBetsAPI = betsAPI.getAllEventsKeys('Cricket').get("all keys")
# print(keysInBetsAPI)
# print(keysInOddsAPI)
# printJSON(betsAPI.getData('32179'))
# printJSON(betsAPI.getActiveEvents('Cricket'))
# print(None == 0)
# print('cricket_test_match'[0].isdigit())
# print(betsAPI.isWorking())

# Data from betsapi Bet365 API
# inplay filter, inplay event, upcomming events, pre match odds

# printJSON(oddsAPI.getAllEventsKeys("Cricket"))
# print(betsAPI.getEventName('150521924'))

