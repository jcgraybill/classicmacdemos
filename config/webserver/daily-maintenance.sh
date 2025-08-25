#!/bin/sh
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 "UPDATE demos_play SET plays=plays-1 WHERE plays > 1;"
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 "UPDATE demos_download SET downloads=downloads-1 WHERE downloads > 1;"
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 "UPDATE demos_play SET plays = 0 WHERE game_id IN (select id from demos_game where game like 'Living Books%');"
/usr/bin/date >> /home/ec2-user/daily-maintenance.log