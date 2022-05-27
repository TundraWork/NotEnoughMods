from lib.adapter.cache import Cache
from lib.adapter.modlist import ModList
from lib.util.crawler import Crawler
from lib.api.curseforge import CurseForge
from lib.api.modrinth import Modrinth


modlist = ModList()
mods = modlist.read()
if mods is None:
    exit(1)
crawler = Crawler()  # hold crawler instance to avoid repeatedly open and close chrome
curseforge = CurseForge(crawler)
modrinth = Modrinth(crawler)
failed = []
new_mods = []
upgraded = []
dependencies = {}
dependencies_cleared = {}
for mod in mods:
    if mod[0] == 'curseforge':
        result = curseforge.download_from_url(mod[1])
        if result[0] is not True:
            failed.append((mod[1], result[1]))
        else:
            if result[1] == 1:
                new_mods.append(mod[1])
            elif result[1] == 2:
                upgraded.append(mod[1])
            if result[2]:
                dependencies[mod[1].split('/')[-1]] = result[2]

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

cache = Cache().read()
all_ids = []
for mod in cache['curseforge']:
    all_ids.append(cache['curseforge'][mod]['mod_id'])
for dependency in dependencies:
    tmp = []
    for dependency_mod_id in dependencies[dependency]:
        if dependency_mod_id not in all_ids:
            tmp.append(dependency_mod_id)
    if len(tmp) > 0:
        dependencies_cleared[dependency] = tmp
for dependency in dependencies_cleared:
    if len(dependencies_cleared[dependency]) == 1:
        print(f'(!){dependency} has the following dependency but is not in the mod list:')
    elif len(dependencies_cleared[dependency]) > 1:
        print(f'(!){dependency} has the following dependencies but are not in the mod list:')
    for dependency_mod_id in dependencies_cleared[dependency]:
        print(dependency_mod_id)
exit(0)
