import discord
import asyncio
import random
from discord.ext import commands, tasks
import os

intents = discord.Intents.all()
bot = commands.Bot(
    # command_prefix=commands.when_mentioned_or("-"),
    command_prefix="!",
    intents=intents,
    help_command=None,
)

token = os.environ.get("token")

file_list = [
    "eco.py",
    "misc.py",
    "events.py",
    "owner.py",
    "setup.py",
    "tasks.py",
    "test.py",
]


async def load_cogs():
    global file_list

    for filename in file_list:
        if filename.endswith(".py"):
            print(filename)
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.command()
async def help(ctx, *, help_type=None):

    help_list = ["misc", "shop", "balance", "earn", "gamble", "crime", "other"]

    if not help_type or help_type.lower() not in help_list:
        embed = discord.Embed(
            title="CapyBot Help",
            description="Capy Slay💅: type -help <category> to see info about those commands",
            color=0xEEE657,
        )
        embed.add_field(name="misc", value="userinfo, ping, invite", inline=False)
        embed.add_field(name="shop", value="shop, buy, sell, inventory", inline=False)
        embed.add_field(
            name="balance", value="balance, withdraw, deposit, transfer", inline=False
        )
        embed.add_field(
            name="earn", value="busk, hunt, chew, fish, pm, beg, search", inline=False
        )
        embed.add_field(name="gamble", value="gamble, invest", inline=False)
        embed.add_field(name="crime", value="rob, murder", inline=False)
        embed.add_field(name="other", value="leaderboard, daily, hourly", inline=False)
    else:
        embed = discord.Embed(
            title="CapyBot Help",
            description=f"Capy Slay💅: {help_type.capitalize()} Commands",
            color=0xEEE657,
        )
        if help_type.lower() == "misc":
            embed.add_field(
                name="``-userinfo <person>``",
                value="gets the userinfo of a user",
                inline=False,
            )
            embed.add_field(name="``-ping``", value="returns bot latency", inline=False)
            embed.add_field(
                name="``-invite``",
                value="gets the invite link for the bot",
                inline=False,
            )
        elif help_type.lower() == "shop":
            embed.add_field(
                name="``-shop``",
                value="shows a list of shop items and their price",
                inline=False,
            )
            embed.add_field(
                name="``-buy <item> <amount (optional)>``",
                value="buy an item from the shop",
                inline=False,
            )
            embed.add_field(
                name="``-sell <item> <amount (optional)>``",
                value="sell an item from the shop",
                inline=False,
            )
        elif help_type.lower() == "balance":
            embed.add_field(
                name="``-balance <user (optional)>``",
                value="shows the balance of a user",
                inline=False,
            )
            embed.add_field(
                name="``-withdraw <amount>``",
                value="withdraw money from your bank",
                inline=False,
            )
            embed.add_field(
                name="``-deposit <amount>``",
                value="deposit money into your bank",
                inline=False,
            )
            embed.add_field(
                name="``-transfer/give <user> <amount>``",
                value="gives money to a user",
                inline=False,
            )
        elif help_type.lower() == "earn":
            embed.add_field(
                name="``-busk``", value="earn money by busking!", inline=False
            )
            embed.add_field(
                name="``-hunt``", value="earn money by hunting!", inline=False
            )
            embed.add_field(
                name="``-chew``", value="earn money by chewing!", inline=False
            )
            embed.add_field(
                name="``-fish``", value="earn money by fishing!", inline=False
            )
            embed.add_field(
                name="``-pm``", value="earn money by posting memes!", inline=False
            )
            embed.add_field(name="``-beg``", value="earn money by begging!")
            embed.add_field(
                name="``-search``",
                value="earn money by searching random places!",
                inline=False,
            )
        elif help_type.lower() == "gamble":
            embed.add_field(
                name="``-invest <amount>``",
                value="try your luck investing money!",
                inline=False,
            )
            embed.add_field(
                name="``-gamble <amount>``",
                value="try your hand at gambling!",
                inline=False,
            )
        elif help_type.lower() == "crime":
            embed.add_field(name="``-rob <user>``", value="rob someone", inline=False)
            embed.add_field(
                name="``-murder <user>``",
                value="murder someone (get all their money if you succeed!)",
                inline=False,
            )
        elif help_type.lower() == "other":
            embed.add_field(
                name="``-leaderboard (lb) <item>``",
                value="returns leaderboard for an item",
                inline=False,
            )
            embed.add_field(
                name="``-daily``", value="get your daily coins!", inline=False
            )
            embed.add_field(
                name="``-hourly``", value="get your hourly coins!", inline=False
            )

    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down")
    await bot.close()


@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Sorry, Only my owner, Venimental#7944 can use this command")


@bot.command()
@commands.is_owner()
async def reload(ctx, *, file=None):
    global file_list
    if not file:
        for filename in file_list:
            if filename.endswith(".py"):
                await bot.unload_extension(f"cogs.{filename[:-3]}")
                await bot.load_extension(f"cogs.{filename[:-3]}")
                await ctx.send(f"Successfully reloaded {filename}!")
        return

    await bot.unload_extension(f"cogs.{file}")
    await bot.load_extension(f"cogs.{file}")
    await ctx.send(f"Successfully reloaded {file}.py!")


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Successfully loaded {extension}.py!")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Successfully unloaded {extension}.py!")


"""@bot.command()
@commands.is_owner()
async def eval(ctx, *, string):
    string = string
    try:
        o = await eval(string)
    except Exception as e:
        await ctx.reply(e)
        return
    await ctx.reply(o)"""


"""@bot.command()
async def test123(ctx, a):
    await ctx.send(a: discord.User)"""


async def main():
    await load_cogs()


asyncio.run(main())
bot.run(token, reconnect=True)
