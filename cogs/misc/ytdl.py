import discord
from discord.ext import commands
import youtube_dl
from typing import Union
import os
'''ytdl'''

class ytdl(commands.Cog):
    '''ytdl'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['youtube-dl', 'ytdl', 'dl', 'download'])
    #@commands.cooldown(1, 45, commands.BucketType.user)
    async def youtubedl(self, ctx, videolink, options=None):
        """Downloads a video
        options = [video_only/audio_only]"""
        ydl_opts = {
            'geo_bypass': True,
            'no_color': True,
            #'quiet': True,
            'max_filesize': 8000000,
            'outtmpl': '%(id)s.%(ext)s',
            'restrictfilenames': True
        }

        if options == 'video_only':
            ydl_opts['format'] = 'bestvideo'
        elif options == 'audio_only':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }]
        else:
            ydl_opts['format'] = 'best[filesize<8M]/' + \
                      'best/' + \
                      'bestvideo+bestaudio/' + \
                      'bestvideo[filesize<8M]/' + \
                      'bestaudio'

        try:
            formatcode = None
            filename = None
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videolink, download=False)
                if 'is_live' in info and info['is_live']:
                    raise commands.BadArgument('Cannot download a livestream')

                if options != 'audio_only' and 'formats' in info and info['formats'] and 'filesize' in info['formats'][0] and info['formats'][0]['filesize']:
                    biggest = 0
                    for formats in info['formats']:
                        if not formats['filesize'] or not formats['width']:
                            continue
                        if formats['filesize'] < 8000000 and formats['filesize'] > biggest:
                            biggest = formats['filesize']
                    for formats in info['formats']:
                        if formats['filesize'] == biggest:
                            if not formats['acodec'] or formats['acodec'] == 'none':
                                formatcode = formats['format_id'] + '+worstaudio'
                            else:
                                formatcode = formats['format_id']

            if formatcode:
                ydl_opts['format'] = formatcode

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videolink)
                if options == 'audio_only':
                    filename = info['id']+'.mp3'
                elif 'ext' in info:
                    filename = info['id']+'.'+info['ext']
                else:
                    # Just pray it's mp4, too lazy to fix
                    filename = info['id']+'.mp4'
                file = discord.File(filename)
                await ctx.send(file=file)
        except FileNotFoundError:
            raise youtube_dl.DownloadError('Could not download video. It is most likely too large for discord (max 8MB)')
        except Exception as e:
            raise e
        finally:
            if filename and os.path.exists(filename):
                os.remove(filename)

def setup(bot):
    bot.add_cog(ytdl(bot))