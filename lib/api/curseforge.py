import os, requests
from lib.adapter.config import Config
from lib.adapter.cache import Cache
from lib.adapter.modfile import ModFile


class CurseForge:
    api_endpoint = None
    api_key = None
    user_agent = None
    game_version = None
    modloader = None
    cache = None
    crawler = None
    modfile = None

    def __init__(self, crawler):
        config = Config().read()
        self.game_version = config['game_version']
        self.modloader = config['modloader']
        self.api_endpoint = config['api']['curseforge']['api_endpoint']
        self.api_key = config['api']['curseforge']['api_key']
        self.user_agent = config['api']['curseforge']['user_agent']
        self.cache = Cache()
        self.crawler = crawler
        self.modfile = ModFile()

    def api_request(self, path, override_api_endpoint=False):
        if not override_api_endpoint:
            path = f'{self.api_endpoint}{path}'
        headers = {
            'accept': 'application/json',
            'x-api-key': self.api_key,
            'user-agent': self.user_agent
        }
        response = requests.get(path, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_mod_id_by_search(self, slug):
        url = f'/addon/search?gameId=432&sectionId=6&searchFilter={slug}'
        data = self.api_request(url)
        if data is None:
            print(f'(!) Failed to get mod id.')
            return False
        for mod in data:
            if mod['slug'] == slug:
                return mod['id']
        return False

    def get_mod_id_by_crawler(self, slug):
        mod_id = self.crawler.crawl_webpage(
            f'https://www.curseforge.com/minecraft/mc-mods/{slug}',
            self.crawler.selectors.XPATH,
            '/html/body/div[1]/main/div[1]/div[2]/section/aside/div[2]/div/div[1]/div[2]/div[1]/span[2]'
            )
        return mod_id

    def get_file_id(self, mod_id):
        url = f'/addon/{mod_id}/files'
        data = self.api_request(url)
        if data is None:
            return False
        filtered = list()
        for game_version in self.game_version:
            for file in data:
                if game_version in file['gameVersion'] and self.modloader in file['gameVersion']:
                    filtered.append(file)
            if len(filtered) != 0:
                break
        if len(filtered) == 0:
            print(f'No files found for game version: {self.game_version} and modloader: {self.modloader}!')
            return False
        latest_file = filtered[0]
        for file in filtered:
            if file['id'] > latest_file['id']:
                latest_file = file
        return latest_file['id']

    def get_file_url(self, mod_id, file_id):
        url = f'/addon/{mod_id}/file/{file_id}/download-url'
        data = self.api_request(url)
        if data is None:
            return False
        return data

    def download_from_url(self, url):
        print(f'Processing CurseForge entry: {url}')
        if 'www.curseforge.com/minecraft/mc-mods' not in url:
            print('Invalid URL for CurseForge Minecraft mods!')
            return False
        slug = url.split('/')[-1]
        cache = self.cache.read()
        if slug in cache['curseforge']:
            mod_id = cache['curseforge'][slug]['mod_id']
        else:
            cache['curseforge'][slug] = {}
            print('Searching for mod ID...')
            mod_id = self.get_mod_id_by_search(slug)
            if not mod_id:
                print('Search for mod slug failed, fallback to crawling webpage...')
                mod_id = self.get_mod_id_by_crawler(slug)
                if not mod_id:
                    print('Invalid mod slug!')
                    return False
                else:
                    mod_id = int(mod_id)
            cache['curseforge'][slug]['mod_id'] = mod_id
        file_id = self.get_file_id(mod_id)
        if not file_id:
            print(f'(!) Failed to get file id.')
            return False
        upgrade = False
        if 'file_id' in cache['curseforge'][slug]:
            upgrade = True
            if file_id <= cache['curseforge'][slug]['file_id']:
                print(f'Mod {slug} is already up to date.')
                return True
        url = self.get_file_url(mod_id, file_id)
        if not url:
            print('(!) Failed to get file url.')
            return False
        self.modfile.download(url, 'curseforge', mod_id, file_id, slug)
        if upgrade:
            self.modfile.delete('curseforge', mod_id, cache['curseforge'][slug]['file_id'], slug)
        cache['curseforge'][slug]['file_id'] = file_id
        self.cache.write(cache)
        print(f'Successfully updated {slug} from CurseForge!')
        return True
