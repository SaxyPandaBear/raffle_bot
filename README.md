Raffle Bot
==========

A simple Discord bot made to handle raffles in a given server.

### Setup

- Written in Python 3.5+
- Uses [discord.py v0.16.12](https://github.com/Rapptz/discord.py)
- [Create a client bot and get a token](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
- In a file called `discord_token.py`, place your client token in there (see template)

### Usage

All bot operations start with `!raffle`

`!raffle help` : displays all of the available commands

`!raffle list` : lists all of the raffles, along with their IDs, in a server

`!raffle new mm/dd/yyyy Some reward name` : creates a new raffle

`!raffle delete ID` : deletes a given raffle

`!raffle details ID` : displays basic information for a given raffle

`!raffle run` : conducts all raffles up to today that still need to be conducted
