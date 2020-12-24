from discord.ext import commands
from datetime import datetime
import discord
import typing

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60),
            ('second',      1)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append('%s %s%s' % (period_value, period_name, has_s))

        return ', '.join(strings)

    UserFlags = {
        'UserFlags.staff': '<:staff:720576645345574913> Discord Staff',
        'UserFlags.partner': '<:partner:720576779554783253> Discord Partner',
        'UserFlags.hypesquad': '<:hypesquad:720576880733847562> HypeSquad Events',
        'UserFlags.bug_hunter': '<:hypesquad:720576880733847562> Bug Hunter',
        'UserFlags.hypesquad_bravery': '<:bravery:720576989265789001> HypeSquad Bravery',
        'UserFlags.hypesquad_brilliance': '<:brilliance:720579240050950144> HypeSquad Brilliance',
        'UserFlags.hypesquad_balance': '<:balance:720579490924986379> HypeSquad Balance',
        'UserFlags.early_supporter': '<:earlysupporter:720577134627782716> Early Supporter',
        'UserFlags.team_user': 'Team User',
        'UserFlags.system': '<:system:720579663134720001> System',
        'UserFlags.bug_hunter_level_2': '<:bughunter2:720577058027208817> Bug Hunter Level 2',
        'UserFlags.verified_bot': '<:verifiedbot:720579572537753630> Verified Bot',
        'UserFlags.verified_bot_developer': '<:botdev:720579320531124235> Verified Bot Developer',
        'UserFlags.bot': '<:bot:720579762795577416> Bot'
    }

    Status = {
        'online': 'Online',
        'idle': 'Idle',
        'dnd': 'Do Not Disturb',
        'offline': 'Offline',
        'invisible': 'Invisible'
    }

    MobileStatus = {
        'online': 'Online',
        'idle': 'Idle',
        'dnd': 'Do Not Disturb'
    }

    ActivityTypes = {
        'ActivityType.unknown': 'unknown',
        'ActivityType.playing': 'Playing',
        'ActivityType.streaming': 'Streaming',
        'ActivityType.listening': 'Listening to',
        'ActivityType.watching': 'Watching',
        'ActivityType.custom': ''
    }

    @commands.command(name='user', aliases=['userinfo'])
    async def userinfo(self, ctx, *, user: typing.Union[discord.Member, None]):
        if not user:
            user = ctx.author
        embeds = []
        embed = discord.Embed()
        embed.set_author(name=f"{user.name}#{user.discriminator}")
        embed.set_thumbnail(url=user.avatar_url)

        globalinfo = []
        globalinfo.append(f"Mention: {user.mention}")
        globalinfo.append(f"ID: {user.id}")
        globalinfo.append(f"Account created: {user.created_at.strftime('%c')}")
        globalinfo.append(f"Account created: {self.td_format(datetime.utcnow() - user.created_at)} ago")

        serverinfo = []
        serverinfo.append(f"Nickname: {user.nick}")
        serverinfo.append(f"Joined server: {user.joined_at.strftime('%c')}")
        serverinfo.append(f"Joined server: {self.td_format(datetime.utcnow() - user.joined_at)} ago")
        serverinfo.append(f"Highest role: {user.roles[-1].mention}")
        serverinfo.append(f"All roles: {', '.join(list(map(lambda x: x.mention, user.roles[::-1])))}")
        if user.premium_since:
            serverinfo.append(f"Boosting server since {user.joined_at.strftime('%c')}")

        embed.color = user.roles[-1].color

        flags = []
        for flag in user.public_flags.all():
            # Awful code, I know.
            flags.append(self.UserFlags.get(str(flag), str(flag)))

        if user.bot:
            flags.append(self.UserFlags['UserFlags.bot'])

        statusinfo = []
        if user.is_on_mobile():
            statusinfo.append(self.MobileStatus.get(str(user.status), str(user.status)))
        else:
            statusinfo.append(self.Status.get(str(user.status), str(user.status)))

        for activity in user.activities:
            if type(activity) is not discord.Spotify and type(activity) is not discord.Streaming:
                statusinfo.append(f"{self.ActivityTypes.get(str(activity.type), str(activity.type))} {activity.name}")

        embed.add_field(name='Global Information', value='\n'.join(globalinfo), inline=False)
        embed.add_field(name='Server Information', value='\n'.join(serverinfo), inline=False)
        embed.add_field(name='Status', value='\n'.join(statusinfo), inline=False)
        if flags:
            embed.add_field(name='Public Badges', value='\n'.join(flags), inline=False)

        embeds.append(embed)

        for activity in user.activities:
            if type(activity) is discord.Spotify:
                embed = discord.Embed(title=activity.name, color=activity.color)
                embed.url = f"https://open.spotify.com/track/{activity.track_id}"
                embed.description = f"Listening to {activity.title} by {','.join(activity.artists)}\n\n`{self.td_format(datetime.utcnow()-activity.start)}` / `{self.td_format(activity.duration)}`"
                embed.set_thumbnail(url=activity.album_cover_url)
                embeds.append(embed)
            elif type(activity) is discord.Streaming:
                #embed = discord.Embed(title=)
                pass

        for embed in embeds:
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(UserInfo(bot))