from discord.ext import commands
from BotUtils import REST, escapeURL, getAPIKey
from io import BytesIO
import discord
import aiohttp

class WolframAlpha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wolframalpha', aliases=['wa', 'wolfram'])
    async def wolframalpha(self, ctx, *, query):
        res = await REST(f"http://api.wolframalpha.com/v1/simple?appid={getAPIKey('wolframalpha')}&layout=labelbar&ip=None&background=2F3136&foreground=white&i={escapeURL(query)}", returns=('raw', 'status'))
        data = BytesIO(res[0])
        if res[1] == 501:
            raise commands.ArgumentParsingError(data.read().decode('utf-8'))
        elif res[1] != 200:
            raise commands.CommandError(data.read().decode('utf-8'))
        answer = discord.File(data, filename='wolfram.png')
        await ctx.send(files=[answer])

def setup(bot):
    bot.add_cog(WolframAlpha(bot))