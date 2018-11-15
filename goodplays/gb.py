from datetime import datetime, timedelta
from time import sleep
import requests


# https://www.giantbomb.com/api/

# "We restrict the number of requests made per user/hour. We officially support
# 200 requests per resource, per hour. In addition, we implement velocity
# detection to prevent malicious use. If too many requests are made per second,
# you may receive temporary blocks to resources."

# TODO: Cache responses, if necessary.


class GiantBomb():
    def __init__(self, api_key):
        self.api_key = api_key
        self.history = []

    def request(self, url, **kwargs):
        payload = {'api_key': self.api_key, 'format': 'json', **kwargs}
        headers = {'User-Agent': 'goodplays'}

        if not self.rate_limit(url):
            return {}, 'Too many requests! Please obey the speed limit!'

        r = requests.get(url, params=payload, headers=headers)

        if r.status_code != 200:
            return {}, 'Request to {} returned {}'.format(url, r.status_code)

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
            'https://www.giantbomb.com/api/game/{}/'.format(game_id)
        )

    def games(self, limit=None, offset=None):
        return self.request(
            'https://www.giantbomb.com/api/games/',
            limit=None, offset=None
        )

    def search(self, query, limit=None, offset=None):
        return self.request(
            'https://www.giantbomb.com/api/search/',
            query=query, limit=limit, offset=offset, resources='game'
        )
