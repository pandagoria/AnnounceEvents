#!/bin/bash

# source "source bots/bin/activate"

#bot startup
if [ $1 == "bot" ]
then
    python DiscordBot.py
fi

if [ $1 == "script" ]
then
    python DiscordBot.py script
fi