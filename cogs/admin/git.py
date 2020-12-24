from discord.ext import commands
from BotUtils import splitMessage, shellCommand

class Git(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True)
    @commands.is_owner()
    async def git(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @git.command(name='reset', aliases=['fuck'])
    async def gitreset(self, ctx):
        await shellCommand(ctx, 'git reset --hard origin/master', timeout=30)

    @git.command(name='pull')
    async def gitpull(self, ctx):
        await shellCommand(ctx, 'git pull && git log @{1}.. --format="%h %an | %B%n%N"', timeout=30)

    @git.command(name='log', aliases=['show'])
    async def gitlog(self, ctx, last='1'):
        await shellCommand(ctx, 'git log -'+str(int(last)), timeout=30)

def setup(bot):
    bot.add_cog(Git(bot))