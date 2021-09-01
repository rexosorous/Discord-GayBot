class GayBotException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = f':no_entry_sign: {message}'

class EmojiNotFound(GayBotException):
    def __init__(self):
        super().__init__('Could not find that emoji in this server. Try checking your spelling and don\'t include the colons.')

class UserNotInVoiceChannel(GayBotException):
    def __init__(self):
        super().__init__('You must be in a voice channel to use that command.')

class UserNotInSameVoiceChannel(GayBotException):
    def __init__(self):
        super().__init__('You must be in the same voice channel as me to use that command.')

class NotInteger(GayBotException):
    def __init__(self):
        super().__init__('Only integers allowed.')

class NotInQueue(GayBotException):
    def __init__(self):
        super().__init('That number does not represent an item in the queue.')