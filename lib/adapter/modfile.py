import os, requests
from lib.adapter.config import Config


class ModFile:
    mods_path = None

    def __init__(self):
        config = Config().read()
        self.mods_path = config['mods_path']

    def download(self, url, platform, mod_id, file_id, slug):
        print(f'Downloading new version of {slug}...')
        download = requests.get(url, allow_redirects=True)
        open(os.path.join(self.mods_path, f'{slug}_{platform}_{mod_id}_{file_id}.jar'), 'wb').write(download.content)

    def delete(self, platform, mod_id, file_id, slug):
        print(f'Deleting old version of {slug}...')
        if os.path.exists(os.path.join(self.mods_path, f'{slug}_{platform}_{mod_id}_{file_id}.jar')):
            os.remove(os.path.join(self.mods_path, f'{slug}_{platform}_{mod_id}_{file_id}.jar'))
