from lib.adapter.config import Config


class ModList:
    modlist_path = None

    def __init__(self):
        config = Config().read()
        self.modlist_path = config['modlist_path']

    def read(self):
        try:
            mods = []
            with open(self.modlist_path, 'r') as modlist_file:
                modlist = modlist_file.read().splitlines()
                for line in modlist:
                    line = line.strip()
                    if len(line) == 0 or line.startswith('#'):
                        continue
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
