import json


class Cache:
    cache = {
        'curseforge': {},
        'modrinth': {}
    }

    def __init__(self):
        with open('conf/cache.json', 'r') as cache_file:
            try:
                self.cache = json.load(cache_file)
                test = 1
            except json.decoder.JSONDecodeError:
                pass

    def read(self):
        return self.cache

    def write(self, data):
        self.cache = data
        with open('conf/cache.json', 'w+') as cache_file:
            json.dump(data, cache_file)
