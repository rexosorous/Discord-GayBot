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
        self.voice = None
        self.queue = list()
 


####################################################################################################################################
# GENERIC FUNCTIONS
####################################################################################################################################

    async def play_next(self):
        '''
        A recursive function that plays all the audio clips in the queue
        If there are no more audio clips in the queue, it disconnects

        Note:
            NOT A COMMAND
        '''
        if self.queue:
            clip_data = self.queue.pop(0)
            self.voice.play(clip_data['ffmpeg'])
            # waits 3 seconds between clips so it doesn't just play back to back
            while self.voice.is_playing(): # this while loop is needed like this because discord.VoiceClient.play is not asynchronous for some reason
                await asyncio.sleep(0.5)
            await asyncio.sleep(3)
            await self.play_next()
        else:
            await self.stop()



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
        4. Starts playing clips if the bot isn't already doing so

        Args:
            clip_data (dict): see self.queue for dict format

        Note:
            NOT A COMMAND
        '''
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            if not self.voice or not self.voice.is_connected(): # connect and start playing if the bot isn't already doing so
                self.queue.append(clip_data)
                self.voice = await channel.connect()
                await self.play_next()
            elif channel == self.voice.channel: # if the bot is already playing music and the person invoking the command is in the same channel, add the audio clip to the queue
                self.queue.append(clip_data)
            else:
                await ctx.send('please join the same channel as me')
        else:
            await ctx.send('please join a voice channel first')



    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        '''
        Skips the currently playing audio clip if there is one
        '''
        self.voice.stop()



    @commands.command(name='checkqueue', aliases=['queue', 'q', 'checkq'])
    async def check_queue(self, ctx):
        '''
        Shows all items in the clip queue
        '''
        msg = ''
        for index in range(len(self.queue)):
            msg += f'{index}: temp\n'
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send('there are no items in the queue')



    @commands.command(name='clearqueue', aliases=['clear', 'clearq'])
    async def clear_queue(self, ctx):
        '''
        Clears all items from the clip queue
        '''
        self.queue = list()



    @commands.command(name='remove')
    async def remove_from_queue(self, ctx, index):
        '''
        Removes one item from the clip queue based on index

        Args:
            index (int or str): the index of the clip to be removed
                can also be 'first', 'next', 'last', or 'end
        '''
        if index.lower() in ['first', 'next']:
            index = 0
        elif index.lower() in ['last', 'end']:
            index = -1
        try:
            index = int(index)
            self.queue.pop(index)
        except ValueError:
            await ctx.send('only integers allowed')
        except IndexError:
            await ctx.send('that number does not represent an item in the queue')



    @commands.command(aliases=['leave', 'kick', 'fuckoff'])
    async def stop(self, ctx = None):
        '''
        Stops playing audio and disconnects from the voice channel
        '''
        if not self.voice:
            return
        self.voice.stop()
        self.queue = list()
        await self.voice.disconnect()



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
            'title': filename[:-4]
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
        filename = f'soundboard/{random.choice(all_clips)}'
        audio_clip = discord.FFmpegPCMAudio(filename, **self.FFMPEG_OPTIONS)
        data = {
            'ffmpeg': audio_clip,
            'title': filename[:-4]
        }
        await self.join_and_play(ctx, data)
        


    @soundboard.command(name='checksoundboard', aliases=['help', 'check', 'names', 'list', 'ls'])
    async def check_soundboard(self, ctx):
        '''
        Shows all the clips that the soundboard can play

        Note:
            Is part of a group so is invoked similarly to 'gay soundboard list'
        '''
        clip_names = []
        for clip in listdir('soundboard/'):
            clip_names.append(f'{clip[:-4]}')
        clip_names.sort()
        clip_names.insert(0, 'All Playable Soundboard Clips:```')
        clip_names.append('```')
        msg = '\n'.join(clip_names)
        await ctx.send(msg)

        

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