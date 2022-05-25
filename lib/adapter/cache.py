import json
import os


class Cache:
    cache = {
        'curseforge': {},
        'modrinth': {}
    }

    def __init__(self):
        with open('conf/cache.json', 'a+') as cache_file:
            cache_file.seek(0)
            try:
                self.cache = json.load(cache_file)
            except json.decoder.JSONDecodeError:
                pass

    def read(self):
        return self.cache

    def write(self, data):
        self.cache = data
        with open('conf/cache.json', 'w+') as cache_file:
            json.dump(data, cache_file)
