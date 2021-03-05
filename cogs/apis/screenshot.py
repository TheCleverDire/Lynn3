from discord.ext import commands
from BotUtils import REST, escapeURL, getAPIKey
from io import BytesIO
import discord
import aiohttp

class Screenshot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="screenshot")
    async def screenshot(self, ctx, *, url, size="1920x1080"):
        if not url.startswith("http"):
            url = "http://" + url
        # Download file to website.png
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.screenshotlayer.com/api/capture?viewport=" + size + "&access_key=" + getAPIKey("screenshotlayer") + "&url=" + url) as r:
                with open("website.png", "wb") as f:
                    f.write(await r.read())
        shot = discord.File("website.png", filename="website.png")
        await ctx.send(files=[shot])

def setup(bot):
    bot.add_cog(Screenshot(bot))