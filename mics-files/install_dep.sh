#!/usr/bin/env bash

# Author: Veerendra K
# Description: Installs dependency packages for Odoo app deployment

wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
sudo add-apt-repository "deb http://download.virtualbox.org/virtualbox/debian xenial contrib"
sudo apt update
echo "[*] Installing VirtualBox, Vagrant and PIP"
sudo apt-get install virtualbox-6.0 python-pip vagrent -y
echo "[*] Installing ansible"
sudo pip install ansible
echo "[*] Downloading minikube binary"
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo install minikube /usr/local/bin
