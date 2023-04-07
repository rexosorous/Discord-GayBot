# standard libraries
import getopt
import logging
import logging.handlers
import sys

# dependencies
from discord import Game
from discord import Intents
from discord.ext import commands



if __name__ == '__main__':
    '''
    essentially a main.py file
    '''
    # allow the user to input their own login file with cmdline
    opts, _ = getopt.getopt(sys.argv[1:], "i:")
    token_file = 'login.token'

    for opt, arg in opts:
        if opt == '-i':
            token_file = arg

    # permissions
    intents = Intents.default()
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.members = True
    intents.message_content = True
    intents.messages = True
    intents.reactions = True
    intents.voice_states = True

    # logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)
    logging.getLogger('discord.gateway').setLevel(logging.INFO)
    file_formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name:<20}: {message}', '%Y-%m-%d %H:%M:%S', style='{')
    file_handler = logging.handlers.TimedRotatingFileHandler(filename='logs\discord.log', when='midnight')
    file_handler.setFormatter(file_formatter)
    stream_formatter = logging.Formatter('[\u001B[38;5;240m{asctime}\u001B[0m] [\u001B[38;5;184m{levelname:<8}\u001B[0m] \u001B[38;5;123m{name:<20}\u001B[0m: {message}\u001B[0m', '%Y-%m-%d %H:%M:%S', style='{') # this one just has colors added to it, but the format should be the same
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # discord bot
    bot = commands.Bot(command_prefix='gay ', activity=Game(name='gay help'), intents=intents)

    @bot.event
    async def on_ready():
        await bot.load_extension('GeneralCommands')
        await bot.load_extension('VoiceCommands')
        await bot.load_extension('EventHandler')
        logger.info(f'logged in as {bot.user.name}')
        await bot.get_cog('VoiceCommands').init_guilds()


    @bot.before_invoke
    async def on_command(ctx):
        logger.info(f'[{ctx.command.module}.{ctx.command.name}] executing...')

    with open(token_file, 'r') as file:
        token = file.read()
    bot.run(token, log_handler=None)