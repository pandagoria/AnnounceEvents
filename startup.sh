#!/bin/bash

python3.12 -m venv bots
echo "Виртуальная среда создана"
source "bots/bin/activate"
echo "Виртуальная среда активирована"
pip3 install -r requirements.txt
echo "Установлены зависимости"
bash announce.sh bot > log.txt