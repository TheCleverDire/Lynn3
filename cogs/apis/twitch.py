from discord.ext import commands
from BotUtils import REST, getAPIKey, escapeURL, getTwitchToken
from datetime import datetime
import discord

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append('%s %s%s' % (period_value, period_name, has_s))

        return ', '.join(strings)

    @commands.command(name='twitch')
    async def TwitchAPI(self, ctx, *, user):
        """Gets information about twitch users"""
        token = await getTwitchToken()
        data = await REST(f"https://api.twitch.tv/helix/users?login={escapeURL(user)}", headers={'Authorization': 'Bearer ' + token, 'Client-ID': getAPIKey('twitchID')})
        data = data['data'][0]
        stream = await REST(f"https://api.twitch.tv/helix/streams?user_login={escapeURL(user)}", headers={'Authorization': 'Bearer ' + token, 'Client-ID': getAPIKey('twitchID')})
        live = True
        try:
            stream = stream['data'][0]
        except:
            live = False

        name = data['display_name']
        if data['login'].lower() != data['display_name'].lower():
            name = data['display_name'] + ' (' + data['login'] + ')'

        embed = discord.Embed(title='Twitch - ' + name, color=0x6441A4, url='https://twitch.tv/' + data['login'])

        embed.set_thumbnail(url=data['profile_image_url'])

        if live:
            embed.set_image(url=stream['thumbnail_url'].replace('{width}','1920').replace('{height}','1080'))
        elif data['offline_image_url']:
            embed.set_image(url=data['offline_image_url'])

        if data['broadcaster_type']:
            utype = data['broadcaster_type'].title()
            if data['type']:
                utype += '\n' + data['type'].title()
            embed.add_field(name='User Type', value=utype)

        if data['description']:
            embed.add_field(name='Description', value=data['description'])
        embed.add_field(name='Total views', value=str(data['view_count']))

        if live:
            embed.add_field(name='Currently '+stream['type'], value=f"Title: **{stream['title']}**", inline=False)
            embed.add_field(name='Current viewers', value=stream['viewer_count'])
            embed.add_field(name='Live for', value=self.td_format(datetime.now() - datetime.fromisoformat(stream['started_at'][:-1])))

        embed.set_footer(icon_url='https://static.twitchcdn.net/assets/favicon-32-d6025c14e900565d6177.png', text='User ID ' + data['id'])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Twitch(bot))