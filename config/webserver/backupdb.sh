#!/bin/sh
DATE=$(/usr/bin/date "+%F-%T")
/usr/bin/sqlite3 /home/ec2-user/classicmacdemos/website/db.sqlite3 ".backup /home/ec2-user/backups/backup-$DATE.sqlite3"