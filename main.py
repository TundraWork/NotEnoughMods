from lib.adapter.cache import Cache
from lib.adapter.config import Config
from lib.adapter.modlist import ModList
from lib.api.curseforge import CurseForge
from lib.api.modrinth import Modrinth
from lib.util.crawler import Crawler


def main(conf):
    modlist = ModList(conf)
    mods = modlist.read()
    if mods is None:
        exit(1)
    crawler = Crawler(conf)  # hold crawler instance to avoid repeatedly open and close chrome
    curseforge = CurseForge(conf, crawler)
    modrinth = Modrinth(conf, crawler)
    cache = Cache(conf).read()
    failed = []
    new_mods = []
    upgraded = []
    curseforge_mods = []
    dependency_list = {}
    missing_dependency_list = {}
    for mod in mods:
        if mod[0] == 'curseforge':
            result = curseforge.download_from_url(mod[1])
            slug = mod[1].split('/')[-1]
            if slug in cache['curseforge']:
                curseforge_mods.append(cache['curseforge'][slug]['mod_id'])
            if result[0] is not True:
                failed.append((mod[1], result[1]))
            else:
                if result[1] == 1:
                    new_mods.append(mod[1])
                elif result[1] == 2:
                    upgraded.append(mod[1])
                if result[2]:
                    dependency_list[slug] = result[2]

        elif mod[0] == 'modrinth':
            result = modrinth.download_from_url(mod[1])
            if result[0] is not True:
                failed.append((mod[1], result[1]))
            elif result[1]:
                upgraded.append(mod[1])
        else:
            print('(!) Unsupported mod type: ' + mod[0])
            failed.append((mod[1], 'Unsupported mod type.'))

    print('Done!')
    if len(new_mods) == 1:
        print(f'Added {len(new_mods)} new mod:')
    elif len(new_mods) > 1:
        print(f'Added {len(new_mods)} new mods:')
    else:
        print('No new mods added')
    for new_mod in new_mods:
        print(new_mod)

    if len(upgraded) == 1:
        print(f'Upgraded {len(upgraded)} mod:')
    elif len(upgraded) > 1:
        print(f'Upgraded {len(upgraded)} mods:')
    else:
        print('No mods upgraded.')
    for upgraded_entity in upgraded:
        print(upgraded_entity)

    if len(failed) == 1:
        print(f'{len(failed)} entity failed:')
    elif len(failed) > 1:
        print(f'{len(failed)} entities failed:')
    else:
        print('No failed entities.')
    for failed_entity in failed:
        print(failed_entity[0] + ' : ' + failed_entity[1])

    for mod, dependencies in dependency_list.items():
        missing_dependencies = []
        for dependency in dependencies:
            if dependency not in curseforge_mods:
                missing_dependencies.append(dependency)
        if len(missing_dependencies):
            missing_dependency_list[mod] = missing_dependencies
    for dependency in missing_dependency_list:
        if len(missing_dependency_list[dependency]) == 1:
            print(f'(!){dependency} has the following dependency but is not in the mod list:')
        elif len(missing_dependency_list[dependency]) > 1:
            print(f'(!){dependency} has the following dependencies but are not in the mod list:')
        for dependency_mod_id in missing_dependency_list[dependency]:
            print(dependency_mod_id)
    return True


if __name__ == '__main__':
    if main(Config('server').read()):
        print('Server side done!')
    if main(Config('client').read()):
        print('Client side done!')

