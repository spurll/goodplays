from datetime import datetime, timedelta
from time import sleep
from difflib import SequenceMatcher
from howlongtobeatpy import HowLongToBeat
import requests, json, re


SEARCH_URL = 'https://howlongtobeat.com/api/search'
DETAILS_URL = 'https://howlongtobeat.com/api/game/{id}'
DETAILS_HTML_URL = 'https://howlongtobeat.com/game/{id}'

PROPS = r'<script id="__NEXT_DATA__" type="application/json">(.+)</script>'

HEADERS = {
    'User-Agent': 'goodplays',
    'content-type': 'application/json',
    'referer': 'https://howlongtobeat.com/',
    'accept': '*/*'
}


class HLTB():
    def __init__(self, json_data=None, api_data=None):
        if not json_data and api_data:
            json_data = api_data.json_content

        self.name = json_data.get('game_name')
        self.id = json_data.get('game_id')
        self.main = json_data.get('comp_main', 0) / 3600
        self.extra = json_data.get('comp_plus', 0) / 3600
        self.comp = json_data.get('comp_100', 0) / 3600
        self.all = json_data.get('comp_all', 0) / 3600
        self.no_data = self.main + self.extra + self.comp + self.all == 0

    @property
    def url(self):
        return f'https://howlongtobeat.com/game/{self.id}'

    @property
    def main_hours(self):
        return 'Unknown' if self.no_data else hours(self.main)

    @property
    def extra_hours(self):
        return 'Unknown' if self.no_data or self.extra < self.main \
            else hours(self.extra)

    @property
    def comp_hours(self):
        return 'Unknown' if self.no_data or self.comp < self.main \
            else hours(self.comp)

    @property
    def all_hours(self):
        return 'Unknown' if self.no_data else hours(self.all)


def hours(i):
    return ('< 1' if i < 1 else str(round(i))) + \
        ' hour' + ('' if i < 2 else 's')


# Unfortunately HLTB has now added a randomly-generated API key to prevent
# parsing; will now use howlongtobeatpy to fetch this data rather than
# reinventing the wheel


def search(name):
    results = HowLongToBeat().search(name)

    if results is not None and len(results) > 0:
        data = max(results, key=lambda x: x.similarity)
        return data and HLTB(api_data=data), ""


def details(game_id):
    data = HowLongToBeat().search_from_id(game_id)
    return data and HLTB(api_data=data), ""


###############################################################################


def search_old(name):
    payload = {
        'searchType': 'games',
        'searchTerms': name.split(),
        'searchOptions': {}
    }

    url = SEARCH_URL
    r = requests.post(url, data=json.dumps(payload), headers=HEADERS)

    if r.status_code != 200:
        return {}, f'Request to {url} returned {r.status_code}'

    data = r.json().get('data')

    # Find the best match for the game title from HLTB's list
    game = data and max(data, key=lambda x:
        SequenceMatcher(None, name.lower(), x.get('game_name', '').lower()
    ).ratio())

    return data and HLTB(game), ""


# Though we can't get the JSON via the API anymore, that JSON is still supplied
# to the main HTML page in props, and remains highly parsable!
def details_old(game_id):
    url = DETAILS_HTML_URL.format(id=game_id)
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return {}, f'Request to {url} returned {r.status_code}'

    x = re.search(PROPS, r.text)
    data = json.loads(x.group(1)) \
        .get('props', {}) \
        .get('pageProps', {}) \
        .get('game', {}) \
        .get('data', {}) \
        .get('game', {})

    return data and HLTB(data[0]), ""


# Unfortunately HLTB seems to have removed (or just moved) their game details
# API, so this function no longer works; use the new details function instead
def details_very_old(game_id):
    url = DETAILS_URL.format(id=game_id)
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return {}, f'Request to {url} returned {r.status_code}'

    data = r.json().get('data', {}).get('game')
    return data and HLTB(data[0]), ""
