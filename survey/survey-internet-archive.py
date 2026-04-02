# https://archive.org/developers/internetarchive/python-lib.html

from internetarchive import get_item, search_items, get_files
import os, sqlite3, sys

searches = [
    'collection:macaddict_coverdiscs',
    'collection:macformat-mag-cds',
    'collection:macworld-cds',

    'creator:"AMUG"',
    'creator:"Aztech New Media Corp." AND subject:("Macintosh" OR "Mac" OR "Macintosh software" OR "apple" OR "mac" OR "macintosh")',
    'creator:"Berkeley Macintosh User\'s Group"',
    'creator:"MacAddict"',
    'creator:"Macworld" AND mediatype:"software"',

    'subject:"MacFormat" AND mediatype:"software"',
    'subject:"Macworld" AND mediatype:"software"',

    '"BBS in a BOX" AND mediatype:"software"',
]

globs = [
    '*.iso',
    '*.ISO',
    '*.toast',
    '*.bin',
    '*.cdr',
    '*.sit',
    '*.dmg',
    '*.7z'
]

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

con = sqlite3.connect("../website/db.sqlite3")
cur = con.cursor()
query = """
select count() from demos_source where infinite_mac_url = :url
    OR disc2_infinite_mac_url = :url
    OR disc3_infinite_mac_url = :url
    OR disc4_infinite_mac_url = :url;
"""

survey_con = sqlite3.connect("survey.sqlite3")
survey_cur = survey_con.cursor()
survey_peek = "select status, note from internet_archive where url = :url;"
survey_insert = """
insert into internet_archive(url, status, note) 
values(:url, :status, :note)
on conflict (url) do update set status=:status, note=:note;
"""

memo = dict()

print()
for search in searches:
    for result in search_items(search):
        if result['identifier'] in memo:
            continue
        memo[result['identifier']] = True
        print("https://archive.org/details/" + result['identifier'])
        print("-" * 50)
        for g in globs:
            for f in get_files(result['identifier'], glob_pattern=g):
                res = cur.execute(query, { "url": f.url })
                if res.fetchone()[0] > 0:
                    print("✅ {url}".format(url=f.url))
                else:
                    sur = survey_cur.execute(survey_peek, {"url": f.url})
                    sr = sur.fetchone()
                    if sr and sr[0] == 's':
                        print("⛔️ {url}".format(url=f.url))
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
        print()