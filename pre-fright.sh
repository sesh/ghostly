#!/bin/sh

sudo apt install -y python3.5-dev git-core htop python3-pip python3-setuptools build-essential libfreetype6 libfreetype6-dev fontconfig

wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar -xf phantomjs-2.1.1-linux-x86_64.tar.bz2
sudo mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/
sudo chmod a+x /usr/local/bin/phantomjs

sudo pip3 install glances
sudo pip3 install git+https://github.com/sesh/ghostly.git
