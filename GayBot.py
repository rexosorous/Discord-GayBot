# dependencies
from discord import Game
from discord.ext import commands



if __name__ == '__main__':
    '''
    essentially a main.py file
    '''
    bot = commands.Bot(command_prefix='gay ', activity=Game(name='gay help'))
    bot.load_extension('GeneralCommands')
    bot.load_extension('VoiceCommands')
    bot.load_extension('EventHandler')

    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')
        await bot.get_cog('VoiceCommands').init_guilds()

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)