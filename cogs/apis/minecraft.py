from discord.ext import commands
import discord
from BotUtils import REST, headRenderer, skinRenderer2D, escapeURL
import math
from datetime import datetime
import json
import base64
import socket
import struct
import time
import io

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # thanks stackoverflow love ya
    # https://stackoverflow.com/a/13756038
    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append('%s %s%s' % (period_value, period_name, has_s))

        return ', '.join(strings)

    # Thanks wiki.vg and https://gist.github.com/ewized/97814f57ac85af7128bf
    def _unpack_varint(self, sock):
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7*i

            if not byte & 0x80:
                break

        return data

    def _pack_varint(self, data):
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if type(data) is str:
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif type(data) is int:
            return struct.pack('H', data)
        elif type(data) is float:
            return struct.pack('L', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, connection, extra_varint=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    async def getMinecraftUUID(self, name):
        r = await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}", returns=('raw', 'status'))
        if r[1] == 200:
            return json.loads(r[0])

        r = await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}?at=0", returns=('raw', 'status'))
        if r[1] == 200:
            return json.loads(r[0])
        return None

    async def getMinecraftSkinUrl(self, uuid):
        data = await REST(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        try:
            val = data['properties'][0]['value']
        except:
            return None
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    @commands.group(name='minecraft', aliases=['mc'])
    async def minecraft(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.UserInputError()

    @minecraft.command(name='player', aliases=['players', 'user', 'username'])
    async def minecraftAPI(self, ctx, *, user):
        """Searches minecraft players."""
        uuid = await self.getMinecraftUUID(user)
        if not uuid:
            raise commands.BadArgument(message='User not found')
        history = await REST(f"https://api.mojang.com/user/profiles/{uuid['id']}/names")
        names = []
        user = history[-1]['name']
        for i in range(len(history)):
            names.append(history[i]['name'])
            # Escape special markdown characters
            names[i] = names[i].replace('*', '\\*').replace('_', '\\_').replace('~', '\\~')
        names.reverse()
        names[0] += ' **[CURRENT]**'
        skin = await self.getMinecraftSkinUrl(uuid['id'])
        if not skin:
            raise commands.CommandOnCooldown(commands.BucketType.default, 10)
        embed = discord.Embed(title='Minecraft User', colour=0x82540f)
        embed.set_author(name=user)
        embed.set_thumbnail(url='attachment://head.png')
        embed.add_field(name='Name history', value='\n'.join(names), inline=False)
        embed.add_field(name='UUID', value=uuid['id'], inline=False)
        try:
            embed.add_field(name='Skin URL', value='[Click me]('+skin['textures']['SKIN']['url']+')')
            await skinRenderer2D(skin['textures']['SKIN']['url'])
            await headRenderer(skin['textures']['SKIN']['url'])
            skinFile = discord.File(f"skins/2d/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='skin.png')
            headFile = discord.File(f"skins/head/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='head.png')
        except:
            # TODO: Try to find a official steve skin in mojang's skin server
            await skinRenderer2D('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
            await headRenderer('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
            skinFile = discord.File('skins/2d/Steve_skin.png', filename='skin.png')
            headFile = discord.File('skins/head/Steve_skin.png', filename='head.png')
        embed.set_footer(text='\U00002063', icon_url='https://minecraft.net/favicon-96x96.png')
        embed.set_image(url='attachment://skin.png')
        embed.timestamp = datetime.utcnow()
        
        # Minecraft Cape
        cape = False
        if 'CAPE' in skin['textures']:
            cape = discord.Embed(title='Minecraft Cape', colour=0x82540f)
            cape.set_author(name=user, icon_url='attachment://head.png')
            cape.set_image(url=skin['textures']['CAPE']['url'])
            headFile2 = discord.File(f"skins/head/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='head.png')
        
        # Optifine Cape
        OF = False
        OFCape = await REST(f"http://s.optifine.net/capes/{user}.png", returns='status')
        if OFCape == 200:
            OF = discord.Embed(title='Optifine Cape', colour=0x82540f)
            OF.set_author(name=user, icon_url='attachment://head.png')
            OF.set_image(url=f"http://s.optifine.net/capes/{user}.png")
            headFile3 = discord.File(f"skins/head/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='head.png')
        await ctx.send(files=[skinFile, headFile], embed=embed)
        
        if cape:
            await ctx.send(file=headFile2, embed=cape)
        if OF:
            await ctx.send(file=headFile3, embed=OF)

    @minecraft.command(name='sales', aliases=['sale', 'stat', 'stats', 'statistics'])
    async def MCStats(self, ctx):
        """Gets Minecraft sales"""
        sale = await REST('https://api.mojang.com/orders/statistics', method='POST', data='{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}', headers={"content-type": "application/json"})
        embed = discord.Embed(title='Minecraft', colour=0xa4d168)
        embed.add_field(name='Sold total', value=sale['total'])
        embed.add_field(name='Sold in the last 24h', value=sale['last24h'])
        embed.add_field(name='Sold per hour', value=str(float(sale['saleVelocityPerSeconds'])*60*60))
        embed.set_footer(text='\U00002063', icon_url='https://static.wikia.nocookie.net/minecraft_gamepedia/images/3/3b/Grass_Block_(side_texture)_JE2_BE2.png')
        embed.timestamp = datetime.utcnow()
        
        sale = await REST('https://api.mojang.com/orders/statistics', method='POST', data='{"metricKeys":["item_sold_dungeons"]}', headers={"content-type": "application/json"})
        embed2 = discord.Embed(title='Minecraft Dungeons', colour=0xe57834)
        embed2.add_field(name='Sold total', value=sale['total'])
        embed2.add_field(name='Sold in the last 24h', value=sale['last24h'])
        embed2.add_field(name='Sold per hour', value=str(float(sale['saleVelocityPerSeconds'])*60*60))
        embed2.set_footer(text='\U00002063', icon_url='https://i.imgur.com/EkLm2j8.png')
        embed2.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)            

    @minecraft.command(name='server', aliases=['servers', 'ip'])
    async def mcServer(self, ctx, *, ip):
        """Gets information about a Minecraft server"""
        port = int(25565 if not ':' in ip else ip.split(':')[-1])
        ip = ip.split(':')[0]
        valid = False

        # https://gist.github.com/ewized/97814f57ac85af7128bf
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                conn.settimeout(5)
                conn.connect((ip, port))
                valid = True

                # Send handshake + status request
                self._send_data(conn, b'\x00\x00', ip, port, b'\x01')
                self._send_data(conn, b'\x00')

                # Read response, offset for string length
                data = self._read_fully(conn, extra_varint=True)

                # Send and read unix time
                unix = time.time()
                self._send_data(conn, b'\x01', 123)
                _ = self._read_fully(conn)
        except socket.timeout as e:
            if not valid:
                raise commands.CommandError(message='Could not connect to server. Make sure the IP is valid.')
            raise e

        if not data:
            raise commands.CommandError(message='Server did not respond properly. TODO: Fix hivemc doing this.')
        
        # Get time.time() before loading json as that can take a couple of milliseconds
        ping = int((time.time() - unix) * 1000)

        response = json.loads(data.decode('utf8'))
        response['ping'] = ping

        if 'favicon' in response and response['favicon']:
            favicon = io.BytesIO(base64.b64decode(response['favicon'].replace('data:image/png;base64,', '')))
        else:
            favicon = 'res/pack.png'
        favicon = discord.File(favicon, filename='pack.png')
        
        embed = discord.Embed(colour=0xa4d168)
        embed.title = ip + (':'+str(port) if port != 25565 else '')

        if isinstance(response['description'], dict):
            # json text format
            desc = response['description']
            description = ''
            for obj in desc:
                if obj == 'extra':
                    for extra in desc[obj]:
                        if 'text' in extra:
                            description += extra['text']
                elif obj == 'text':
                    description += desc[obj]
        else:
            # Fallback to non-json text format
            description = ''
            for i in range(len(response['description'])):
                # (Try to) clean up colorcodes from description
                if (response['description'][i] == '§') or (i != 0 and response['description'][i-1] == '§'):
                    continue
                description += response['description'][i] 


        embed.description = description
        embed.set_footer(text='\U00002063', icon_url='https://minecraft.net/favicon-96x96.png')
        embed.set_thumbnail(url='attachment://pack.png')

        embed.add_field(name='Version', value=response['version']['name'])
        embed.add_field(name='Players', value=f"{response['players']['online']}/{response['players']['max']}")
        embed.add_field(name='Ping', value=f"{response['ping']}ms")

        if 'modinfo' in response:
            if response['modinfo']['type'] == 'FML':
                embed.add_field(name='Forge Server', value=f"{len(response['modinfo']['modList'])} mods enabled.")
            else:
                embed.add_field(name='Modded Server', value=f"Type: {response['modinfo']['type']}")
        elif 'forgeData' in response:
            embed.add_field(name='Forge Server', value=f"{len(response['forgeData']['mods'])} mods enabled.")

        embed.timestamp = datetime.utcnow()
        await ctx.send(file=favicon, embed=embed)

    @commands.group(name='classicube', aliases=['cc'])
    async def classicube(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.UserInputError()

    @classicube.command(name='player', aliases=['players', 'user', 'username'])
    async def classiCubeAPI(self, ctx, *, user):
        """Searches ClassiCube players."""
        data = await REST(f"https://www.classicube.net/api/player/{escapeURL(user)}")
        if not data or data['error'] != '':
                raise commands.BadArgument(message=data['error'] if data and data['error'] else 'User not found')
        
        flagName = {
            'b': 'Banned from forums',
            'd': 'Developer',
            'm': 'Forum moderator',
            'a': 'Forum admin',
            'e': 'Blog editor',
            'p': 'Patron',
            'u': 'Unverified',
            'r': 'Recovering account'
        }
        
        flags = data['flags']
        embed = discord.Embed(title='ClassiCube User', colour=0x977dab)
        embed.set_author(name=data['username'])
        embed.set_thumbnail(url='attachment://head.png')
        embed.add_field(name='ID', value=data['id'])
        ago = self.td_format(datetime.utcnow() - datetime.utcfromtimestamp(data['registered']))
        
        if len(ago) == 0:
            ago = 'Under a minute'
        
        embed.add_field(name='Account created', value=f"On {datetime.utcfromtimestamp(data['registered']).strftime('%c')}\n{ago} ago")
        
        if flags:
            embed.add_field(name='Notes', value=', '.join([flagName[n] for n in flags]))
        if data['forum_title']:
            embed.add_field(name='Forum Title', value=discord.utils.escape_mentions(data['forum_title']))
        
        skinURL = f'https://classicube.s3.amazonaws.com/skin/{str(data["username"])}.png'
        if await REST(skinURL, returns='status') == 200:
            embed.add_field(name='Skin URL', value=f"[Click me]({skinURL})")
            await skinRenderer2D(skinURL, fromFile=False)
            await headRenderer(skinURL, fromFile=False)
            file = discord.File(f"skins/2d/{data['username']}.png", filename='skin.png')
            file2 = discord.File(f"skins/head/{data['username']}.png", filename='head.png')
        else:
            await skinRenderer2D('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
            await headRenderer('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
            file = discord.File('skins/2d/Steve_skin.png', filename='skin.png')
            file2 = discord.File('skins/head/Steve_skin.png', filename='head.png')

        embed.set_footer(text='\U00002063', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
        embed.set_image(url='attachment://skin.png')
        embed.timestamp = datetime.utcnow()
        await ctx.send(files=[file, file2], embed=embed)

    @classicube.command(name='stats', aliases=['stat', 'statistics'])
    async def CCStats(self, ctx):
        """Gets ClassiCube stats"""
        data = await REST('https://www.classicube.net/api/players/')
        playercount = data['playercount']
        data = await REST('https://www.classicube.net/api/servers/')
        serverlist = []
        servers = ''

        for server in sorted(data['servers'], key=lambda k: k['players'], reverse=True):
            if server['players'] > 0:
                temp = f"[{server['country_abbr']}] [{server['name']}](https://www.classicube.net/server/play/{server['hash']}) | {server['players']}/{server['maxplayers']}"
                if len(servers) + len('\n---\n') + len(temp) > 1024:
                    serverlist.append(servers)
                    servers = ''
                servers += temp+'\n---\n'
        serverlist.append(servers)
        embed = discord.Embed(title='ClassiCube', colour=0x977dab)
        embed.add_field(name='Total Accounts', value=playercount)
        for i in range(len(serverlist)):
            embed.add_field(name=(f"({str(i+1)}/{str(len(serverlist))})" if len(serverlist) != 1 else '') + 'Servers with players\nClick the server names to join!', value=serverlist[i], inline=False)

        embed.set_footer(text='\U00002063', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @classicube.command(name='servers', aliases=['server'])
    async def CCServers(self, ctx):
        """Alias for %cc stats"""
        await self.CCStats(ctx)

def setup(bot):
    bot.add_cog(Minecraft(bot))