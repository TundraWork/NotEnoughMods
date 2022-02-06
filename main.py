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
for mod in mods:
    if mod[0] == 'curseforge':
        curseforge.download_from_url(mod[1])
    elif mod[0] == 'modrinth':
        modrinth.download_from_url(mod[1])
    else:
        print('(!) Unsupported mod type: ' + mod[0])
print('Done!')
exit(0)
