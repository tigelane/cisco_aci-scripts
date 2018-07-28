#!/bin/sh

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-cache policy docker-ce
sudo apt-get -f install -y
sudo apt-get install -y docker-ce
sudo systemctl status docker
sudo usermod -aG docker ${USER}

# Download and execute script
# Here so it doesn't execute again.
exit
# Copy after this line
wget -O ubuntu_install_docker.sh https://raw.githubusercontent.com/tigelane/system_utilities/master/ubuntu_install_docker.sh \
    && chmod +x ubuntu_install_docker.sh \
    && ./ubuntu_install_docker.sh
