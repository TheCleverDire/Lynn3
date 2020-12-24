import discord
from discord.ext import commands
import subprocess
from BotUtils import shellCommand

'''Units commands'''


class Units(commands.Cog):
    '''Units'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['convert', 'unit'])
    async def units(self, ctx, *, arg):
        '''Converts one unit into another. Use "|" to seperate input and output units
        You can find documentation at https://www.gnu.org/software/units/manual/units.html
        List of supported units can be found at https://raw.githubusercontent.com/ryantenney/gnu-units/master/units.dat'''
        source = arg.split('|')[0].strip()
        out = arg.split('|')[1].strip()
        if source[0] == '-' or out[0] == '-':
            raise commands.BadArgument(message='Units cannot start with a -')
        await shellCommand(ctx, ['units', '-1t', source, out], realtime=False)


def setup(bot):
    bot.add_cog(Units(bot))