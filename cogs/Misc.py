import discord
import datetime
import time
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(aliases=["ui"])
    @commands.guild_only()
    async def userinfo(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.message.author
        userroles = ", ".join([r.mention for r in user.roles if r.name != "@everyone"])

        embed = discord.Embed(
            title=f"User info for {user}", description="", color=0xEEE657
        )
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="Nick", value=user.nick, inline=False)
        embed.add_field(name="Status", value=user.status, inline=False)
        embed.add_field(name="Game", value=user.activity, inline=False)
        embed.add_field(name="Roles", value=userroles, inline=False)
        embed.add_field(
            name="Account Created",
            value=user.created_at.strftime("%d/%m/%Y, %I:%M %p"),
            inline=False,
        )
        embed.add_field(
            name="Join Date",
            value=user.joined_at.strftime("%d/%m/%Y, %I:%M %p"),
            inline=False,
        )
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send("Pong! {0}ms".format(round(self.bot.latency * 1000)))

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        text = str(datetime.timedelta(seconds=difference))
        await ctx.send(f"The bot has been up for {text}")

    @commands.command()
    @commands.guild_only()
    async def invite(self, ctx):
        await ctx.send(
            "https://discord.com/api/oauth2/authorize?client_id=699897622479241297&permissions=8&scope=bot"
        )


async def setup(bot):
    await bot.add_cog(Misc(bot))
