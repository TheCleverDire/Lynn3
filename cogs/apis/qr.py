from discord.ext import commands
from BotUtils import REST, escapeURL
import discord

class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='qr')
    async def QR(self, ctx, *, text):
        embed = discord.Embed()
        embed.set_thumbnail(url=f'https://chart.googleapis.com/chart?cht=qr&choe=UTF-8&chs=512x512&chl={escapeURL(text)}')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(QR(bot))