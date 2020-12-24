from discord.ext import commands
from BotUtils import REST, getAPIKey, escapeURL, isURL
import discord
from datetime import datetime

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='news')
    async def NewsAPI(self, ctx, *, query):
        """Gets news"""
        data = await REST(f"http://newsapi.org/v2/everything?qInTitle={escapeURL(query)}&from={datetime.now().strftime('%Y-%m-%d')}&sortBy=popularity&pageSize=1&apiKey={getAPIKey('newsapi')}")

        if len(data['articles']) == 0:
            await ctx.send('No articles found.')
            return
        data = data['articles'][0]
        embed = discord.Embed(colour=0xf5c518)
        embed.title = data['title']
        embed.url = data['url']
        embed.description = data['description']
        embed.timestamp = datetime.fromisoformat(data['publishedAt'].replace('Z',''))
        if 'urlToImage' in data and isURL(str(data['urlToImage'])):
            embed.set_image(url=data['urlToImage'])
        embed.set_footer(text=f"{data['source']['name']} | Written by {data['author']}. Published ")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(News(bot))
