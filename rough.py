import util
import app

betsapi = app.BetsAPI()
oddsapi = app.OddsAPI()

print( betsapi.getAllEventsKeys("Cricket") )
