from discord.ext import commands
from BotUtils import REST
import discord

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #region Groups
    @commands.group(name='btc', aliases=['bitcoin'], description='Bitcoin')
    async def btc(self, ctx):
        """Bitcoin"""
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @commands.group(name='eth', aliases=['ethereum'], description='Ethereum')
    async def eth(self, ctx):
        """Ethereum"""
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @commands.group(name='ltc', aliases=['litecoin'], description='Litecoin')
    async def ltc(self, ctx):
        """Litecoin"""
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @commands.group(name='doge', aliases=['dogecoin'], description='Dogecoin')
    async def doge(self, ctx):
        """Dogecoin"""
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @commands.group(name='dash', description='DASH')
    async def dash(self, ctx):
        """DASH"""
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()
    #endregion

    # Can't have a command in multiple groups so I guess I'll have to do it the hard way
    #region Price commands
    @btc.command(name='price')
    async def btcprice(self, ctx, amount=1, currency='USD'):
        value = await self.price(ctx.command.parent.name, currency)
        await ctx.send(f'**{amount} BTC = {"{:,}".format(value*amount)} {currency.upper()}**')

    @eth.command(name='price')
    async def ethprice(self, ctx, amount=1, currency='USD'):
        value = await self.price(ctx.command.parent.name, currency)
        await ctx.send(f'**{amount} ETH = {"{:,}".format(value*amount)} {currency.upper()}**')

    @ltc.command(name='price')
    async def ltcprice(self, ctx, amount=1, currency='USD'):
        value = await self.price(ctx.command.parent.name, currency)
        await ctx.send(f'**{amount} LTC = {"{:,}".format(value*amount)} {currency.upper()}**')

    @doge.command(name='price')
    async def dogeprice(self, ctx, amount=1, currency='USD'):
        value = await self.price(ctx.command.parent.name, currency)
        await ctx.send(f'**{amount} DOGE = {"{:,}".format(value*amount)} {currency.upper()}**')

    @dash.command(name='price')
    async def dashprice(self, ctx, amount=1, currency='USD'):
        value = await self.price(ctx.command.parent.name, currency)
        await ctx.send(f'**{amount} DASH = {"{:,}".format(value*amount)} {currency.upper()}**')
    #endregion

    #region Wallet
    @btc.command(name='balance', aliases=['wallet', 'address'])
    async def btcbalance(self, ctx, address, currency='USD'):
        embed = await self.balance(ctx.command.parent.description, ctx.command.parent.name, address, currency)
        await ctx.send(embed=embed)

    @eth.command(name='balance', aliases=['wallet', 'address'])
    async def ethbalance(self, ctx, address, currency='USD'):
        embed = await self.balance(ctx.command.parent.description, ctx.command.parent.name, address, currency)
        await ctx.send(embed=embed)

    @ltc.command(name='balance', aliases=['wallet', 'address'])
    async def ltcbalance(self, ctx, address, currency='USD'):
        embed = await self.balance(ctx.command.parent.description, ctx.command.parent.name, address, currency)
        await ctx.send(embed=embed)

    @doge.command(name='balance', aliases=['wallet', 'address'])
    async def dogebalance(self, ctx, address, currency='USD'):
        embed = await self.balance(ctx.command.parent.description, ctx.command.parent.name, address, currency)
        await ctx.send(embed=embed)

    @dash.command(name='balance', aliases=['wallet', 'address'])
    async def dashbalance(self, ctx, address, currency='USD'):
        embed = await self.balance(ctx.command.parent.description, ctx.command.parent.name, address, currency)
        await ctx.send(embed=embed)
    #endregion

    async def price(self, symbol, currency):
        symbol = symbol.upper()
        currency = currency.upper()
        data = await REST(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}')
        if ',' in currency or ('ParamWithError' in data and data['ParamWithError'] == 'tsyms'):
            raise commands.UserInputError(message='Invalid currency')
        value = data[currency]
        return float(value)

    def balanceformat(self, symbol, symvalue, currency, curvalue):
        if symbol == 'ETH':
            symvalue /= 1000000000000000000
        else:
            symvalue /= 100000000
        return f'**{symvalue} {symbol}** ({symvalue*curvalue} {currency})'

    async def balance(self, cryptoname, symbol, address, currency):
        symbol = symbol.upper()
        currency = currency.upper()
        value = await self.price(symbol, currency)
        data = await REST(f'https://api.blockcypher.com/v1/{symbol.lower()}/main/addrs/{address}/balance')

        embed = discord.Embed(title=f'{cryptoname} address - {address}', color=0xF1A120)
        embed.set_thumbnail(url=f'https://chart.googleapis.com/chart?cht=qr&choe=UTF-8&chs=512x512&chl={cryptoname.lower()}%3A{address}')
        embed.url = f'https://blockchair.com/{cryptoname.lower()}/address/{address}'

        embed.add_field(name='Total Balance', value=self.balanceformat(symbol, data['final_balance'], currency, value), inline=False)
        if data['unconfirmed_balance']:
            embed.add_field(name='Unconfirmed Balance', value=self.balanceformat(symbol, data['unconfirmed_balance'], currency, value))
        embed.add_field(name='Total Transactions', value=data['final_n_tx'], inline=False)
        if data['unconfirmed_n_tx']:
            embed.add_field(name='Unconfirmed Transactions', value=data['unconfirmed_n_tx'], inline=False)

        return embed

def setup(bot):
    bot.add_cog(Crypto(bot))