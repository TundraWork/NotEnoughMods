import datetime
import urllib

import requests

from lib.adapter.cache import Cache
from lib.adapter.modfile import ModFile


class Modrinth:
    api_endpoint = None
    game_version = None
    modloader = None
    cache = None
    crawler = None

    def __init__(self, config, crawler):
        self.game_version = config['game_version']
        self.modloader = config['modloader']
        self.api_endpoint = config['api']['modrinth']['api_endpoint']
        self.cache = Cache(config['type'])
        self.crawler = crawler
        self.modfile = ModFile(config)

    def api_request(self, path, override_api_endpoint=False):
        if not override_api_endpoint:
            path = f'{self.api_endpoint}{path}'
        headers = {
            'accept': 'application/json'
        }
        response = requests.get(path, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_mod_id_by_search(self, slug):
        url = 'mod?query={}&filters={}&versions={}'.format(
            slug,
            urllib.parse.quote(f'categories="{self.modloader}"'),
            urllib.parse.quote('version="' + '" OR version="'.join(self.game_version) + '"')
        )
        data = self.api_request(url)
        if data is None:
            print(f'(!) Failed to get mod id.')
            return False
        for mod in data['hits']:
            if mod['slug'] == slug:
                return mod['mod_id'][6:]
        return False

    def get_mod_id_by_crawler(self, slug):
        mod_id = self.crawler.crawl_webpage(
            f'https://modrinth.com/mod/{slug}',
            self.crawler.selectors.XPATH,
            '//*[@id="main"]/div/div[2]/div[last()]/div[4]/div[2]'
        )
        return mod_id.strip()

    def get_version(self, mod_id):
        url = f'mod/{mod_id}/version'
        data = self.api_request(url)
        if data is None:
            print(f'(!) Failed to get file id.')
        filtered = list()
        for game_version in self.game_version:
            for version in data:
                if game_version in version['game_versions'] and self.modloader.lower() in version['loaders']:
                    filtered.append(version)
            if len(filtered) != 0:
                break
        if len(filtered) == 0:
            print(f'No files found for game version: {self.game_version} and modloader: {self.modloader}!')
            return False
        latest_version = filtered[0]
        for version in filtered:
            if datetime.datetime.strptime(version['date_published'], '%Y-%m-%dT%H:%M:%S.%fZ') \
                    > datetime.datetime.strptime(latest_version['date_published'], '%Y-%m-%dT%H:%M:%S.%fZ'):
                latest_version = version
        return latest_version['id'], latest_version['files'][0]['url']

    def download_from_url(self, url):
        print(f'Processing Modrinth entry: {url}')
        if 'modrinth.com/mod' not in url:
            print('Invalid URL for Modrinth mods!')
            return False, 'Invalid URL for Modrinth mods!'
        slug = url.split('/')[-1]
        cache = self.cache.read()
        if slug in cache['modrinth'] and 'mod_id' in cache['modrinth'][slug]:
            mod_id = cache['modrinth'][slug]['mod_id']
        else:
            cache['modrinth'][slug] = {}
            print('Searching for mod ID...')
            mod_id = self.get_mod_id_by_search(slug)
            if not mod_id:
                print('Search for mod slug failed, fallback to crawling webpage...')
                mod_id = self.get_mod_id_by_crawler(slug)
                if not mod_id:
                    print('Invalid mod slug!')
                    return False, 'Invalid mod slug!'
            cache['modrinth'][slug]['mod_id'] = mod_id
            self.cache.write(cache)
        version = self.get_version(mod_id)
        upgrade = False
        if 'version_id' in cache['modrinth'][slug]:
            upgrade = True
            if version[0] == cache['modrinth'][slug]['version_id']:
                print(f'Mod {slug} is already up to date.')
                return True, False
        if not version:
            print('(!) Failed to get file url.')
            return False, 'Failed to get file url.'
        self.modfile.download(version[1], 'modrinth', mod_id, version[0], slug)
        if upgrade:
            self.modfile.delete('modrinth', mod_id, cache['modrinth'][slug]['version_id'], slug)
        cache['modrinth'][slug]['version_id'] = version[0]
        self.cache.write(cache)
        print(f'Successfully updated {slug} from Modrinth!')
        return True, True
