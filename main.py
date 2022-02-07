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
for mod in mods:
    if mod[0] == 'curseforge':
        result = curseforge.download_from_url(mod[1])
        if result is not True:
            failed.append((mod[1], result[1]))
    elif mod[0] == 'modrinth':
        result = modrinth.download_from_url(mod[1])
        if result is not True:
            failed.append((mod[1], result[1]))
    else:
        print('(!) Unsupported mod type: ' + mod[0])
        failed.append((mod[1], 'Unsupported mod type.'))
print('Done!')
print('Failed entities:')
for failed_entity in failed:
    print(failed_entity[0] + ' : ' + failed_entity[1])
exit(0)
