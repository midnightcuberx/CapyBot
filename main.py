import discord
import asyncio
import random
from discord.ext import commands, tasks
import os

intents = discord.Intents.all()
bot = commands.Bot(
    # command_prefix=commands.when_mentioned_or("-"),
    command_prefix=".",
    intents=intents,
    help_command=None,
)

token = os.environ.get("token")


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(filename)
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.command()
async def help(ctx):
    # await ctx.send("Work in progress")
    await ctx.send(f"List of commands:\n{', '.join([c.name for c in bot.commands])}")


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
    if not file:
        for filename in os.listdir("./cogs"):
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
async def test123(ctx, a):
    await ctx.send(a: discord.User)"""


async def main():
    await load_cogs()


asyncio.run(main())
bot.run(token, reconnect=True)
