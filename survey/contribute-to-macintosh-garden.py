import os, subprocess, sqlite3, urllib.parse

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

query = """select dg.slug, dw.macintosh_garden, dg.filename, dg.filename_68k, dg.filename_3 
    from demos_game dg join demos_website dw on dw.game_id = dg.id;
    """

subdir = "demofiles"

with open(".gitignore", 'w') as f: 
    f.write(subdir)

con = sqlite3.connect("../website/db.sqlite3")
cur = con.cursor()
res = cur.execute(query)
for result in res.fetchall():
    print( result )
    directory = subdir + "/" + result[0]
    try: 
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"An error occurred: {e}")
    
    if result[1]:
        webloc = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>URL</key>
        <string>{url}</string>
    </dict>
    </plist>
    """.format(url=result[1])

        with open(directory + "/Macintosh Garden.webloc", 'w') as f: 
            f.write(webloc)

    if result[2] and not os.path.isfile(directory + "/" + result[2]):
        subprocess.run(['curl', '-o', directory + "/" + result[2], 
                        "https://download.classicmacdemos.com/" + urllib.parse.quote(result[2])])
    if result[3] and not os.path.isfile(directory + "/" + result[3]):
        subprocess.run(['curl', '-o', directory + "/" + result[3], 
                        "https://download.classicmacdemos.com/" + urllib.parse.quote(result[3])])
    if result[4] and not os.path.isfile(directory + "/" + result[4]):
        subprocess.run(['curl', '-o', directory + "/" + result[4], 
                        "https://download.classicmacdemos.com/" + urllib.parse.quote(result[4])])
