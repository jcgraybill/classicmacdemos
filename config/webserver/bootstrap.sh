#!/bin/sh

sudo dnf install -y gcc git nginx cronie sqlite python3-pip python3-devel
python3 -m pip install Django uwsgi markdown boto3

sudo mkdir /var/run/uwsgi
sudo chmod 777 /var/run/uwsgi
mkdir /home/ec2-user/uwsgi/

echo "GitHub Deployment Key:"
github_deployment_key=$(</dev/stdin)
echo "$github_deployment_key" | tee /home/ec2-user/.ssh/id_ed25519
eval "$(ssh-agent -s)"
ssh-add /home/ec2-user/.ssh/id_ed25519

( cd /home/ec2-user
  curl https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-oss-7.12.1-linux-arm64.tar.gz | tar xz
  git clone git@github.com:jcgraybill/classicmacdemos.git
)

echo "Django secret key:"
read django_secret_key
echo "$django_secret_key" | tee /home/ec2-user/classicmacdemos/website/secret-key.txt

sudo service nginx start
curl https://get.acme.sh | sh -s email=jcg@cro-magnon.com
acme.sh --issue -d classicmacdemos.com -d www.classicmacdemos.com -w /usr/share/nginx/html
sudo service nginx stop

sudo cp /home/ec2-user/classicmacdemos/config/webserver/nginx.conf /etc/nginx/
sudo cp /home/ec2-user/classicmacdemos/config/webserver/nginx /etc/logrotate.d/

/home/ec2-user/filebeat-7.12.1-linux-arm64/filebeat -c /home/ec2-user/classicmacdemos/config/webserver/filebeat.yml modules enable nginx

sudo cp /home/ec2-user/classicmacdemos/config/webserver/systemd/backupdb.service /etc/systemd/system/
sudo cp /home/ec2-user/classicmacdemos/config/webserver/systemd/backupdb.timer /etc/systemd/system/
sudo cp /home/ec2-user/classicmacdemos/config/webserver/systemd/filebeat.service /etc/systemd/system/
sudo cp /home/ec2-user/classicmacdemos/config/webserver/systemd/uwsgi.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo service backupdb enable
sudo service filebeat enable
sudo service uwsgi enable
sudo service nginx enable

sudo service backupdb start
sudo service filebeat start
sudo service uwsgi start
sudo service nginx start

sudo cp /home/ec2-user/classicmacdemos/config/webserver/webroot/* /usr/share/nginx/html/
sudo mkdir -p /usr/share/nginx/html/.well-known/acme-challenge
sudo chown ec2-user:ec2-user /usr/share/nginx/html/.well-known/acme-challenge

echo "Remember to set output.elasticsearch.hosts in /home/ec2-user/classicmacdemos/config/webserver/filebeat.yml"
echo "Remember to add /home/ec2-user/classicmacdemos/website/db.sqlite3"