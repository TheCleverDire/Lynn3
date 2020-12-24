from discord.ext import commands
from config import statusPages
from BotUtils import REST
from datetime import datetime
import discord

class Statuspage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='status', aliases=['statuspage'])
    async def StatusAPI(self, ctx, *, name=None):
        """Gets information about status pages. Run without arguments to see supported pages"""
        if not name:
            await ctx.send('```Currently supported pages:\n' + '\n'.join([n.title() for n,u,c in statusPages]) + '```')
            return
        for page in statusPages:
            if name.lower() == page[0]:
                col = 0x00
                j = await REST(page[1] + '/index.json')
                if j['status']['indicator'] == 'none':
                    col = 0x00ff00
                elif j['status']['indicator'] == 'minor':
                    col = 0xffa500
                elif j['status']['indicator'] == 'major':
                    col = 0xff0000

                embed = discord.Embed(title=f"**{page[0].title()} Status** - {j['status']['description']}", colour=col, url=page[1])
                for comp in j['components']:
                    embed.add_field(name=comp['name'], value=comp['status'].replace('_', ' ').title())
                if page[2]:
                    # Seperate component and metric statuses by using an invisible field
                    embed.add_field(inline=False, name='\U00002063', value='\U00002063')
                    for metric in page[2]:
                        m = await REST(f"{page[1]}/metrics-display/{metric}/day.json")
                        last = m['summary']['last']
                        last = str(round(last, 2)) if last else '0'
                        embed.add_field(name=m['metrics'][0]['metric']['name'], value=last)
                embed.timestamp = datetime.utcnow()

                await ctx.send(embed=embed)

                for incident in j['incidents']:
                    if incident['status'] == 'resolved' or incident['status'] == 'completed':
                        continue
                    firstUpdate = incident['incident_updates'][-1]
                    lastUpdate = incident['incident_updates'][0]
                    if incident['status'] == 'scheduled':
                        col = 0xffa500
                    else:
                        col = 0xff0000

                    embed = discord.Embed(title='**' + incident['status'].title() + '** - ' + incident['name'], color=col)
                    if firstUpdate['affected_components']:
                        embed.add_field(name='Affected components', value='\n'.join(c['name'] for c in firstUpdate['affected_components']))
                    if firstUpdate != lastUpdate and len(firstUpdate) + len(lastUpdate) + 5 < 1900:
                        embed.description = '**' + datetime.fromisoformat(lastUpdate['created_at'].rstrip('Z')).strftime('%b %d %H:%M:%S %Y UTC%z') \
                                          + '**: ' + lastUpdate['body'] + '\n\n\n**' \
                                          + datetime.fromisoformat(firstUpdate['created_at'].rstrip('Z')).strftime('%b %d %H:%M:%S %Y UTC%z') \
                                          + '**: ' + firstUpdate['body']
                    else:
                        embed.description = firstUpdate['body']

                    if incident['scheduled_for']:
                        embed.timestamp = datetime.fromisoformat(incident['scheduled_for'].rstrip('Z'))
                        embed.set_footer(text=incident['impact'].title() + ' • Starts')
                    else:
                        embed.timestamp = datetime.fromisoformat(incident['created_at'].rstrip('Z'))
                        embed.set_footer(text=incident['impact'].title() + ' • Started')

                    await ctx.send(embed=embed)
                return


def setup(bot):
    bot.add_cog(Statuspage(bot))