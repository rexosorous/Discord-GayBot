# standard libraries
from random import randint

# dependencies
import discord
from discord.ext import commands

# local modules
from Exceptions import *



def setup(bot):
    '''
    Used by discord.commands.Bot.load_extension() to load this cog onto the bot.
    This is required to allow hot reloading with GeneralCommands.reload()
    '''
    bot.add_cog(GeneralCommands(bot))



class GeneralCommands(commands.Cog):
    '''
    Holds all the general use commands.
    '''
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    async def bruh(self, ctx):
        '''
        Sends the bruh copy pasta
        '''
        await ctx.send(':warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:... \n\nThe :police_officer: Department of :house: Homeland :statue_of_liberty: Security :oncoming_police_car: has issued a :b:ruh Moment :warning: warning :construction: for the following districts: Ligma, Sugma, :b:ofa, and Sugondese. \n\nNumerous instances of :b:ruh moments :b:eing triggered by :eyes: cringe:grimacing: normies :toilet: have :alarm_clock: recently :clock2: occurred across the :earth_americas: continental :flag_us:United States:flag_us:. These individuals are :b:elieved to :b:e highly :gun: dangerous :knife: and should :no_entry_sign: not :x: :b:e approached. Citizens are instructed to remain inside and :lock:lock their :door:doors. \n\nUnder :x:no:no_entry: circumstances should any citizen :speak_no_evil: say "bruh" in reaction to an action performed :b:y a cringe:grimacing: normie:toilet: and should store the following items in a secure:lock: location: Jahcoins:euro:, V-bucks:yen:, Gekyume\'s foreskin:eggplant:, poop:poop: socks, juul:thought_balloon: pods, ball :cherries: crushers, and dip. \n\nRemain tuned for further instructions. \n\n:warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:...')



    @emoji_exists()
    @commands.command()
    async def emoji(self, ctx, emoji_name):
        '''
        Allows users to use server nitro-gated emojis.
        Does not send error messages unless NONE of the emojis are found.
            So if 1 emoji is found but 5 aren't, then it's still 'legal' and won't throw error messages

        args:
            emoji_names (str)
        '''
        emoji_name = emoji_name.lower()
        server_emojis = {emoji.name.lower(): emoji.url for emoji in ctx.guild.emojis}
        pretty_data = discord.Embed()
        pretty_data.color = discord.Color.green()
        pretty_data.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        pretty_data.set_image(url=server_emojis[emoji_name])
        await ctx.send(embed=pretty_data)
        await ctx.message.delete()



    @commands.command()
    async def mock(self, ctx, user):
        '''
        Mocks a user by randomizing the capitilzation in that user's last message
        '''
        user = ctx.message.mentions[0]

        # pretty output using embed
        pretty_data = discord.Embed()
        pretty_data.color = discord.Color.green()
        pretty_data.set_author(name=user.display_name, icon_url=user.avatar_url)
        pretty_data.set_image(url='https://i.imgur.com/xQu6gKd.jpg')
        async for message in ctx.channel.history(limit=50):
            if message.author == user:
                mocked = ''
                for char in message.content:
                    if randint(0, 1) == 1:
                        mocked += char.upper()
                    else:
                        mocked += char.lower()
                pretty_data.title = mocked
                break
        await ctx.send(embed=pretty_data)



    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx):
        '''
        Hot reloads all the command cogs so the bot doesn't need to be shut down to enact changes

        Note:
            Can only be used by me.
        '''
        instances = self.bot.get_cog('VoiceCommands').get_instances()
        self.bot.reload_extension('GeneralCommands')
        self.bot.reload_extension('VoiceCommands')
        self.bot.reload_extension('EventHandler')
        self.bot.get_cog('VoiceCommands').load_instances(instances)



    @commands.is_owner()
    @commands.command(aliases=['die', 'murder', 'strangle'])
    async def kill(self, ctx):
        '''
        Gracefully stops the bot

        Note:
            Can only be used by me.\
        '''
        await self.bot.get_cog('VoiceCommands').kill()
        await self.bot.close()