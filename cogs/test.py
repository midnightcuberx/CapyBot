import discord
from discord.ext import commands
import asyncio
import asyncpraw
import random

reddit = asyncpraw.Reddit(
    client_id="IQrNBn7cLvP8sA",
    client_secret="tunboAlcyEJ47vANZ3FhnN_qX-I",
    password="casinoboss",
    user_agent="ok",
    username="midnightcuberx",
)


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx):
        arrays = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        gameOver = False
        while not gameOver:
            try:
                await ctx.send("Please enter something")
                sqn = await self.bot.wait_for("message", timeout=10.0)

                await ctx.send(sqn.content)
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you took too long.")
                break

    @commands.command()
    @commands.is_owner()
    async def test1(self, ctx):
        print(await reddit.user.me())
        await ctx.send(
            "test",
            file=discord.File(
                "cute-capybara-chilling-with-laptop-and-snacks-unisex-hoodie.jpg"
            ),
        )

    @commands.command()
    async def joke(self, ctx):
        for submission in reddit.subreddit("jokes").hot():
            if not submission.stickied:
                break
        embed = discord.Embed(
            title=submission.title, description=submission.selftext, color=0xEEE657
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def meme(self, ctx):
        subreddit = await reddit.subreddit("memes")
        async for submission in subreddit.hot():
            if not submission.stickied:
                break
        embed = discord.Embed(
            title="from r/memes: {}".format(submission.title),
            description="",
            color=0xEEE657,
        )
        embed.set_image(url=submission.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Test(bot))
