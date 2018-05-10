from os import path

from aiohttp import ClientSession
import confidence
from jinja2 import Environment, FileSystemLoader
from sanic import Sanic
from sanic.response import html, json


HERE = path.dirname(path.abspath(__file__))


class Stoom(Sanic):
    urls = {
        'games': 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/',
    }

    def __init__(self, config):
        super().__init__(name=config.name or 'stoom')
        self._config = config
        self._env = Environment(loader=FileSystemLoader(path.join(HERE, 'templates')))
        self._client = None

        self.add_routes()

    @property
    def client(self):
        if not self._client:
            self._client = ClientSession(loop=self.loop)

        return self._client

    def add_routes(self):
        self.add_route(uri='/', handler=self.index)
        self.add_route(uri='/api/steam/player/<steam_id:int>/games', handler=self.games)
        self.add_route(uri='/api/steam/intersect-games/<steam_id1:int>/<steam_id2:int>', handler=self.intersect_games)

    async def index(self, request):
        template = self._env.get_template('stoom/index.html')
        return html(template.render())

    async def get_games(self, steam_id):
        games = await self.client.get(self.urls.get('games'), params={'key': self._config.steam.api_key,
                                                                      'steamid': steam_id,
                                                                      'format': 'json'})
        games = await games.json()
        return sorted(game['appid'] for game in games['response']['games'])

    async def games(self, request, steam_id):
        return json(await self.get_games(steam_id))

    async def get_intersecting_games(self, steam_id, *friends):
        games = set(await self.get_games(steam_id))
        for friend in friends:
            games &= set(await self.get_games(friend))

        return sorted(games)

    async def intersect_games(self, request, steam_id1, steam_id2):
        return json(await self.get_intersecting_games(steam_id1, steam_id2))


if __name__ == '__main__':
    config = confidence.load_name('stoom')
    Stoom(config).run()
