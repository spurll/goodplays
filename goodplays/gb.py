from datetime import datetime, timedelta
from time import sleep
import requests


# https://www.giantbomb.com/api/

# "We restrict the number of requests made per user/hour. We officially support
# 200 requests per resource, per hour. In addition, we implement velocity
# detection to prevent malicious use. If too many requests are made per second,
# you may receive temporary blocks to resources."

# TODO: Cache responses, if necessary.


GAME_FIELDS = [
    'id',
    'name',
    'platforms',
    'site_detail_url',
    'deck',
    'image',
    'expected_release_day',
    'expected_release_month',
    'expected_release_year',
]

PLATFORM_FIELDS = [
    'id',
    'name',
    'company',
    'abbreviation',
    'image',
    'platforms',
    'site_detail_url',
    'release_date'
]


class GiantBomb():
    def __init__(self, api_key):
        self.api_key = api_key
        self.history = []

    def request(self, url, **kwargs):
        headers = {'User-Agent': 'goodplays'}
        payload = {
            'api_key': self.api_key,
            'format': 'json',
            **kwargs
        }

        if not self.rate_limit(url):
            return {}, 'Too many requests! Please obey the speed limit!'

        r = requests.get(url, params=payload, headers=headers)

        if r.status_code != 200:
            return {}, f'Request to {url} returned {r.status_code}'

        json = r.json()

        if json.get('status_code') != 1:
            return {}, json.get('error', 'Unknown error')

        return json.get('results', {}), ""

    def rate_limit(self, url):
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        milliseconds_ago = now - timedelta(milliseconds=200)

        # Make sure we don't make more than 200 requests in an hour
        if len(self.history) >= 200 and self.history[0] >= one_hour_ago:
            return False

        # Make sure that requests are at least 200 milliseconds apart
        if self.history and self.history[-1] >= milliseconds_ago:
            sleep((self.history[-1] - milliseconds_ago).total_seconds())

        self.history.append(now)

        # Keep a record of the last 200 requests
        if len(self.history) > 200:
            self.history.pop(0)

        return True

    def game(self, game_id):
        return self.request(
            f'https://www.giantbomb.com/api/game/{game_id}/',
            field_list=','.join(GAME_FIELDS)
        )

    # TODO: When limit and offset=None, consider doing paging here, then
    # merging the results

    def games(self, limit=None, offset=None):
        return self.request(
            'https://www.giantbomb.com/api/games/',
            limit=limit, offset=offset, field_list=','.join(GAME_FIELDS)
        )

    def platform(self, platform_id):
        return self.request(
            f'https://www.giantbomb.com/api/platform/{platform_id}/',
            field_list=','.join(PLATFORM_FIELDS)
        )

    def platforms(self, limit=None, offset=None):
        return self.request(
            'https://www.giantbomb.com/api/platforms/',
            limit=limit, offset=offset, field_list=','.join(PLATFORM_FIELDS)
        )

    def search(self, query, limit=None, offset=None):
        return self.request(
            'https://www.giantbomb.com/api/search/',
            query=query, limit=limit, offset=offset, resources='game',
            field_list=','.join(GAME_FIELDS)
        )
