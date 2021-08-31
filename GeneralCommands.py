# dependencies
from discord.ext import commands



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



    @commands.command()
    async def emoji(self, ctx, *emoji_names):
        '''
        Allows users to use server nitro-gated emojis.
        Does not send error messages unless NONE of the emojis are found.
            So if 1 emoji is found but 5 aren't, then it's still 'legal' and won't throw error messages

        args:
            emoji_names (tuple[str])
        '''
        emoji_names = [emoji.lower() for emoji in emoji_names]
        emojis = []
        for server_emoji in await ctx.guild.fetch_emojis():
            if server_emoji.name.lower() in emoji_names:
                emojis.append(str(server_emoji))
        msg = ' '.join(emojis)

        if msg:
            await ctx.send(msg)
        else:
            await ctx.send('could not find any of those emojis')



    @commands.command()
    async def kill(self, ctx):
        '''
        Stops the bot

        Note:
            Can only be used by me.
            Yes this technically doxxes me, but whatever.
        '''
        if ctx.author.id == 158371798327492608:
            await self.bot.get_command('stop')(ctx)
            await self.bot.close()