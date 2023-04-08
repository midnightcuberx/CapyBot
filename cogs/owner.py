import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Owner(bot))
