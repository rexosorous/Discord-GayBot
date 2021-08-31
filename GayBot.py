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
    '''
    essentially a main.py file
    '''
    bot = commands.Bot(command_prefix='gay ', activity=Game(name='gay help'))
    bot.add_cog(GeneralCommands(bot))
    bot.add_cog(VoiceCommands(bot))

    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')
        await bot.get_cog('VoiceCommands').init_guilds()

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)