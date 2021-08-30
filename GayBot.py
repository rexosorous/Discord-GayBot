# dependencies
from discord.ext import commands


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='gay ', help_command=None, activity=discord.Game(name='gay help'))
    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')

    with open('login.token', 'r') as file:
        token = file.read()
    bot.run(token)