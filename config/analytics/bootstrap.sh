#!/bin/sh

sudo dnf install git

echo "GitHub Deployment Key:"
github_deployment_key=$(</dev/stdin)
echo "$github_deployment_key" | tee /home/ec2-user/.ssh/id_ed25519
sudo chmod 0600 /home/ec2-user/.ssh/id_ed25519
eval "$(ssh-agent -s)"
ssh-add /home/ec2-user/.ssh/id_ed25519

( cd /home/ec2-user
  curl https://artifacts.opensearch.org/releases/core/opensearch/2.12.0/opensearch-min-2.12.0-linux-arm64.tar.gz | tar xz
  curl https://artifacts.opensearch.org/releases/core/opensearch-dashboards/2.12.0/opensearch-dashboards-min-2.12.0-linux-arm64.tar.gz | tar xz
  git clone git@github.com:jcgraybill/classicmacdemos.git
)

cp /home/ec2-user/classicmacdemos/config/analytics/opensearch.yml /home/ec2-user/opensearch-2.12.0/config/
cp /home/ec2-user/classicmacdemos/config/analytics/opensearch_dashboards.yml /home/ec2-user/opensearch-dashboards-2.12.0-linux-arm64/config/

sudo cp /home/ec2-user/classicmacdemos/config/analytics/90-vm-max-map-count.conf /etc/sysctl.d/
sudo sysctl -p

sudo cp /home/ec2-user/classicmacdemos/config/analytics/systemd/opensearch.service /etc/systemd/system/
sudo cp /home/ec2-user/classicmacdemos/config/analytics/systemd/opensearch-dashboards.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable opensearch
sudo systemctl enable opensearch-dashboards

sudo service opensearch start
sudo service opensearch-dashboards start