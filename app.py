# dependencies
from discord import Game
from discord import Intents
from discord.ext import commands



if __name__ == '__main__':
    '''
    essentially a main.py file
    '''
    # permissions
    intents = Intents.default()
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.members = True
    intents.message_content = True
    intents.messages = True
    intents.reactions = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix='gay ', activity=Game(name='gay help'), intents=intents)

    @bot.event
    async def on_ready():
        await bot.load_extension('GeneralCommands')
        await bot.load_extension('VoiceCommands')
        await bot.load_extension('EventHandler')
        print(f'logged in as {bot.user.name}')
        await bot.get_cog('VoiceCommands').init_guilds()

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)