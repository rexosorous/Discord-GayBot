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
    def __init__(self, bot):
        self.bot = bot
        self.voice = None   # only None when init. should be discord.VoiceClient otherwise
        self.queue = list() # should be list of discord.AudioSource most likely created from discord.FFmpegPCMAudio
        self.FFMPEG_OPTIONS = {'executable': 'ffmpeg/ffmpeg.exe'}  # so the end user doesn't have to have ffmpeg installed to PATH
 


#########################################
# GENERIC FUNCTIONS
#########################################

    async def play_next(self):
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
        checks if the bot needs to join a channel
        checks if the user is even in a vc to being with
        checks if the user is in the same vc as the bot (if the bot is connected to one)
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
        self.voice.stop()



    @commands.command(name='checkqueue', aliases=['queue', 'q', 'checkq'])
    async def check_queue(self, ctx):
        msg = ''
        for index in range(len(self.queue)):
            msg += f'{index}: temp\n'
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send('there are no items in the queue')



    @commands.command(name='clearqueue', aliases=['clear', 'clearq'])
    async def clear_queue(self, ctx):
        self.queue = list()



    @commands.command(name='remove')
    async def remove_from_queue(self, ctx, index):
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
        disconnects from voice channel
        '''
        # self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        if not self.voice:
            return
        self.voice.stop()
        self.queue = list()
        await self.voice.disconnect()



#########################################
# SOUNDBOARD FUNCTIONS
#########################################

    @commands.group(aliases=['sb', 'clip'], case_insensitive=True, invoke_without_command=True)
    async def soundboard(self, ctx, *search_terms):
        '''
        joins a voice channel and plays the specified soundboard clip
        '''
        # self.logger.info(f'{ctx.author.name}: {ctx.message.content}')         
        search = ' '.join(search_terms)
        clip_dir = util.get_clip(search)
        audio_clip = discord.FFmpegPCMAudio(clip_dir, **self.FFMPEG_OPTIONS)
        data = {
            'ffmpeg': audio_clip,
            'title': clip_dir[clip_dir.find('/')+1 : -4]
        }
        await self.join_and_play(ctx, data)



    @soundboard.command(name='cliproulette', aliases=['roulette', 'random', 'rand', 'rando'])
    async def clip_roulette(self, ctx):
        '''
        randomly selects an audio clip for gay soundboard to play
        ''' 
        all_clips = listdir('soundboard/')
        selected_clip = f'soundboard/{random.choice(all_clips)}'
        audio_clip = discord.FFmpegPCMAudio(selected_clip, **self.FFMPEG_OPTIONS)
        data = {
            'ffmpeg': audio_clip,
            'title': selected_clip[:-4]
        }
        await self.join_and_play(ctx, audio_clip)
        


    @soundboard.command(name='checksoundboard', aliases=['help', 'check', 'names', 'list', 'ls'])
    async def check_soundboard(self, ctx):
        '''
        shows all the clips that the soundboard can play
        '''
        # self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        clip_names = []
        for clip in listdir('soundboard/'):
            clip_names.append(f'{clip[:-4]}')
        clip_names.sort()
        clip_names.insert(0, 'All Playable Soundboard Clips:```')
        clip_names.append('```')
        msg = '\n'.join(clip_names)
        await ctx.send(msg)

        

#########################################
# YOUTUBE FUNCTIONS
#########################################

    @commands.command(name='play', aliases=['yt', 'youtube', 'music'])
    async def search_youtube(self, ctx, *search_term):
        search_term = ' '.join(search_term)
        yt_options = {'verbose': 'False', 'format': 'bestaudio', 'noplaylist': 'True', 'cookiefile': 'cookies.txt'}
        with YoutubeDL(yt_options) as ytdl:
            info = ytdl.extract_info(f'ytsearch:{search_term}', download=False)['entries'][0]
        url = info['url']
        ffmpeg_addtl_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        audio_clip = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS, **ffmpeg_addtl_options)
        audio_clip_volume = discord.PCMVolumeTransformer(audio_clip, volume=0.3)
        data = {
            'ffmpeg': audio_clip_volume,
            'title': info['title'],
            'duration': info['duration'],
            'thumbnail_url': info['thumbnail'],
            'audio_url': info['url'],             # this is the raw audio url
            'video_url': info['webpage_url']   # this is the youtube webpage
        }
        await self.join_and_play(ctx, data)