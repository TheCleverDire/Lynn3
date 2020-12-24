from discord.ext import commands
from BotUtils import REST, escapeURL
import discord
import re

class Mediawiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mediawiki(self, ctx, query, apiURL, full, introOnly=True, safe=False):
        # Assuming the user knows what they are looking for by using srwhat=nearmatch
        search = await REST(f"{apiURL}?action=query&list=search&format=json&srwhat=nearmatch&utf8&srsearch={escapeURL(query)}")
        if not search['query']['search']:
            # No matches found, guess what the user meant
            search = await REST(f"{apiURL}?action=query&list=search&format=json&utf8&srsearch={escapeURL(query)}")
            # Check if user is just stupid and can't spell properly
            if not search['query']['search']:
                if 'suggestionsnippet' in search['query']['searchinfo']:
                    await ctx.send('No results found. Did you mean: {}?'.format(search['query']['searchinfo']['suggestionsnippet'].replace('<em>', '__').replace('</em>', '__')))
                else:
                    await ctx.send('No results found.')
                return

        pageID = search['query']['search'][0]['pageid']

        props = []
        getProps = await REST(f"{apiURL}?action=paraminfo&modules=query+info|query+pageimages|query+extracts&format=json&utf8")
        if 'modules' in getProps['paraminfo']:
            for module in getProps['paraminfo']['modules']:
                props.append(module['name'])

        if 'info' not in props:
            raise commands.CommandError(message="Wiki doesn't support required API modules")

        params = ''
        if 'info' in props:
            params += '&inprop=url|displaytitle'
        if 'pageimages' in props:
            params += '&piprop=original&pilicense=any'
        if 'extracts' in props:
            params += '&exlimit=1&explaintext'

        # FIXME: pageimages, extracts deprecated on fandom/gamepedia/wikia
        # TODO: Don't rely on TextExtracts by stripping html manually (?)

        info = await REST(f"{apiURL}?action=query&meta=siteinfo&prop={'|'.join(props)}{params}&format=json&utf8&redirects&pageids={pageID}")
        # Get "first" page with an unknown pageID
        page = list(info['query']['pages'].values())[0]

        embed = discord.Embed(title=f"{page['title']} - {info['query']['general']['sitename']}", color=0x32cd32, url=page['fullurl'])

        totalchars = 0
        totalchars += len(embed.title)

        if 'pageimages' in props:
            try:
                if safe or (not ctx.guild or ctx.channel.is_nsfw()):
                    embed.set_image(url=page['original']['source'])
            except:
                pass

        if 'extracts' in props:
            extract = page['extract'].replace('\\t', '')
            r = re.compile('([^=])(==\\s)(.+?)(\\s==)')
            m = [m for m in r.finditer(extract)]
            if m:
                desclength = min(m[0].start(), 2048)
            else:
                desclength = 2048

            embed.description = extract[:desclength]
            totalchars += len(embed.description)

            if full:
                for i in range(len(m)):
                    nex = None if i+1 == len(m) else m[i+1].start()
                    val = extract[m[i].end():nex]
                    if val.strip() and len(val)+len(m[i].group(3))+totalchars < 6000:
                        embed.add_field(name=m[i].group(3), value=val.strip()[:1024], inline=False)
                        totalchars += len(val)+len(m[i].group(3))

        await ctx.send(embed=embed)

    @commands.command(name='wiki', aliases=['wikipedia'])
    async def wiki(self, ctx, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, 'https://en.wikipedia.org/w/api.php', full)

    @commands.command(name='wiktionary', aliases=['dictionary', 'define'])
    async def wiktionary(self, ctx, *, query):
        """Displays summary of the wiki article."""
        full = True
        await self.mediawiki(ctx, query, 'https://en.wiktionary.org/w/api.php', full)

    @commands.command(name='wikilanguage', aliases=['wikil', 'wikilang'])
    async def wikilanguage(self, ctx, lang, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, f"https://{lang}.wikipedia.org/w/api.php", full)

    @commands.command(name='wiktionarylanguage', aliases=['wiktionarylang', 'dictionarylanguage', 'dictionarylang', 'definelang', 'definelanguage'])
    async def wiktionarylanguage(self, ctx, lang, *, query):
        """Displays summary of the wiki article."""
        full = True
        await self.mediawiki(ctx, query, f"https://{lang}.wiktionary.org/w/api.php", full)

    @commands.command(name='wikibooks', aliases=['wikibook', 'book', 'books'])
    async def wikibooks(self, ctx, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, 'https://en.wikibooks.org/w/api.php', 'Wikibooks', full)

    @commands.command(name='wikibookslanguage', aliases=['wikibookslang', 'wikibooklanguage', 'wikibooklang', 'bookslanguage', 'bookslang', 'booklanguage', 'booklang'])
    async def wikibookslanguage(self, ctx, lang, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, f"https://{lang}.wikibooks.org/w/api.php", full)

    @commands.command(name='fandom')
    async def fandom(self, ctx, wiki, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, f"https://{wiki}.fandom.com/api.php", full)

    @commands.command(name='gamepedia')
    async def gamepedia(self, ctx, wiki, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, f"https://{wiki}.gamepedia.com/api.php", full)

    @commands.command(name='wikia')
    async def wikia(self, ctx, wiki, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, f"https://{wiki}.wikia.org/api.php", full)

    @commands.command(name='mcwiki', aliases=['minecraftwiki'])
    async def mcwiki(self, ctx, *, query):
        """Displays summary of the wiki article.
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        await self.mediawiki(ctx, query, 'https://minecraft.gamepedia.com/api.php', full, safe=True)

    @commands.command(name='customwiki', aliases=['cwiki'])
    async def customwiki(self, ctx, url, *, query):
        """Displays summary of the wiki article.
        URL should be base url for api.php. Usually https://[domain]/w/ or https://[domain]/
        If "--full " is passed into the query, as much as possible will be shown"""
        full = False
        if query.startswith('--full '):
            query = query.replace('--full ', '', 1)
            full = True
        if url[-1] != '/':
            url += '/'
        await self.mediawiki(ctx, query, url+'/api.php', url, full)


    # TODO: Bulbapedia doesn't return pageIDs in searches

def setup(bot):
    bot.add_cog(Mediawiki(bot))