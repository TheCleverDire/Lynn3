import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import re
import time
from config import uptime
import subprocess
import sys
from BotUtils import splitMessage, shellCommand

'''Misc commands'''


class Misc(commands.Cog):
    '''Misc'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['col', 'color', 'colour'])
    async def hex(self, ctx, *, col):
        hexcol = str(col).replace('#', '')
        if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hexcol):
            raise commands.CommandError(message='Invalid hex color')

        embed = discord.Embed(title='#'+hexcol, colour=int(hexcol, 16))
        r = int(hexcol[:2], 16)
        rp = round(int(hexcol[:2], 16) / 2.55, 2)
        g = int(hexcol[2:4], 16)
        gp = round(int(hexcol[2:4], 16) / 2.55, 2)
        b = int(hexcol[4:6], 16)
        bp = round(int(hexcol[4:6], 16) / 2.55, 2)
        embed.description = f'**Red** = **{str(r)}** (**{str(rp)}%**)\n**Green** = **{str(g)}** (**{str(gp)}%**)\n**Blue** = **{str(b)}** (**{str(bp)}%**)'
        await ctx.send(embed=embed, content='')

    @commands.command(aliases=['id'])
    async def snowflake(self, ctx, *, snowflake):
        # HACK: Parse mentions by just removing everything that's not a digit
        snowflake = ''.join(c for c in snowflake if c.isdigit())
        snowflake = int(snowflake)
        embed = discord.Embed(title=f'Snowflake {snowflake}', colour=0x7289DA)
        embed.description = f'''**Timestamp**: {datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000) / 1000).strftime('%c')}
                                **Internal worker ID**: {str((snowflake & 0x3E0000) >> 17)}
                                **Internal process ID**: {str((snowflake & 0x1F000) >> 12)}
                                **Increment**: {str(snowflake & 0xFFF)}'''
        await ctx.send(embed=embed, content='')

    @commands.command()
    async def whois(self, ctx, *, domain):
        """Whois"""
        if not sys.platform.startswith('linux'):
            await ctx.send("This command is only usable when the bot is hosten on linux. Sorry!")
            return
        await shellCommand(ctx, ['whois', domain], realtime=False)

    def getOutput(self, command, shell=False):
        return subprocess.check_output(command, stderr=subprocess.PIPE, shell=shell).decode('utf-8')

    @commands.cooldown(1, 120)
    @commands.command(name='ping', aliases=['hostinfo'])
    async def ping(self, ctx, *message):
        if not sys.platform.startswith('linux'):
            embed = discord.Embed(title='Pong!', colour=0xfffdd0)
            embed.description = f'{str(round(self.bot.latency*1000, 2))}ms'
            await ctx.send(embed=embed, content='')
            return
        hostname = self.getOutput(['hostname'])
        uname = self.getOutput(['uname', '-a'])
        hostuptime = self.getOutput(['uptime', '-p'])
        temperature = self.getOutput(['sensors | grep ° | head -1'], shell=True)
        ram = self.getOutput(['free -m | grep Mem | awk \'{print ($3 "\057" $2 " MB")}\''], shell=True)
        cpu = self.getOutput(["mpstat | awk '$12 ~ /[0-9.]+/ { print 100 - $12 \"%\"}'"], shell=True)

        embed = discord.Embed(title=f'Pong! {round(self.bot.latency*1000, 2)}ms', colour=0xfffdd0)
        embed.set_author(name=hostname)
        embed.add_field(name="Current Time", value=f"🕒 {datetime.now().isoformat()}", inline=False)
        embed.add_field(name="System", value=f"ℹ️ {uname}", inline=False)
        embed.add_field(name="Uptime", value=f"🖥️**System**: {hostuptime} \n 🤖**Bot**: {datetime.now()-uptime}", inline=False)
        embed.add_field(name='Temperature', value=f"🔥 {temperature}")
        embed.add_field(name="Memory", value=f"💾 {ram}", inline=False)
        embed.add_field(name='CPU', value=f"🎚️ {cpu}", inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))