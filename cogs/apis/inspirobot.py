from discord.ext import commands
import discord
from BotUtils import REST

class inspirobot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='inspire', aliases=['inspirobot', 'inspireme'])
    async def inspirobotAPI(self, ctx):
        """Generates an inspirational quote"""
        data = await REST('https://inspirobot.me/api?generate=true', returns='text')
        embed = discord.Embed(color=0x00af00)
        embed.set_image(url=data)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(inspirobot(bot))