import discord
from discord.ext import commands
import os
from io import BytesIO
import aiohttp
import urllib
import json
import re
import select
import asyncio
import typing
import time
from config import apiKeys, cache
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from PIL import Image, ImageOps

async def REST(url: str, method='GET', headers=None, data=None, auth=None, returns='json'):
    async with aiohttp.ClientSession() as s:
        async with s.request(method, url, headers=headers, data=data, auth=auth) as r:
            temp = []
            if isinstance(returns, str):
                returns = (returns,)
            for ret in returns:
                if ret == 'json':
                    temp.append(await r.json())
                elif ret == 'status':
                    temp.append(r.status)
                elif ret == 'raw':
                    temp.append(await r.read())
                elif ret == 'text':
                    temp.append(await r.text())
                elif ret == 'object':
                    return r
                else:
                    raise NotImplementedError('Invalid return type ' + ret)
            if len(temp) == 1:
                return temp[0]
            return temp

async def getTwitchToken() -> str:
    token = getCache('twitchToken')
    if token:
        authenticate = await REST('https://id.twitch.tv/oauth2/validate', headers={'Authorization': 'Bearer ' + token})
    if not token or 'status' in authenticate:
        # Invalid token
        token = await REST(f"https://id.twitch.tv/oauth2/token?client_id={getAPIKey('twitchID')}&client_secret={getAPIKey('twitchSecret')}&grant_type=client_credentials", method='POST')
        token = token['access_token']
        setCache('twitchToken', token)
    return token

def getCache(key: str) -> str:
    if not key in cache:
        return None

    value = cache[key]
    cache.pop(key)
    return value

def setCache(key: str, value: str):
    if key in cache:
        raise Exception()
    cache.append({key: value})

def escapeURL(url: str) -> str:
    return urllib.parse.quote(url)

def getAPIKey(service: str) -> str:
    if not service in apiKeys:
        raise commands.DisabledCommand(message='Command disabled due to missing API key. Please contact bot owner')
    return apiKeys[service]

def isURL(string: str) -> bool:
    """Check if string is a valid URL"""
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string) is not None

def codeBlockWrapper(string: str, lang: str = ''):
    return f'```{lang}\n{string}\n```'

async def sendShellMsg(ctx: commands.Context, message: discord.Message, curmsg: list):
    if len(codeBlockWrapper('\n'.join(curmsg), 'sh')) < 2000:
        await message.edit(content=codeBlockWrapper('\n'.join(curmsg), 'sh'))
        return message, curmsg
    else:
        msgs = splitMessage('\n'.join(curmsg), 'sh')
        await message.edit(content=msgs[0])
        curmsg = curmsg[-1]
        for msg in msgs[1:]:
            message = await ctx.send(msg)
        return message, curmsg

async def shellCommand(ctx: commands.Context, command: typing.Union[str, tuple, list], realtime: bool = False, timeout: int = 10, verbose: bool = False):

    curmsg = ['⏳']
    message = await ctx.send(codeBlockWrapper('\n'.join(curmsg), 'sh'))

    curmsg = []

    if realtime:
        if type(command) == str:
            p = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        else:
            p = Popen(command, stdout=PIPE, stderr=STDOUT)
        if verbose:
            curmsg = [f'$ {command}', f'[PID] {p.pid}']
        startTime = time.time()
        lastEdit = time.time()
        out = p.stdout
        while True:
            r, _, _ = select.select([out], [], [], 0.5)
            if p.poll() != None:
                break
            if out in r:
                line = os.read(out.fileno(), 4096)
                if isinstance(line, bytes):
                    curmsg.append(line.decode().strip())
                else:
                    curmsg.append(str(line))
                if time.time()-lastEdit > 1 and realtime:
                    message, curmsg = await sendShellMsg(ctx, message, curmsg)
                    lastEdit = time.time()

            if timeout and time.time()-startTime > timeout:
                curmsg.append('[SIGKILLED AFTER 10 SECONDS]')
                message, curmsg = await sendShellMsg(ctx, message, curmsg)
                p.kill()
                p.wait()
                break
    else:
        try:
            if type(command) == str:
                curmsg.append(check_output(command, stderr=STDOUT, shell=True, timeout=timeout).decode('utf-8'))
            else:
                curmsg.append(check_output(command, stderr=STDOUT, timeout=timeout).decode('utf-8'))
        except CalledProcessError as e:
            curmsg.append(e.output.decode('utf-8'))

    if verbose and realtime:
        curmsg.append(f'[RET] {p.returncode}')
    await sendShellMsg(ctx, message, curmsg)

async def makeBodyPart(img, img2, p, s, o11, o12, o21, o22):
    size = (p*s[0], p*s[1], p*s[2], p*s[3])
    part = img.crop(size)
    img2.paste(part, (p*o11, p*o12))
    part = ImageOps.mirror(part)
    img2.paste(part, (img2.width-p*o21, p*o22))

async def makeDualBodyPart(img, img2, p, s1, s2, o1, o2, l=False):
    size1 = (p*s1[0], p*s1[1], p*s1[2], p*s1[3])
    size2 = (p*s2[0], p*s2[1], p*s2[2], p*s2[3])
    part1 = img.crop(size1).convert('RGBA')
    part2 = img.crop(size2).convert('RGBA')
    cols = part2.getcolors()
    if not cols or cols[0] != (part2.width*part2.height, (0, 0, 0, 255)):
        part1 = Image.alpha_composite(part1, part2)
    if l:
        img2.paste(part1, (img2.width-p*o1, p*o2))
    else:
        img2.paste(part1, (p*o1, p*o2))


async def headRenderer(url: str, fromFile=True) -> str:
    """Renders a Minecraft head and returns path to image"""
    filename = url.split('/')[-1].replace('.png', '')
    if fromFile and os.path.isfile(f'skins/head/{str(filename)}.png'):
        return f'skins/head/{str(filename)}.png',

    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            img = Image.open(BytesIO(await r.read()))

    p = int(img.width / 64)
    img2 = Image.new('RGBA', (p*8, p*8), color=000000)

    # Head
    await makeDualBodyPart(img, img2, p, (8, 8, 16, 16), (40, 8, 48, 16), 0, 0)

    # We do our own resizing because discord interpolates images which makes them blurry
    if img2.width < 64:
        img2 = img2.resize((img2.width * 8, img2.height * 8), resample=Image.NEAREST)

    if not os.path.exists('skins/head'):
        os.makedirs('skins/head')
    img2.save(f'skins/head/{str(filename)}.png')
    return f'skins/head/{str(filename)}.png'

async def skinRenderer2D(url, fromFile=True) -> str:
    """Renders a Minecraft skin in 2D and returns path to the saved file"""

    filename = url.split('/')[-1].replace('.png', '')
    if fromFile and os.path.isfile(f'skins/2d/{str(filename)}.png'):
        return f'skins/2d/{str(filename)}.png'

    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            img = Image.open(BytesIO(await r.read()))

    p = int(img.width / 64)
    x64 = img.width == img.height
    img2 = Image.new('RGBA', (p*16, p*32), color=000000)

    # Head
    await makeDualBodyPart(img, img2, p, (8, 8, 16, 16), (40, 8, 48, 16), 4, 0)
    # Body
    bodySize = (p*20, p*20, p*28, p*32)
    body = img.crop(bodySize).convert('RGBA')
    if x64:
        # 64x64
        body2Size = (p*20, p*36, p*28, p*48)
        body2 = img.crop(body2Size).convert('RGBA')
        cols = body2.getcolors()
        if not cols or cols[0] != (body2.width*body2.height, (0, 0, 0, 255)):
            body = Image.alpha_composite(body, body2)
    img2.paste(body, (p*4, p*8))

    if not x64:
        # 64x32 format
        # Arms
        await makeBodyPart(img, img2, p, (44, 20, 48, 32), 0, 8, 4, 8)
        # Legs
        await makeBodyPart(img, img2, p, (4, 20, 8, 32), 4, 20, 8, 20)
    else:
        # 64x64 format
        # Right arm
        await makeDualBodyPart(img, img2, p, (44, 20, 48, 32), (44, 36, 48, 48), 0, 8)
        # Left arm
        await makeDualBodyPart(img, img2, p, (36, 52, 40, 64), (52, 52, 56, 64), 4, 8, l=True)
        # Right leg
        await makeDualBodyPart(img, img2, p, (4, 20, 8, 32), (4, 36, 8, 48), 4, 20)
        # Left leg
        await makeDualBodyPart(img, img2, p, (20, 52, 24, 64), (4, 52, 8, 64), 8, 20, l=True)

    if img2.width < 256:
        img2 = img2.resize((img2.width * 16, img2.height * 16), resample=Image.NEAREST)

    if not os.path.exists('skins/2d'):
        os.makedirs('skins/2d')
    img2.save(f'skins/2d/{str(filename)}.png')
    return f'skins/2d/{str(filename)}.png'

def splitMessage(message: str, highlight='') -> list:
    returns = []
    for msg in [message[i:i+1990] for i in range(0, len(message), 1990)]:
            returns.append('```' + highlight + '\n' + msg.replace('```', '`\U00002063``') + '```')
    return returns