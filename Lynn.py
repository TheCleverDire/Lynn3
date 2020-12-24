import discord
from discord.ext import commands
import config
import glob
import logging

bot = commands.Bot(command_prefix=config.get_prefix, description=config.description, allowed_mentions=discord.AllowedMentions(everyone=False), intents=discord.Intents.all())

if __name__ == '__main__':
    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('cogs/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.', exc_info=True)

    @bot.event
    async def on_ready():
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Discord.py version: {discord.__version__}')

    @bot.event
    async def on_message(message):
        if message.author.id == 671726702967259169: # Command from DiscordSRV / MC
            message.content = message.content.split(' » ')[-1]
        ctx = await bot.get_context(message)
        if ctx.valid:
            if message.author.bot and message.author.id != 671726702967259169:
                return

            async with ctx.channel.typing():
                await bot.invoke(ctx)

    bot.run(config.token, bot=True, reconnect=True)