# dependencies
from discord import Game
from discord.ext import commands

# local modules
from GeneralCommands import GeneralCommands

'''
DEPENDENCIES:
    discord.py
    PyNaCl
    ffmpeg be installed to PATH
    fuzzywuzzy
    difflib
    python-levenshtein
'''


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='gay ', help_command=None, activity=Game(name='gay help'))
    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')

    bot.add_cog(GeneralCommands(bot))

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)