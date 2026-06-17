#!/bin/sh

sudo apt update
sudo apt upgrade -y
sudo apt install -y qemu-guest-agent avahi-daemon

cd /home/$USER

echo -n "public ssh key: "
read key
mkdir -p .ssh
echo $key | tee -a .ssh/authorized_keys

tee sync-logs.sh << EOF
#!/bin/sh

remote_host=""
private_key=""

if ! test -z \$remote_host && ! test -z \$private_key; then
rsync -avP -e "ssh -i \$private_key" \
	$USER@\$remote_host:/var/log/nginx/ \
	/home/$USER/nginx-logs
fi
EOF
chmod 755 sync-logs.sh

echo "* * * * * /home/$USER/sync-logs.sh" | crontab

curl https://artifacts.opensearch.org/releases/core/opensearch/2.19.5/opensearch-min-2.19.5-linux-x64.tar.gz | tar xz
curl https://artifacts.opensearch.org/releases/core/opensearch-dashboards/2.19.5/opensearch-dashboards-min-2.19.5-linux-x64.tar.gz | tar xz
curl https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-oss-7.12.1-linux-x86_64.tar.gz | tar xz

tee opensearch-2.19.5/config/opensearch.yml << EOF
compatibility.override_main_response_version: true
network.host: 0.0.0.0
discovery.type: single-node
EOF

tee opensearch-dashboards-2.19.5-linux-x64/config/opensearch_dashboards.yml << EOF
opensearchDashboards.survey.url: "false"
server.host: "0.0.0.0"
EOF

mkdir -p nginx-logs
./filebeat-7.12.1-linux-x86_64/filebeat -c filebeat-7.12.1-linux-x86_64/filebeat.yml modules enable nginx

tee filebeat-7.12.1-linux-x86_64/modules.d/nginx.yml << EOF
- module: nginx
  access:
    enabled: true
    var.paths: ["/home/$USER/nginx-logs/access.log*"]
  error:
    enabled: true
    var.paths: ["/home/$USER/nginx-logs/error.log*"]
  ingress_controller:
    enabled: false
EOF

sudo tee -a /etc/sysctl.d/90-vm-max-map-count.conf << EOF
vm.max_map_count=262144
EOF

sudo tee /etc/systemd/system/opensearch.service << EOF
[Service]
Type=forking
Restart=always
User=$USER
ExecStart=/home/$USER/opensearch-2.19.5/bin/opensearch -d -p /var/tmp/opensearch.pid
PIDFile=/var/tmp/opensearch.pid

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/opensearch-dashboards.service << EOF
[Service]
Type=simple
Restart=always
User=$USER
ExecStart=/home/$USER/opensearch-dashboards-2.19.5-linux-x64/bin/opensearch-dashboards

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/filebeat.service << EOF
[Service]
Type=simple
Restart=always
User=$USER
ExecStart=/home/$USER/filebeat-7.12.1-linux-x86_64/filebeat -c /home/$USER/filebeat-7.12.1-linux-x86_64/filebeat.yml run

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

sudo systemctl enable opensearch
sudo systemctl enable opensearch-dashboards
sudo systemctl enable filebeat

sudo service opensearch start
sudo service opensearch-dashboards start
sudo service filebeat start