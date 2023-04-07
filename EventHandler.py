# dependencies
from discord.ext.commands import errors

# local modules
from Exceptions import GayBotException



'''
Handles all the event listeners.
This is mainly used for good/smart error handling
'''



async def setup(bot):
    '''
    Used by discord.commands.Bot.load_extension() to load this cog onto the bot.
    This is required to allow hot reloading with GeneralCommands.reload()
    '''
    bot.add_listener(on_command_error)
    bot.add_listener(on_command_completion)



async def on_command_error(ctx, error):
    await ctx.message.add_reaction('❌')
    if isinstance(error, errors.CommandNotFound):
        await ctx.send("That is not a recognized command. Use `gay help` for a list of commands.")
    elif isinstance(error, errors.CommandInvokeError) and isinstance(error.original, GayBotException):
        # discord.ext.commands.errors.CommandInvokeError is raised whenever another error is raised while executing a command
        # use discord.ext.commands.errors.CommandInvokeError.original to get the error raised
        # Exceptions.GayBotException is a generic exception that all other exceptions inherit from
        await ctx.send(error.original.message)
    elif isinstance(error, GayBotException):
        # this catches exceptions thrown during checks
        await ctx.send(error.message)
    else:
        raise error



async def on_command_completion(ctx):
    await ctx.message.add_reaction('☑️')