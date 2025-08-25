#!/bin/sh
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 "update demos_play set plays=plays-1 where plays > 0;"
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 "update demos_download set downloads=downloads-1 where downloads > 0;"
