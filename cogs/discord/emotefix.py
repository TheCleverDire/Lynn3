import discord
from discord.ext import commands
import re


class EmoteFix(commands.Cog):
    '''EmoteFix'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command:
            return

        replaced = []
        shouldSend = False
        newmsg = message.content
        match = re.findall('(?=[^:\\s]*):\\S+?:(?=[^:\\s]*)', message.content)
        if match:
            for emote in match:
                if not re.search('<a:\\S+:\\d{18}>', message.content) and not emote in replaced:
                    em = emote.replace(':', '')
                    for e in message.guild.emojis:
                        if e.name.lower() == em.lower():
                            prefix = ''
                            if not e.animated:
                                # TODO: Emotes from other servers
                                continue
                            else:
                                prefix = 'a'
                            fullemote = f'<{prefix}:{str(em)}:{str(e.id)}>'
                            newmsg = newmsg.replace(emote, fullemote)
                            replaced.append(emote)
                            shouldSend = True

        match = re.findall('\\[.+]\\(<?https?://.+\\..+\\)', message.content)
        if match or shouldSend:
            hook = [h for h in await message.channel.webhooks() if h.name == 'EmoteFix']
            if not hook:
                hook = await message.channel.create_webhook(name='EmoteFix')
            else:
                hook = hook[0]
            newmsg = newmsg.replace('@here', '@\U00002063here').replace('@everyone', '@\U00002063everyone')
            await hook.send(content=newmsg, username=message.author.display_name, avatar_url=message.author.avatar_url)
            await message.delete()

def setup(bot):
    bot.add_cog(EmoteFix(bot))