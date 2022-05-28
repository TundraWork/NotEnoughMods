import json

from lib.adapter.config import Config


class Cache:
    cache = {
        'curseforge': {},
        'modrinth': {}
    }
    type = None

    def __init__(self):
        self.type = Config().read()['type']
        with open(f'conf/cache.{self.type}.json', 'a+') as cache_file:
            cache_file.seek(0)
            try:
                self.cache = json.load(cache_file)
            except json.decoder.JSONDecodeError:
                pass

    def read(self):
        return self.cache

    def write(self, data):
        self.cache = data
        with open(f'conf/cache.{self.type}.json', 'w+') as cache_file:
            json.dump(data, cache_file)
