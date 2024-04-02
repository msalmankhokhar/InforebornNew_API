from bs4 import BeautifulSoup
import requests
import json

# What I am doing: Doing webscaping from a webpage

link = 'https://betsapi.com/docs/bet365/fields.html'

data = dict()

html = requests.get(link).content

soup = BeautifulSoup(html, 'html.parser')

rowList = soup.select('table tbody tr')

for row in rowList:
    abbrieviation = row.select_one('td:nth-child(1)').get_text()
    value = row.select_one('td:nth-child(2)').get_text()
    data[abbrieviation] = value
    print(f"Saved {value} in the json file")

json.dump(data, open('betsapi_fields.json', 'w'), indent=2)
