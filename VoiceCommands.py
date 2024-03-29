# standard libraries
from asyncio import sleep
from enum import Enum
import logging
from os import listdir
from random import choice

# dependencies
from discord import Color, Embed, FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from fuzzywuzzy import fuzz
from yt_dlp import YoutubeDL

# local modules
from Exceptions import *



async def setup(bot):
    '''
    Used by discord.commands.Bot.load_extension() to load this cog onto the bot.
    This is required to allow hot reloading with GeneralCommands.reload()
    '''
    await bot.add_cog(VoiceCommands(bot))



class AudioType(Enum):
    '''
    Simple Enum to differentiate what type of audio is being added to the queue
    '''
    YOUTUBE = 0
    SOUNDBOARD = 1



class VoiceCommands(commands.Cog):
    '''
    Holds all the voice-channel related commands
    Things like playing youtube videos or soundboard

    Attributes:
        FFMPEG_OPTIONS (dict): options sent to ffmpeg
        instances (dict): following this format
            {
                discord.Guild.id (int): {
                    'voice': discord.VoiceClient,
                    'queue': [{
                            'type': AudioType,
                            'source': str,          # url or dir
                            'title': str,
                            'duration': int,        # seconds
                            'thumbnail_url': str,
                            'video_url': str]       # youtube webpage
                        }],
                    'loop_audio': bool
                }
            }

    '''
    def __init__(self, bot):
        self.bot = bot
        self.instances = dict()
        self.logger = logging.getLogger('discord')



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
                'queue': list(),
                'loop_audio': False
            }



    # used to preserve the bot's current state when reloading the extension
    def get_instances(self) -> dict:
        return self.instances
    def load_instances(self, instances):
        self.instances = instances



####################################################################################################################################
# GENERIC FUNCTIONS
####################################################################################################################################

    def get_audio_object(self, clip_data: dict) -> FFmpegPCMAudio:
        '''
        Converts the clip link/dir to be played into an discord.FFMpegPCMAudio object used for playing audio.

        Args:
            clip_data (dict): see self.instances[discord.Guild.id]['queue'][0]

        Returns:
            audio_clip (discord.FFmpegPCMAudio)
        '''
        if clip_data['type'] == AudioType.YOUTUBE:
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', # this prevents the bot from prematurely disconnecting if it loses connection for a short period of time
                'options': '-vn -af loudnorm=I=-16:LRA=11:TP=-2.5'  # this normalizes the volume so things aren't overly loud or quiet
            }
            audio_clip = FFmpegPCMAudio(clip_data['source'], executable=r'C:\ffmpeg\bin\ffmpeg.exe', **ffmpeg_options)
            audio_clip = PCMVolumeTransformer(audio_clip, volume=0.3)
            return audio_clip

        if clip_data['type'] == AudioType.SOUNDBOARD:
            ffmpeg_options = {'options': '-af loudnorm=I=-16:LRA=11:TP=-2.5'}   # this normalizes the volume so things aren't overly loud or quiet
            audio_clip = FFmpegPCMAudio(clip_data['source'], executable=r'C:\ffmpeg\bin\ffmpeg.exe', **ffmpeg_options)
            audio_clip = PCMVolumeTransformer(audio_clip, volume=0.3)
            return audio_clip



    async def play_next(self, ctx):
        '''
        A recursive function that plays all the audio clips in the queue
        If there are no more audio clips in the queue, it disconnects

        Note:
            NOT A COMMAND
        '''
        if self.instances[ctx.guild.id]['queue']:
            clip_data = self.instances[ctx.guild.id]['queue'][0]

            # pretty output using embed
            pretty_data = Embed()
            pretty_data.title = clip_data['title']
            pretty_data.color = Color.green()
            if self.instances[ctx.guild.id]['loop_audio']:
                pretty_data.set_author(name='Now Playing on Repeat 🔂', icon_url='https://i.imgur.com/8zZGsGQ.png')
            else:
                pretty_data.set_author(name='Now Playing', icon_url='https://i.imgur.com/8zZGsGQ.png')
            if clip_data['type'] == AudioType.YOUTUBE:
                pretty_data.url = clip_data['video_url']
                pretty_data.description = f'Length: {int(clip_data["duration"]/60)}m {int(clip_data["duration"]%60)}s'
                pretty_data.set_thumbnail(url=clip_data['thumbnail_url'])
            else:
                # if this is a soundboard clip
                pretty_data.description = 'Length: This is a soundboard clip and I\'m too lazy to code in the length. It should be over soon anyways.'

            # still pretty output stuff
            if len(self.instances[ctx.guild.id]['queue']) > 1:
                next_clip = self.instances[ctx.guild.id]['queue'][1]
                val = f'[{next_clip["title"]}]({next_clip["video_url"]})' if next_clip['type'] == AudioType.YOUTUBE else next_clip['title']
                pretty_data.add_field(name='Up Next', value=val)
            else:
                pretty_data.add_field(name='Up Next', value='This is the last video in the queue')
            await ctx.send(embed=pretty_data)

            # actually play audio
            self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] playing {clip_data["title"]}...')
            self.instances[ctx.guild.id]['voice'].play(self.get_audio_object(clip_data))
            # waits 3 seconds between clips so it doesn't just play back to back
            while self.instances[ctx.guild.id]['voice'].is_playing(): # this while loop is needed like this because discord.VoiceClient.play is not asynchronous for some reason
                await sleep(0.5)
            await sleep(3)

            # don't pop from queue unless the 'loop' feature is on
            if not self.instances[ctx.guild.id]['loop_audio']:
                if self.instances[ctx.guild.id]['queue']:
                    self.instances[ctx.guild.id]['queue'].pop(0)
            await self.play_next(ctx)
        else:
            await self.instances[ctx.guild.id]['voice'].disconnect()



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
        voice = self.instances[ctx.guild.id]['voice']
        if voice and voice.is_connected():
            if voice.channel == ctx.message.author.voice.channel:
                # if the bot is already playing audio and the user invoking the command is in the same voice channel, add to queue but don't call self.play_next()
                self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] bot is already in the voice channel')
                self.instances[ctx.guild.id]['queue'].append(clip_data)

                # pretty output using embed
                pretty_data = Embed()
                pretty_data.title = clip_data['title']
                pretty_data.color = Color.green()
                pretty_data.set_author(name='Added to Queue', icon_url='https://i.imgur.com/zRn90U1.png')
                pretty_data.set_footer(text=f'To undo, use "gay queue remove last" or "gay queue remove {len(self.instances[ctx.guild.id]["queue"])-1}"')
                if clip_data['type'] == AudioType.YOUTUBE:
                    pretty_data.url = clip_data['video_url']
                    pretty_data.description = f'Length: {clip_data["duration"]//60}m {clip_data["duration"]%60}s'
                    pretty_data.set_thumbnail(url=clip_data['thumbnail_url'])
                else:
                    # if this is a soundboard clip
                    pretty_data.description = 'Length: This is a soundboard clip and I\'m too lazy to code in the length. It should be over soon anyways.'
                await ctx.send(embed=pretty_data)
            else:
                # if the bot is already playing audio and the user invoking the command is NOT in the same voice channel, throw and error
                raise UserNotInSameVoiceChannel
        else:
            # if the bot isn't playing audio and the user invoking the command is in any voice channel, join the channel and start playing
            self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] joining channel {ctx.message.author.voice.channel}')
            self.instances[ctx.guild.id]['queue'].append(clip_data)
            self.instances[ctx.guild.id]['voice'] = await ctx.message.author.voice.channel.connect()
            await self.play_next(ctx)



    @is_user_in_same_VC()
    @is_bot_in_VC()
    @is_user_in_VC()
    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        '''
        Skips the currently playing audio clip if there is one
        '''
        self.instances[ctx.guild.id]['voice'].stop()
        if self.instances[ctx.guild.id]['loop_audio']:
            self.instances[ctx.guild.id]['queue'].pop(0)



    @commands.group(name='loop', aliases=['repeat', 'replay'], case_insensitive=True, invoke_without_command=True)
    async def loop(self, ctx):
        '''
        Toggles the loop feature which will always loop the first audio clip in the queue.

        Note:
            You can still use commands like skip to move on to the next clip while keeping loop enabled.
        '''
        if self.instances[ctx.guild.id]['voice'] and self.instances[ctx.guild.id]['voice'].is_connected(): # if the bot is in a voice channel
            if not ctx.message.author.voice:
                raise UserNotInVoiceChannel

            if ctx.message.author.voice.channel != self.instances[ctx.guild.id]['voice'].channel:
                raise UserNotInSameVoiceChannel

        if not self.instances[ctx.guild.id]['loop_audio']:
            await ctx.send(':repeat_one: Looping is now enabled :repeat_one:')
            self.instances[ctx.guild.id]['loop_audio'] = True
        else:
            await ctx.send('Looping is now **disabled**')
            self.instances[ctx.guild.id]['loop_audio'] = False



    @loop.command(name='check', aliases=['show', 'status'])
    async def check_loop(self, ctx):
        '''
        Shows whether or not audio looping is enabled
        '''
        if self.instances[ctx.guild.id]['loop_audio']:
            await ctx.send(':repeat_one: Looping is enabled :repeat_one:')
        else:
            await ctx.send('Looping is **disabled**')



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
        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name='Queue', icon_url='https://i.imgur.com/1P4LiHx.png')
        for clip_data in self.instances[ctx.guild.id]['queue']:
            title = f'[{clip_data["title"]}]({clip_data["video_url"]})' if clip_data['type'] == AudioType.YOUTUBE else clip_data["title"]
            line = f'`#{self.instances[ctx.guild.id]["queue"].index(clip_data)}:` {title}'
            queue_list.append(line)
        if queue_list:
            pretty_data.description = '\n'.join(queue_list)
            pretty_data.set_footer(text=f'To remove something, use "gay queue remove <index>"')
        else:
            pretty_data.description = 'There are no items in the queue.'
            pretty_data.set_footer(text='To add something to the queue, use "gay play <video>" or "gay soundboard <clip>"')
        await ctx.send(embed=pretty_data)



    @is_user_in_same_VC()
    @is_bot_in_VC()
    @is_user_in_VC()
    @queue.command(name='clear')
    async def clear_queue(self, ctx):
        '''
        Clears all items from the clip queue

        Note:
            Is part of a group so is invoked similarly to 'queue clear'
        '''
        self.instances[ctx.guild.id]['queue'] = list()



    @is_user_in_same_VC()
    @is_bot_in_VC()
    @is_user_in_VC()
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
        if index.lower() in ['first', 'next']:
            index = 0
        elif index.lower() in ['last', 'end']:
            index = -1
        try:
            index = int(index)
            self.instances[ctx.guild.id]['queue'].pop(index)
        except ValueError:
            raise NotInteger
        except IndexError:
            raise NotInQueue



    @is_user_in_same_VC()
    @is_bot_in_VC()
    @is_user_in_VC()
    @commands.command(aliases=['leave', 'kick', 'fuckoff'])
    async def stop(self, ctx):
        '''
        Stops playing audio and disconnects from the voice channel
        '''
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
            voice = self.instances[guild]['voice']
            if voice:
                voice.stop()
                await voice.disconnect()



####################################################################################################################################
# SOUNDBOARD FUNCTIONS
####################################################################################################################################

    @is_user_in_VC()
    @commands.group(aliases=['sb', 'clip'], case_insensitive=True, invoke_without_command=True)
    async def soundboard(self, ctx, *search_term):
        '''
        Adds a soundboard clip to the queue and starts playing the queue if necessary

        Args:
            search_term (tuple[str])
        '''
        search_term = ' '.join(search_term)

        # using fuzzywuzzy, choose the soundboard clip that best matches the search terms
        best_clip = ''
        best_confidence = 0
        for clip in listdir('soundboard/'):
            fixed_clip = clip[:-4]
            confidence = fuzz.token_set_ratio(search_term, fixed_clip)
            if confidence > best_confidence:
                best_confidence = confidence
                best_clip = clip

        data = {
            'type': AudioType.SOUNDBOARD,
            'source': f'soundboard/{best_clip}',
            'title': f'{best_clip[:-4]} (soundboard)'
        }
        self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] got soundboard clip: {data["title"]}')
        await self.join_and_play(ctx, data)



    @is_user_in_VC()
    @soundboard.command(name='cliproulette', aliases=['roulette', 'random', 'rand', 'rando'])
    async def clip_roulette(self, ctx):
        '''
        Randomly selects a soundboard clip, adds it to the queue, and starts playing the queue if necessary

        Note:
            Is part of a group so is invoked similarly to 'gay soundboard random'
        '''
        all_clips = listdir('soundboard/')
        filename = choice(all_clips)
        data = {
            'type': AudioType.SOUNDBOARD,
            'source': f'soundboard/{filename}',
            'title': f'{filename[:-4]} (soundboard)'
        }
        self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] got soundboard clip: {data["title"]}')
        await self.join_and_play(ctx, data)



    @soundboard.command(name='checksoundboard', aliases=['help', 'check', 'names', 'list', 'ls', 'show'])
    async def check_soundboard(self, ctx):
        '''
        Shows all the clips that the soundboard can play

        Note:
            Is part of a group so is invoked similarly to 'gay soundboard list'
        '''
        # pretty output using embed
        pretty_data = Embed()
        pretty_data.color = Color.green()
        pretty_data.set_author(name=':information_source: Soundboard Clips', icon_url='https://i.imgur.com/1P4LiHx.png')
        clip_list = listdir('soundboard/')
        pretty_data.description = '\n'.join(clip_list)
        pretty_data.set_footer(text=f'To play a soundboard clip, use "gay soundboard <clip>"')
        await ctx.send(embed=pretty_data)



####################################################################################################################################
# YOUTUBE FUNCTIONS
####################################################################################################################################

    @is_user_in_VC()
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
            if search_term.startswith('http'):
                info = ytdl.extract_info(search_term, download=False)
            else:
                info = ytdl.extract_info(f'ytsearch:{search_term}', download=False)['entries'][0]
        url = info['url']
        data = {
            'type': AudioType.YOUTUBE,
            'source': url,
            'title': info['title'],
            'duration': info['duration'],           # in seconds
            'thumbnail_url': info['thumbnail'],
            'video_url': info['webpage_url']        # youtube webpage
        }
        self.logger.info(f'[{ctx.command.module}.{ctx.command.name}] got youtube audio: {data["title"]} | {data["video_url"]}')
        await self.join_and_play(ctx, data)