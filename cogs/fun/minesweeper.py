from discord.ext import commands
import discord
import random

class Minesweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def generateMinesweeper(self, width, height, bombs):
        grid = []
        bomb = []
        for i in range(height):
            grid.append([0]*width)
        while bombs > 0:
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            if grid[y][x] != 'x':
                grid[y][x] = 'x'
                bomb.append((x, y))
                bombs-=1

        for loc in bomb:
            canUp = False
            canLeft = False
            canRight = False
            canDown = False
            if loc[1] > 0:
                canUp = True
            if loc[1] < height-1:
                canDown = True
            if loc[0] > 0:
                canLeft = True
            if loc[0] < width-1:
                canRight = True

            if canUp:
                if grid[loc[1]-1][loc[0]] != 'x':
                    grid[loc[1]-1][loc[0]]+=1
            if canUp and canLeft:
                if grid[loc[1]-1][loc[0]-1] != 'x':
                    grid[loc[1]-1][loc[0]-1]+=1
            if canUp and canRight:
                if grid[loc[1]-1][loc[0]+1] != 'x':
                    grid[loc[1]-1][loc[0]+1]+=1
            if canDown:
                if grid[loc[1]+1][loc[0]] != 'x':
                    grid[loc[1]+1][loc[0]]+=1
            if canDown and canLeft:
                if grid[loc[1]+1][loc[0]-1] != 'x':
                    grid[loc[1]+1][loc[0]-1]+=1
            if canDown and canRight:
                if grid[loc[1]+1][loc[0]+1] != 'x':
                    grid[loc[1]+1][loc[0]+1]+=1
            if canLeft:
                if grid[loc[1]][loc[0]-1] != 'x':
                    grid[loc[1]][loc[0]-1]+=1
            if canRight:
                if grid[loc[1]][loc[0]+1] != 'x':
                    grid[loc[1]][loc[0]+1]+=1

        return grid

    @commands.command(name='minesweeper')
    async def minesweeper(self, ctx, *, args=None):
        '''Generates a game of minesweeper.
        args = `width height bombs (nospoil)`'''
        spoil = True
        if args != None and len(str(args).split(' ')) > 2:
            width = int(str(args).split(' ')[0])
            height = int(str(args).split(' ')[1])
            bombs = int(str(args).split(' ')[2])
            if 'nospoil' in args:
                spoil = False
        else:
            width = 10
            height = 10
            bombs = 15
        output = ''
        field = self.generateMinesweeper(width, height, bombs)
        for row in field:
            for c in row:
                if spoil: output += '||'
                if c == 0:
                    output += '\N{WHITE LARGE SQUARE}'
                elif c == 1:
                    output += '\U00000031\U000020E3'
                elif c == 2:
                    output += '\U00000032\U000020E3'
                elif c == 3:
                    output += '\U00000033\U000020E3'
                elif c == 4:
                    output += '\U00000034\U000020E3'
                elif c == 5:
                    output += '\U00000035\U000020E3'
                elif c == 6:
                    output += '\U00000036\U000020E3'
                elif c == 7:
                    output += '\U00000037\U000020E3'
                elif c == 8:
                    output += '\U00000038\U000020E3'
                elif str(c) == 'x':
                    output += '\N{BOMB}'
                if spoil: output += '||'
            output += '\n'
        embed = discord.Embed(title='Minesweeper', colour=0xFFA500)
        embed.description = output
        await ctx.send(embed=embed, content='')

def setup(bot):
	bot.add_cog(Minesweeper(bot))