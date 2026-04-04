import os, subprocess, sqlite3, urllib.parse

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

HTML     = True # HTML output
DOWNLOAD = False # Download demos locally

query = """select dg.slug, dw.macintosh_garden, dg.filename, dg.filename_68k, dg.filename_3, dg.game
    from demos_game dg join demos_website dw on dw.game_id = dg.id 
    ORDER BY dg.slug;
    """

subdir = "demofiles"

if HTML:
    print("<table><tr><th>Game</th><th>Macintosh Garden page</th><th>Demo file(s)</th></tr>")
else:
    with open(".gitignore", 'w') as f: 
        f.write(subdir)

con = sqlite3.connect("../website/db.sqlite3")
cur = con.cursor()
res = cur.execute(query)
for result in res.fetchall():
    if HTML:
        print("<tr>")
        print("<td>{name}</td>".format(name=result[5]))
        if result[1]:
            print("<td><a href=\"{mg}\">Macintosh Garden</a></td>".format(mg=result[1]))
        else:
            print("<td>no page</td>")
        print("<td>")
        for i in range(2,5):
            if result[i]:
                print("<a href=\"{url}\">{filename}</a>".format(
                    url="https://download.classicmacdemos.com/" + urllib.parse.quote(result[i]),
                    filename=result[i]
                ))
        print("</td>")
    else:
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

        if DOWNLOAD and result[2] and not os.path.isfile(directory + "/" + result[2]):
            subprocess.run(['curl', '-o', directory + "/" + result[2], 
                            "https://download.classicmacdemos.com/" + urllib.parse.quote(result[2])])
        if DOWNLOAD and result[3] and not os.path.isfile(directory + "/" + result[3]):
            subprocess.run(['curl', '-o', directory + "/" + result[3], 
                            "https://download.classicmacdemos.com/" + urllib.parse.quote(result[3])])
        if DOWNLOAD and result[4] and not os.path.isfile(directory + "/" + result[4]):
            subprocess.run(['curl', '-o', directory + "/" + result[4], 
                            "https://download.classicmacdemos.com/" + urllib.parse.quote(result[4])])

if HTML:
    print("</table>")