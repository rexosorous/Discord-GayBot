# dependencies
from discord import Game
from discord.ext import commands

# local modules
from GeneralCommands import GeneralCommands
from VoiceCommands import VoiceCommands

'''
DEPENDENCIES:
    discord.py[voice]
    ffmpeg.exe to be placed in ./ffmpeg/
    fuzzywuzzy
    python-levenshtein
'''


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='gay ', help_command=None, activity=Game(name='gay help'))
    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')

    bot.add_cog(GeneralCommands(bot))
    bot.add_cog(VoiceCommands(bot))

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)