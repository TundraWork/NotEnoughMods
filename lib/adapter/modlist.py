import yaml

from lib.adapter.config import Config


class ModList:
    modlist_path = None
    config = None

    def __init__(self):
        self.config = Config().read()
        self.modlist_path = self.config['modlist_path']

    def read(self):
        try:
            mods = []
            with open(self.modlist_path, 'r') as modlist_file:
                modlist = yaml.safe_load(modlist_file)
                target_mod_list = modlist['both'] + modlist[self.config['type']]
                for line in target_mod_list:
                    if 'curseforge.com' in line:
                        mods.append(('curseforge', line))
                    elif 'modrinth.com' in line:
                        mods.append(('modrinth', line))
                    else:
                        print(f'Unknown modlist entry: {line}')
                        continue
            return mods
        except Exception as e:
            print(f'(!) Can not read modlist file.')
            return None
