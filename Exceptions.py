# dependencies
from discord.ext import commands



####################################################################################################################################
# CHECKS
####################################################################################################################################

def emoji_exists():
    def predicate(ctx):
        emoji = ctx.message.content.split(' ')[-1].lower()
        if emoji not in [ele.name.lower() for ele in ctx.guild.emojis]:
            raise EmojiNotFound
        return True
    return commands.check(predicate)

def is_bot_in_VC():
    def predicate(ctx):
        voice = ctx.bot.get_cog('VoiceCommands').get_instances()
        if not voice[ctx.guild.id]['voice'] or not voice[ctx.guild.id]['voice'].is_connected():
            raise BotNotInVoiceChannel
        return True
    return commands.check(predicate)

def is_user_in_VC():
    def predicate(ctx):
        if not ctx.message.author.voice:
            raise UserNotInVoiceChannel
        return True
    return commands.check(predicate)

def is_user_in_same_VC():
    def predicate(ctx):
        voice = ctx.bot.get_cog('VoiceCommands').get_instances()
        if ctx.message.author.voice.channel != voice[ctx.guild.id]['voice'].channel:
            raise UserNotInSameVoiceChannel
        return True
    return commands.check(predicate)



####################################################################################################################################
# EXCEPTIONS
####################################################################################################################################

class GayBotException(commands.errors.CommandError):
    def __init__(self, message):
        super().__init__()
        self.message = f':no_entry_sign: {message}'

class EmojiNotFound(GayBotException):
    def __init__(self):
        super().__init__('Could not find that emoji in this server. Try checking your spelling and don\'t include the colons.')

class UserNotInVoiceChannel(GayBotException):
    def __init__(self):
        super().__init__('You must be in a voice channel in this server to use that command.')

class UserNotInSameVoiceChannel(GayBotException):
    def __init__(self):
        super().__init__('You must be in the same voice channel as me to use that command.')

class NotInteger(GayBotException):
    def __init__(self):
        super().__init__('Only integers allowed.')

class NotInQueue(GayBotException):
    def __init__(self):
        super().__init__('That number does not represent an item in the queue.')

class BotNotInVoiceChannel(GayBotException):
    def __init__(self):
        super().__init__('You can\'t do that. The bot isn\'t even playing anything.')  