import discord
from discord.ext import commands
import requests
from datetime import datetime
import base64
import json
import math

class APIs:
    """APIs"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.message.guild.id != 485076757733572608

    async def getAPI(self, url):
        r = requests.get(url=url)
        return(r.json())

    # ----
    # CLASSICUBE
    # ----
    
    @commands.command(name='classicube', aliases=['cc'])
    async def classiCubeAPI(self, ctx, *, user=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave as blank for general statistics"""
        message = await ctx.send('\N{HOURGLASS}')
        if user:
            data = await APIs.getAPI(self, 'https://www.classicube.net/api/player/'+user)
            if data["error"] != "":
                data = await APIs.getAPI(self, 'https://www.classicube.net/api/id/'+user)
                if data["error"] != "":
                    await message.edit(content='User not found!')
                    return

            flags = []
            if 'b' in data["flags"]:
                flags.append('Banned from forums')
            if 'd' in data["flags"]:
                flags.append('Developer')
            if 'm' in data["flags"]:
                flags.append('Forum moderator')
            if 'a' in data["flags"]:
                flags.append('Forum admin')
            if 'e' in data["flags"]:
                flags.append('Blog editor')
            
            embed = discord.Embed(title='ClassiCube User', colour=0x9873ac)
            embed.set_author(name=data["username"],
                icon_url='https://www.classicube.net/face/'+data["username"]+'.png')
            embed.add_field(name='ID', value=data["id"])
            if flags:
                embed.add_field(name='Flags', value=', '.join(flags))
            embed.add_field(name='Registered on', value=datetime.utcfromtimestamp(data["registered"]).strftime('%c'))
            
            embed.set_footer(text='|', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.timestamp = datetime.utcnow()
            await message.edit(embed=embed, content='')
            return                
        else:
            data = await APIs.getAPI(self, 'https://www.classicube.net/api/players/')
            players = ''
            for p in data["lastfive"]:
                players += str(p) + '\n'
            embed = discord.Embed(title='ClassiCube', colour=0x9873ac)
            embed.add_field(name='Total Players', value=data["playercount"])
            embed.add_field(name='Last five accounts', value=players)

            embed.set_footer(text='|', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.timestamp = datetime.utcnow()
            await message.edit(embed=embed, content='')
    
    # ----
    # MINECRAFT
    # ----

    async def getMinecraftAgeCheck(self, name, num):
        r = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name + '?at=' + str(num))
        if r.status_code == 200:
            return True
        return False

    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        lastfail = 0
        for i in range(30):
            if a == b:
                ok = await APIs.getMinecraftAgeCheck(self, name, a)
                if ok and lastfail == a-1:
                    return datetime.utcfromtimestamp(a).strftime('%c')
                else:
                    return  '???'
            else:
                mid = a + math.floor( ( b - a ) / 2)
                ok = await APIs.getMinecraftAgeCheck(self, name, mid)
                if ok:
                    #print('range: ' + str(a) + '\t<-| \t' + str(b))
                    b = mid
                else:
                    #print('range: ' + str(a) + '\t |->\t' + str(b))
                    a = mid+1
                    lastfail = mid

    async def getMinecraftSales(self):
        payload = '{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}'
        r = requests.post(url='https://api.mojang.com/orders/statistics', data=payload)
        return(r.json())
    
    async def getMinecraftUUID(self, name):
        r = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name)
        if r.status_code == 200:
            return(r.json())
        
        r2 = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name + "?at=0")
        if r2.status_code == 200:
            return(r2.json())
            
        return(None)
    
    async def getMinecraftSkinUrl(self, uuid):
        r = requests.get(url='https://sessionserver.mojang.com/session/minecraft/profile/' + uuid)
        data = r.json()
        val = data["properties"][0]["value"]
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    @commands.command(name='minecraft', aliases=['mc'])
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        message = await ctx.send('\N{HOURGLASS}')
        try:
            if user:
                uuid = await APIs.getMinecraftUUID(self, user)
                if not uuid:
                    await message.edit(content='User not found!')
                    return
                history = await APIs.getAPI(self, 'https://api.mojang.com/user/profiles/' + uuid["id"] + '/names')
                names = []
                for i in range(len(history)):
                    names.append(history[i]["name"])
                    names[i] = names[i].replace('*', '\*').replace('_', '\_').replace('~', '\~')
                names.reverse()
                names[0] += " **[CURRENT]**"

                created = await APIs.getMinecraftAge(self, user)

                skin = await APIs.getMinecraftSkinUrl(self, uuid["id"])
                embed = discord.Embed(title='Minecraft User', colour=0x82540f)
                embed.set_author(name=history[-1]["name"], 
                                icon_url='https://crafatar.com/avatars/' + uuid["id"])
                embed.set_image(url='https://crafatar.com/renders/body/' + uuid["id"] + '.png')
                embed.add_field(name='Name history', value='\n'.join(names))
                embed.add_field(name='UUID', value=uuid["id"])
                embed.add_field(name='Skin URL', value='[Click me]('+skin["textures"]["SKIN"]["url"]+')')
                embed.add_field(name='Account created', value=created)
                embed.set_footer(text='|', icon_url='https://minecraft.net/favicon-96x96.png')
                embed.timestamp = datetime.utcnow()
                await message.edit(embed=embed, content="")
            else:
                sale = await APIs.getMinecraftSales(self)
                embed = discord.Embed(title='Minecraft', colour=0x82540f)
                embed.add_field(name='Sold total', value=sale["total"])
                embed.add_field(name='Sold in the last 24h', value=sale["last24h"])

                embed.set_footer(text='|', icon_url='https://minecraft.net/favicon-96x96.png')
                embed.timestamp = datetime.utcnow()
                await message.edit(embed=embed, content="")
        except Exception:
            await message.edit(content='\N{NO ENTRY SIGN}')

def setup(bot):
    bot.add_cog(APIs(bot))
