# https://archive.org/developers/internetarchive/python-lib.html

from internetarchive import get_item, search_items, get_files
import os, sqlite3, sys

PRELABEL = True
DEEP = False

prelabels = [
    'uploader:(jcg@cro-magnon.com) AND mediatype:"software"',
    'uploader:(matt.sephton@gmail.com) AND mediatype:"software"'
]

searches = [
    'collection:cdnetpower',
    'collection:cdromtodaycds',
    'collection:coverdiscs AND mediatype:"software" AND subject:("Macintosh" OR "Mac" OR "Macintosh software" OR "apple" OR "mac" OR "macintosh")',
    'collection:coverdiscs_misc AND mediatype:"software" AND subject:("Macintosh" OR "Mac" OR "Macintosh software" OR "apple" OR "mac" OR "macintosh")',
    'collection:insidemacgames'
    'collection:macaddict_coverdiscs',
    'collection:macformat-mag-cds',
    'collection:macworld-cds',

    'creator:"AMUG"',
    'creator:"Australian Consolidated Press" AND mediatype:("software" OR "data")',
    'creator:"Aztech New Media Corp." AND subject:("Macintosh" OR "Mac" OR "Macintosh software" OR "apple" OR "mac" OR "macintosh")',
    'creator:"Berkeley Macintosh User\'s Group"',
    'creator:"MacAddict"',
    'creator:"MacHome" AND mediatype:"software"',
    'creator:"MacUser" AND mediatype:"software"',
    'creator:"Macworld" AND mediatype:"software"',
    'creator:"Metatec Corporation"',
    'creator:"MM-Musik-Media-Verlag"',
    'creator:"Net Power"',
    'creator:"Netpower"',

    'subject:"Australian Personal Computer" AND mediatype:("software" OR "data")',
    'subject:"Imagine Publishing" AND mediatype:"software"',
    'subject:"MacAddict" AND mediatype:"software"',
    'subject:"MacFormat" AND mediatype:"software"',
    'subject:"MacHome" AND mediatype:"software"',
    'subject:"Macworld" AND mediatype:"software"',
    'subject:"MacUser" !MACBIN AND mediatype:"software"',
    'subject:"Next Generation" 25',

    '"BBS in a BOX" AND mediatype:"software"',
    '"MacHome" AND mediatype:"software"',
    '"MacUser" mediatype:"software"'
]

globs = [
    '*.iso',
    '*.ISO',
    '*.toast',
    '*.bin',
    '*.BIN',
    '*.cdr',
    '*.sit',
    '*.dmg',
    '*.7z'
]

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

survey_con = sqlite3.connect("survey.sqlite3")
survey_cur = survey_con.cursor()
survey_shallow_peek = "select count() from internet_archive where url like '%{url}%' and status != 'l';"
survey_peek = "select status, note from internet_archive where url = :url;"
survey_insert = """
insert into internet_archive(url, status, note) 
values(:url, :status, :note)
on conflict (url) do update set status=:status, note=:note;
"""

con = sqlite3.connect("../website/db.sqlite3")
cur = con.cursor()
shallow_query = """
select count() from demos_source where infinite_mac_url like '%{url}%'
    OR disc2_infinite_mac_url like '%{url}%'
    OR disc3_infinite_mac_url like '%{url}%'
    OR disc4_infinite_mac_url like '%{url}%';
"""
query = """
select count() from demos_source where infinite_mac_url = :url
    OR disc2_infinite_mac_url = :url
    OR disc3_infinite_mac_url = :url
    OR disc4_infinite_mac_url = :url;
"""

memo = dict()

print()

if PRELABEL:
    for search in prelabels:
        for result in search_items(search):
            if result['identifier'] in memo:
                print("➡️ https://archive.org/details/" + result['identifier'])    
                continue
            memo[result['identifier']] = True

            if not DEEP:
                res = survey_cur.execute(survey_shallow_peek.format(url = result['identifier']))
                if res.fetchone()[0] > 0:
                    print("➡️ https://archive.org/details/" + result['identifier'])
                    continue
                res = cur.execute(shallow_query.format(url = result['identifier']))
                if res.fetchone()[0] > 0:
                    print("➡️ https://archive.org/details/" + result['identifier'])
                    continue

            print("https://archive.org/details/" + result['identifier'])
            print("-" * 50)

            found = False
            for g in globs:
                for f in get_files(result['identifier'], glob_pattern=g):
                    found = True
                    print("➡️ {url}".format(url=f.url))
                    survey_cur.execute(survey_insert,{ "url": f.url, "status": 'p', "note": search} )
                    survey_con.commit()
            if not found:
                url = "https://archive.org/details/" + result['identifier']
                print("➡️ {url}".format(url=url))
                survey_cur.execute(survey_insert,{ "url": url, "status": 'p', "note": search} )
                survey_con.commit()

            print()

for search in searches:
    for result in search_items(search):
        if result['identifier'] in memo:
            continue
        memo[result['identifier']] = True

        if not DEEP:
            res = survey_cur.execute(survey_shallow_peek.format(url = result['identifier']))
            if res.fetchone()[0] > 0:
                print("➡️ https://archive.org/details/" + result['identifier'])
                continue
            res = cur.execute(shallow_query.format(url = result['identifier']))
            if res.fetchone()[0] > 0:
                print("➡️ https://archive.org/details/" + result['identifier'])
                continue

        print("https://archive.org/details/" + result['identifier'])
        print("-" * 50)

        found = False
        for g in globs:
            for f in get_files(result['identifier'], glob_pattern=g):
                found = True
                res = cur.execute(query, { "url": f.url })
                if res.fetchone()[0] > 0:
                    print("✅ {url}".format(url=f.url))
                else:
                    sur = survey_cur.execute(survey_peek, {"url": f.url})
                    sr = sur.fetchone()
                    if sr and sr[0] == 's':
                        print("⛔️ {url}".format(url=f.url))
                    elif sr and sr[0] == 'p':
                        print("➡️ {url}".format(url=f.url))
                    else:
                        print("❓ {url}".format(url=f.url))
                        if sr and sr[1]:
                            print(sr[1])
                        choice = ''
                        while(choice == ''):
                            action = input("[s]kip forever, deal with [L]ater, be [d]one: ")
                            if action == '': action = 'l'
                            choice = action[0].lower()
                            if choice == 'd': sys.exit()
                            if choice != 's' and choice != 'l':
                                choice = ''
                        note = input("note [enter to leave unchanged]: ")
                        if sr and sr[1] and note == '': note = sr[1]
                        survey_cur.execute(survey_insert,{ "url": f.url, "status": choice, "note": note} )
                        survey_con.commit()
        if not found:
            url = "https://archive.org/details/" + result['identifier']
            print("➡️ {url}".format(url=url))
            survey_cur.execute(survey_insert,{ "url": url, "status": 'p', "note": search} )
            survey_con.commit()

        print()