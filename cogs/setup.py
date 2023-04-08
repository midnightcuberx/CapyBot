import discord
from discord.ext import commands

class Setup(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        # change_status.start()
        # activity = discord.Game(name="with Rubiks cubes | +help", type=3)
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Lab Rat Experiments"))
        print('CapyBot is ready')
        print(f"Logged in as {self.bot.user.name}#{self.bot.user.discriminator}")
        print('------')


async def setup(bot):
    await bot.add_cog(Setup(bot))