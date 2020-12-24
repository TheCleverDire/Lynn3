from discord.ext import commands
from BotUtils import REST, getAPIKey, escapeURL, getTwitchToken
from datetime import datetime
import discord

class IGDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='igdb', aliases=['game', 'games'])
    async def IGDBAPI(self, ctx, *, title):
        """Gets information about videogames using IGDB.com"""
        token = await getTwitchToken()
        
        title = title.replace("'", "\\'").replace('"', '\\"')
        exactmatch = f'where name ~ "{title}";sort url asc;'
        closematch = f'search "{title}";'
        body = '''fields name,cover.image_id,release_dates.date,release_dates.platform.name,genres.name,rating,summary,age_ratings.category,age_ratings.rating,game_modes.name,involved_companies.*,involved_companies.company.name,websites.url,url,artworks.image_id,status;
limit 1;'''

        data = await REST(f"https://api.igdb.com/v4/games", method='POST', data=exactmatch+body, headers={'Authorization': 'Bearer ' + token, 'Client-ID': getAPIKey('twitchID')})
        if not len(data):
            # Couldn't find exact match, check for close match then
            data = await REST(f"https://api.igdb.com/v4/games", method='POST', data=closematch+body, headers={'Authorization': 'Bearer ' + token, 'Client-ID': getAPIKey('twitchID')})
            if not len(data):
                raise commands.BadArgument(message='Could not find game')
        data = data[0]

        embed = discord.Embed(title=data['name'], colour=0xf5c518, url=data['url'])
        
        if 'cover' in data:
            embed.set_thumbnail(url='https://images.igdb.com/igdb/image/upload/t_original/'+data['cover']['image_id']+'.jpg')

        if 'artworks' in data:
            embed.set_image(url='https://images.igdb.com/igdb/image/upload/t_original/'+data['artworks'][0]['image_id']+'.jpg')

        if 'summary' in data:
            embed.description = data['summary']

        if 'status' in data:
            if data['status'] == 2:
                temp = 'Alpha'
            elif data['status'] == 3:
                temp = 'Beta'
            elif data['status'] == 4:
                temp = 'Early Access'
            elif data['status'] == 5:
                temp = 'Offline'
            elif data['status'] == 6:
                temp = 'Cancelled'
            elif data['status'] == 7:
                temp = 'Rumored'
            embed.add_field(name='Status', value=temp)

        if 'rating' in data:
            embed.add_field(name='Rating', value=f"{round(data['rating'], 2)}/100")

        if 'release_dates' in data:
            # [(date, platform names),]
            releases = []
            for date in data['release_dates']:
                new = True
                if 'date' in date:
                    human = datetime.fromtimestamp(date['date']).strftime('%Y-%m-%d')
                else:
                    human = 'TBD'
                for release in releases:
                    if date['platform']['name'] == release[1]:
                        # Don't show duplicate platform names
                        new = False
                    elif human == release[0]:
                        release[1] += ', '+date['platform']['name']
                        new = False
                if new:
                    releases.append([human, date['platform']['name']])
            temp = []
            for release in sorted(releases):
                temp.append(f"**{release[1]}** ({release[0]})")
            embed.add_field(name='Platforms', value='\n'.join(temp), inline=False)

        if 'involved_companies' in data:
            temp = []
            for company in data['involved_companies']:
                roles = []
                if company['developer']:
                    roles.append('Developer')
                if company['publisher']:
                    roles.append('Publisher')
                if company['porting']:
                    roles.append('Porting')
                if company['supporting']:
                    roles.append('Supporting')
                temp.append(f"**{company['company']['name']}** ({' & '.join(roles)})")
            embed.add_field(name='Developers', value='\n'.join(temp), inline=False)

        if 'age_ratings' in data:
            temp = []
            for rating in data['age_ratings']:
                if rating['category'] == 1:
                    tmp = '**ESRB** '
                elif rating['category'] == 2:
                    tmp = '**PEGI** '
                else:
                    raise Exception()

                # TODO: Clean this code up im too lazy rn
                if rating['rating'] == 1:
                    tmp += '3+'
                elif rating['rating'] == 2:
                    tmp += '7+'
                elif rating['rating'] == 3:
                    tmp += '12+'
                elif rating['rating'] == 4:
                    tmp += '16+'
                elif rating['rating'] == 5:
                    tmp += '18+'
                elif rating['rating'] == 6:
                    tmp += 'Rating Pending'
                elif rating['rating'] == 7:
                    tmp += 'Early Childhood'
                elif rating['rating'] == 8:
                    tmp += 'Everyone'
                elif rating['rating'] == 9:
                    tmp += 'Everyone 10+'
                elif rating['rating'] == 10:
                    tmp += 'Teen'
                elif rating['rating'] == 11:
                    tmp += 'Mature'
                elif rating['rating'] == 12:
                    tmp += 'Adults Only'
                temp.append(tmp)
            embed.add_field(name='Age Ratings', value='\n'.join(temp))

        if 'genres' in data:
            temp = []
            for genre in data['genres']:
                temp.append(genre['name'])
            embed.add_field(name='Genres', value='\n'.join(temp))

        if 'game_modes' in data:
            temp = []
            for gamemode in data['game_modes']:
                temp.append(gamemode['name'])
            embed.add_field(name='Game Modes', value='\n'.join(temp))

        if 'websites' in data:
            temp = []
            for website in data['websites']:
                temp.append(website['url'])
            embed.add_field(name='External Links', value='\n'.join(temp[:3]))

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(IGDB(bot))