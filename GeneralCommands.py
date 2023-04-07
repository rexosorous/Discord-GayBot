# standard libraries
import json
from random import randint

# dependencies
from discord import Color, Embed
from discord.ext import commands

# local modules
from Exceptions import *



async def setup(bot):
    '''
    Used by discord.commands.Bot.load_extension() to load this cog onto the bot.
    This is required to allow hot reloading with GeneralCommands.reload()
    '''
    await bot.add_cog(GeneralCommands(bot))



class GeneralCommands(commands.Cog):
    '''
    Holds all the general use commands.
    '''
    STAR_FILE = 'gold_stars.json'

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
        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        pretty_data.set_image(url=server_emojis[emoji_name])
        await ctx.send(embed=pretty_data)
        await ctx.message.delete()



    @commands.command()
    async def mock(self, ctx, user):
        '''
        Mocks a user by randomizing the capitilzation in that user's last message

        Args:
            user (str)
        '''
        user = ctx.message.mentions[0]

        # pretty output using embed
        pretty_data = Embed()
        pretty_data.color = Color.green()
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



    @commands.group(name='star', aliases=['goldstar'], case_insensitive=True, invoke_without_command=True)
    async def star(self, ctx):
        '''
        Command group for star command so that commands look like
        gay star leaderboard
        gay star give @user 2
        Defaults to showing the leaderboard
        '''
        await self.star_list(self, ctx)



    @star.command(name='leaderboard', aliases=['list', 'show'])
    async def star_list(self, ctx):
        '''
        Shows the leaderboard/full list of users with gold stars ordered by gold star count

        Note:
            Is part of a group so is invoked similarly to 'star leaderboard'
        '''
        with open(self.STAR_FILE, 'r') as file:
            star_data = json.load(file)

        output = ''
        for record in sorted(star_data.items(), key=lambda data: data[1], reverse=True):    # sort by star count
            username = await ctx.guild.fetch_member(int(record[0]))
            output += f'{username}: {record[1]} ⭐\n' # prettify

        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name='⭐ Star Leaderboard ⭐')
        pretty_data.description = output
        await ctx.send(embed=pretty_data)



    @star.command(name='check')
    async def star_check(self, ctx, user=None):
        '''
        Shows how many gold stars a user has

        Args:
            user (str, optional): must be an @ mention!! if not given, will default to checking message author's stars

        Note:
            Is part of a group so is invoked similarly to 'star check @user'
        '''
        with open(self.STAR_FILE, 'r') as file:
            star_data = json.load(file)

        user = await ctx.guild.fetch_member(user[3:-1]) if user else ctx.author # if user arg not given, use author
        user_id_str = str(user.id)      # this is necessary becuase json format cannot have ints has keys and converts them to strings when using json.dump()
        if user_id_str not in star_data:
            star_data[user_id_str] = 0

        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        pretty_data.description = f'⭐ {star_data[user_id_str]} Gold Stars ⭐'
        await ctx.send(embed=pretty_data)



    @commands.has_permissions(kick_members=True) # checks if user is a mod because only mods should be able to kick members
    @star.command(name='give', aliases=['award', 'add'])
    async def star_give(self, ctx, user, amount=1):
        '''
        Gives gold stars to a user

        Args:
            user (str): must be an @ mention!!
            amount (str, optional): the amount of stars to give to the user. defaults to 1

        Note:
            Is part of a group so is invoked similarly to 'star give @user <amount>'
        '''
        with open(self.STAR_FILE, 'r') as file:
            star_data = json.load(file)

        user = await ctx.guild.fetch_member(user[3:-1])
        user_id_str = str(user.id)      # this is necessary becuase json format cannot have ints has keys and converts them to strings when using json.dump()
        if user_id_str not in star_data:
            star_data[user_id_str] = 0
        star_data[user_id_str] += int(amount)

        with open(self.STAR_FILE, 'w') as file:
            json.dump(star_data, file)

        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name=user.display_name, icon_url=ctx.user.avatar_url)
        pretty_data.description = f'⭐ Now has {star_data[user_id_str]} Gold Stars ⭐'
        await ctx.send(embed=pretty_data)



    @commands.has_permissions(kick_members=True) # checks if user is a mod because only mods should be able to kick members
    @star.command(name='remove', aliases=['rm', 'sub', 'subtract'])
    async def star_remove(self, ctx, user, amount=1):
        '''
        Removes gold stars to a user

        Args:
            user (str): must be an @ mention!!
            amount (str, optional): the amount of stars to give to the user. defaults to 1

        Note:
            Is part of a group so is invoked similarly to 'star remove @user <amount>'
            Just calls self.star_give() with a negative number so logic isn't repeated twice
        '''
        await self.star_give(ctx, user, int(amount)*-1)



    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx):
        '''
        Hot reloads all the command cogs so the bot doesn't need to be shut down to enact changes

        Note:
            Can only be used by me.
        '''
        instances = self.bot.get_cog('VoiceCommands').get_instances()
        await self.bot.reload_extension('GeneralCommands')
        await self.bot.reload_extension('VoiceCommands')
        await self.bot.reload_extension('EventHandler')
        self.bot.get_cog('VoiceCommands').load_instances(instances)



    @commands.is_owner()
    @commands.command(aliases=['die', 'murder', 'strangle'])
    async def kill(self, ctx):
        '''
        Gracefully stops the bot

        Note:
            Can only be used by me.
        '''
        await self.bot.get_cog('VoiceCommands').kill()
        await self.bot.close()