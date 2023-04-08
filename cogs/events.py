import discord
import random
import datetime
import time
import pytz
import pymongo
import os
from discord.ext import commands

mongosecret = os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)

db = client["economy"]
collection = db["economy"]

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.msg_last_sent = {}

    @commands.Cog.listener()
    async def on_message(self, message):

        #eco_commands = ["pm", "postmeme", "fish", "hunt", "buy", "inv", "inventory", "lb"]
        if message.author.bot:
            return
        
        '''commands = [c.name for c in self.bot.get_cog("Economy").get_commands()] + [a for c in self.bot.get_cog("Economy").get_commands() for a in c.aliases]
        t = time.time()    
        if any(message.content.lower()[1:].startswith(a) for a in commands):
            try:
                collection.insert_one(
                    {
                        "_id": message.author.id,
                        "wallet": 0,
                        "bank": 0,
                        "maxbank": 0,
                        "gun": 0,
                        "rod": 0,
                        "laptop": 0,
                        "lifesaver": 0,
                    }
                )
            except pymongo.errors.DuplicateKeyError:
                pass
            
            user = collection.find_one({"_id": message.author.id})
            collection.update_one({"_id": message.author.id}, {"$set": {"maxbank": user["maxbank"] + random.randint(20,60)}})
        await message.channel.send(f"Bank Process time {time.time() - t}")'''

        
        """msg = message.content
        id_list = [341792992354500628,  # Jordan
                646597016205656064,
                863692716785270796,  # Chai
                723784809184493588]  # Candy
        if message.author.bot:
            return

        msg = list(msg)
        for i in range(random.randint(1, len(msg)//4 + 1)):
            n = random.randint(1, len(msg))
            m = random.randint(1, 6)
            if msg[n-1].isalpha():
                for r in range(m):
                    msg.insert(n, msg[n-1])
        msg = "".join(msg)

        if message.author.id in id_list:

            if message.author.id in self.msg_last_sent:
                if time.time() - self.msg_last_sent[message.author.id] >= 5:
                    await message.channel.send(msg)
                    self.msg_last_sent[message.author.id] = time.time()
            else:
                await message.channel.send(msg)
                self.msg_last_sent[message.author.id] = time.time()"""

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(member.guild.id)
        if before.channel is None and after.channel is not None:  # and time is past x
            nz_current_timezone = pytz.timezone("Pacific/Auckland")
            nz_current_time = datetime.datetime.now(nz_current_timezone)
            hour = int(nz_current_time.strftime("%H"))
            if hour >= 20:
                await member.move_to(None)


async def setup(bot):
    await bot.add_cog(Events(bot))
