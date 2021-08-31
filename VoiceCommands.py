# standard libraries
import asyncio
import random
from os import listdir
 
# dependencies
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

# local modules
import utilities as util



class VoiceCommands(commands.Cog):
    '''
    Holds all the voice-channel related commands
    Things like playing youtube videos or soundboard

    Attributes:
        FFMPEG_OPTIONS (dict): options sent to ffmpeg
        instances (dict): following this format
            {
                discord.Guild.id (int): {
                    'voice': discord.AudioSource,
                    'queue': [{
                            'ffmpeg': discord.AudioSource,
                            'title': str,
                            'duration': int,        # seconds
                            'thumbnail_url': str,
                            'audio_url': str,       # raw audio url
                            'video_url': str]       # youtube webpage
                        }]  # if it's a soudnboard clip, it will only have ffmpeg and title fields
                }
            }
        voice (discord.VoiceClient): is set to None on first init
        queue (list[dict]): has the data for each clip to be played. the dicts have the form:
            {
                'ffmpeg': discord.AudioSource,
                'title': str,
                'duration': int,        # seconds
                'thumbnail_url': str,
                'audio_url': str,       # raw audio url
                'video_url': str]       # youtube webpage
            }
            note that soundboard audio clips will only have the first 2 fields
        
    '''
    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTIONS = {'executable': 'ffmpeg/ffmpeg.exe'}  # so the end user doesn't have to have ffmpeg installed to PATH
        self.instances = dict()



    async def init_guilds(self):
        '''
        Inits self.instances with all the guilds that the bot is a part of.
        This is done here instead of in self.__init__() because an instance of this class is created before the bot connects to discord and has knowledge of which guilds it is a part of.
        So this is called after the bot is ready and has this knowledge (see GayBot.py's on_ready())

        Note:
            This is only fetched once at the beginning of the bot's life. If the bot joins other servers during runtime, a KeyError will be thrown whenever
            someone tries to ues voice functionalities.
        '''
        for guild in self.bot.guilds:
            self.instances[guild.id] = {
                'voice': None,
                'queue': list()
            }



####################################################################################################################################
# GENERIC FUNCTIONS
####################################################################################################################################

    async def bot_is_connected(self, ctx):
        if not self.instances[ctx.guild.id]['voice']:
            return False
        return self.instances[ctx.guild.id]['voice'].is_connected()

    async def user_in_channel(self, ctx):
        if ctx.message.author.voice:
            return True
        await ctx.send(':no_entry_sign: You must be in a voice channel to use that command.')
        return False

    async def user_in_same_channel(self, ctx):
        if ctx.message.author.voice.channel == self.instances[ctx.guild.id]['voice'].channel:
            return True
        await ctx.send(':no_entry_sign: You must be in the same voice channel as me to use that command.')
        return False



    async def play_next(self, ctx):
        '''
        A recursive function that plays all the audio clips in the queue
        If there are no more audio clips in the queue, it disconnects

        Note:
            NOT A COMMAND
        '''
        if self.instances[ctx.guild.id]['queue']:
            clip_data = self.instances[ctx.guild.id]['queue'].pop(0)
            
            # pretty output using embed
            pretty_data = discord.Embed()
            pretty_data.title = clip_data['title']
            pretty_data.color = discord.Color.green()
            pretty_data.set_author(name='Now Playing', icon_url='https://i.imgur.com/8zZGsGQ.png')
            if 'audio_url' in clip_data:
                # if this is a youtube video
                pretty_data.url = clip_data['video_url']
                pretty_data.description = f'Length: {int(clip_data["duration"]/60)}m {int(clip_data["duration"]%60)}s'
                pretty_data.set_thumbnail(url=clip_data['thumbnail_url'])
            else:
                # if this is a soundboard clip
                pretty_data.description = 'Length: This is a soundboard clip and I\'m too lazy to code in the length. It should be over soon anyways.'

            if self.instances[ctx.guild.id]['queue']:
                next_clip = self.instances[ctx.guild.id]['queue'][0]
                val = f'[{next_clip["title"]}]({next_clip["video_url"]})' if 'audio_url' in next_clip else next_clip['title']
                pretty_data.add_field(name='Up Next', value=val)
            else:
                pretty_data.add_field(name='Up Next', value='This is the last video in the queue')
            await ctx.send(embed=pretty_data)

            self.instances[ctx.guild.id]['voice'].play(clip_data['ffmpeg'])
            # waits 3 seconds between clips so it doesn't just play back to back
            while self.instances[ctx.guild.id]['voice'].is_playing(): # this while loop is needed like this because discord.VoiceClient.play is not asynchronous for some reason
                await asyncio.sleep(0.5)
            await asyncio.sleep(3)
            await self.play_next(ctx)
        else:
            await self.stop(ctx)



    async def join_and_play(self, ctx, clip_data):
        '''
        Does all the preparations needed to start playing audio.
        1. Determines if the bot should even play audio (ie. if the command is legal)
            a command is legal if:
            the invoker is in a voice channel AND 
            (the bot is not already in a voice channel OR 
            the invoker is in the same voice channel)
        2. Joins a voice channel if the bot isn't already in one
        3. Adds a clip to the queue
        4. Displays confirmation message to chat if adding to queue (ie. not the first video to be played)
        5. Starts playing clips if the bot isn't already doing so

        Args:
            clip_data (dict): see self.instances for dict format

        Note:
            NOT A COMMAND
        '''
        if not await self.user_in_channel(ctx):
            return

        if await self.bot_is_connected(ctx):
            if await self.user_in_same_channel(ctx):
                # if the bot is already playing audio and the user invoking the command is in the same voice channel
                self.instances[ctx.guild.id]['queue'].append(clip_data)
                await ctx.message.add_reaction('☑️')

                # pretty output using embed
                pretty_data = discord.Embed()
                pretty_data.title = clip_data['title']
                pretty_data.color = discord.Color.green()
                pretty_data.set_author(name='Added to Queue', icon_url='https://i.imgur.com/zRn90U1.png')
                pretty_data.set_footer(text=f'To undo, use "gay queue remove last" or "gay queue remove {len(self.instances[ctx.guild.id]["queue"])-1}"')
                if 'audio_url' in clip_data:
                    # if this is a youtube video
                    pretty_data.url = clip_data['video_url']
                    pretty_data.description = f'Length: {int(clip_data["duration"]/60)}m {int(clip_data["duration"]%60)}s'
                    pretty_data.set_thumbnail(url=clip_data['thumbnail_url'])
                else:
                    # if this is a soundboard clip
                    pretty_data.description = 'Length: This is a soundboard clip and I\'m too lazy to code in the length. It should be over soon anyways.'
                await ctx.send(embed=pretty_data)
        else:
            # if the bot isn't playing audio and the user invoking the command is in any voice channel
            self.instances[ctx.guild.id]['queue'].append(clip_data)
            await ctx.message.add_reaction('☑️')
            self.instances[ctx.guild.id]['voice'] = await ctx.message.author.voice.channel.connect()
            await self.play_next(ctx)



    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        '''
        Skips the currently playing audio clip if there is one
        '''
        if not await self.user_in_channel(ctx) or not await self.bot_is_connected(ctx) or not await self.user_in_same_channel(ctx):
            return
        self.instances[ctx.guild.id]['voice'].stop()
        await ctx.message.add_reaction('☑️')



    @commands.group(name='queue', aliases=['q'], case_insensitive=True, invoke_without_command=True)
    async def queue(self, ctx):
        '''
        Really just a command group so self.check_queue and self.clear_queue are more intuitive in their invocations
        In the event that this is called, default to self.check_queue
        '''
        await self.check_queue(ctx)



    @queue.command(name='check', aliases=['list', 'ls', 'show'])
    async def check_queue(self, ctx):
        '''
        Shows all items in the clip queue

        Note:
            Is part of a group so is invoked similarly to 'queue check'
        '''
        # pretty output using embed
        queue_list = list()
        pretty_data = discord.Embed()
        pretty_data.color = discord.Color.green()
        pretty_data.set_author(name='Queue', icon_url='https://i.imgur.com/1P4LiHx.png')
        for clip_data in self.instances[ctx.guild.id]['queue']:
            title = f'[{clip_data["title"]}]({clip_data["video_url"]})' if 'audio_url' in clip_data else clip_data["title"]
            line = f'`#{self.instances[ctx.guild.id]["queue"].index(clip_data)}:` {title}'
            queue_list.append(line)
        if queue_list:
            pretty_data.description = '\n'.join(queue_list)
            pretty_data.set_footer(text=f'To remove something, use "gay queue remove <index>"')
        else:
            pretty_data.description = 'There are no items in the queue.'
            pretty_data.set_footer(text='To add something to the queue, use "gay play <video>" or "gay soundboard <clip>"')
        await ctx.send(embed=pretty_data)



    @queue.command(name='clear')
    async def clear_queue(self, ctx):
        '''
        Clears all items from the clip queue

        Note:
            Is part of a group so is invoked similarly to 'queue clear'
        '''
        if not await self.user_in_channel(ctx) or not await self.bot_is_connected(ctx) or not await self.user_in_same_channel(ctx):
            return
        self.instances[ctx.guild.id]['queue'] = list()
        await ctx.message.add_reaction('☑️')



    @queue.command(name='remove', aliases=['rm', 'delete', 'del'])
    async def remove_from_queue(self, ctx, index):
        '''
        Removes one item from the clip queue based on index

        Args:
            index (int or str): the index of the clip to be removed
                can also be 'first', 'next', 'last', or 'end'

        Note:
            Is part of a group so is invoked similarly to 'queue remove'
        '''
        if not await self.user_in_channel(ctx) or not await self.bot_is_connected(ctx) or not await self.user_in_same_channel(ctx):
            return
        if index.lower() in ['first', 'next']:
            index = 0
        elif index.lower() in ['last', 'end']:
            index = -1
        try:
            index = int(index)
            self.instances[ctx.guild.id]['queue'].pop(index)
            await ctx.message.add_reaction('☑️')
        except ValueError:
            await ctx.send(':no_entry_sign: only integers allowed')
        except IndexError:
            await ctx.send(':no_entry_sign: that number does not represent an item in the queue')



    @commands.command(aliases=['leave', 'kick', 'fuckoff'])
    async def stop(self, ctx):
        '''
        Stops playing audio and disconnects from the voice channel
        '''
        if not await self.user_in_channel(ctx) or not await self.bot_is_connected(ctx) or not await self.user_in_same_channel(ctx):
            return
        self.instances[ctx.guild.id]['voice'].stop()
        self.instances[ctx.guild.id]['queue'] = list()
        await self.instances[ctx.guild.id]['voice'].disconnect()



    async def kill(self):
        '''
        Gracefully stops the voice bot and disconnects from all servers.

        Note:
            NOT A COMMAND
        '''
        for guild in self.instances:
            if voice := self.instances[guild]['voice']:
                voice.stop()
                await voice.disconnect()



####################################################################################################################################
# SOUNDBOARD FUNCTIONS
####################################################################################################################################

    @commands.group(aliases=['sb', 'clip'], case_insensitive=True, invoke_without_command=True)
    async def soundboard(self, ctx, *search_term):
        '''
        Adds a soundboard clip to the queue and starts playing the queue if necessary

        Args:
            search_term (tuple[str])
        '''
        search_term = ' '.join(search_term)
        filename = util.get_clip(search_term)
        audio_clip = discord.FFmpegPCMAudio(f'soundboard/{filename}', **self.FFMPEG_OPTIONS)
        data = {
            'ffmpeg': audio_clip,
            'title': f'{filename[:-4]} (soundboard)'
        }
        await self.join_and_play(ctx, data)



    @soundboard.command(name='cliproulette', aliases=['roulette', 'random', 'rand', 'rando'])
    async def clip_roulette(self, ctx):
        '''
        Randomly selects a soundboard clip, adds it to the queue, and starts playing the queue if necessary

        Note:
            Is part of a group so is invoked similarly to 'gay soundboard random'
        '''
        all_clips = listdir('soundboard/')
        filename = random.choice(all_clips)
        audio_clip = discord.FFmpegPCMAudio(f'soundboard/{filename}', **self.FFMPEG_OPTIONS)
        data = {
            'ffmpeg': audio_clip,
            'title': f'{filename[:-4]} (soundboard)'
        }
        await self.join_and_play(ctx, data)
        


    @soundboard.command(name='checksoundboard', aliases=['help', 'check', 'names', 'list', 'ls', 'show'])
    async def check_soundboard(self, ctx):
        '''
        Shows all the clips that the soundboard can play

        Note:
            Is part of a group so is invoked similarly to 'gay soundboard list'
        '''
        # pretty output using embed
        pretty_data = discord.Embed()
        pretty_data.color = discord.Color.green()
        pretty_data.set_author(name=':information_source: Soundboard Clips', icon_url='https://i.imgur.com/1P4LiHx.png')
        clip_list = listdir('soundboard/')
        pretty_data.description = '\n'.join(clip_list)
        pretty_data.set_footer(text=f'To play a soundboard clip, use "gay soundboard <clip>"')
        await ctx.send(embed=pretty_data)

        

####################################################################################################################################
# YOUTUBE FUNCTIONS
####################################################################################################################################

    @commands.command(name='play', aliases=['yt', 'youtube', 'music'])
    async def search_youtube(self, ctx, *search_term):
        '''
        Searches youtube and selects the top-most video to play

        Args:
            search_term (tuple[str])

        Note:
            A cookiefile saved as 'cookies.txt' is required to play sensitive videos
        '''
        search_term = ' '.join(search_term)
        yt_options = {'verbose': 'False', 'format': 'bestaudio', 'noplaylist': 'True', 'cookiefile': 'cookies.txt'}
        with YoutubeDL(yt_options) as ytdl:
            info = ytdl.extract_info(f'ytsearch:{search_term}', download=False)['entries'][0]
        url = info['url']
        ffmpeg_addtl_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}    # this prevents the bot from prematurely disconnecting if it loses connection for a short period of time
        audio_clip = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS, **ffmpeg_addtl_options)
        audio_clip_volume = discord.PCMVolumeTransformer(audio_clip, volume=0.3)
        data = {
            'ffmpeg': audio_clip_volume,
            'title': info['title'],
            'duration': info['duration'],           # in seconds
            'thumbnail_url': info['thumbnail'],
            'audio_url': info['url'],               # raw audio url
            'video_url': info['webpage_url']        # youtube webpage
        }
        await self.join_and_play(ctx, data)