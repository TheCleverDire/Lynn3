import discord
from discord.ext import commands
import json
from datetime import datetime

class Embed(commands.Cog):
    '''Embed'''

    def __init__(self, bot):
        self.bot = bot

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def embed(self, ctx, *, embedjson):
        """Turns an embed json into an embed. Use https://embed.discord.website/, https://discohook.org etc. to generate an embed.
        If you put the json in a code block, put a newline after the backticks"""
        dictionary = json.loads(self.cleanup_code(embedjson))
        if 'embed' in dictionary:
            dictionary = dictionary['embed']
        elif 'embeds' in dictionary:
            dictionary = dictionary['embeds'][0]

        if 'timestamp' in dictionary and 'T' in dictionary['timestamp']:
            dictionary['timestamp'] = datetime.fromisoformat(dictionary['timestamp'].replace('Z', ''))

        embed = discord.Embed.from_dict(dictionary)
        hook = [h for h in await ctx.channel.webhooks() if h.name == 'EmoteFix']
        if not hook:
            hook = await ctx.channel.create_webhook(name='EmoteFix')
        else:
            hook = hook[0]
        await hook.send(content='', embed=embed, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Embed(bot))