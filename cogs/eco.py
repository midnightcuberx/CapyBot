import discord
import pymongo
import random
import asyncio
import os
import math
from discord.ext import commands
from .viewclasses import FightView
from .viewclasses import Challenge
from .testy import button
from .blackjack import BlackJack
from .blackjack import get_starting_cards
from .blackjack import get_starting_score
from .blackjack import get_dealer_score
from .blackjack import ace_filter
from .blackjack import run_bj
from .blackjack import is_blackjack
from .blackjack import get_result

# add code that adds new users

# Could I restructure the money so that there is one big id with each person having their own dict
# By2【你並不懂我 You Don't Know Me】官方完整版

mongosecret = os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)

db = client["economy"]
collection = db["economy"]
users = collection.find({})

# ---------------------------------- Functions ---------------------------------------


def get_dict(user):
    return {
        "_id": user.id,
        "wallet": 0,
        "bank": 0,
        "maxbank": 0,
        "gun": 0,
        "rod": 0,
        "laptop": 0,
        "lifesaver": 0,
        "instrument": 0,
        "capybara": 0,
        "bunny": 0,
        "knife": 0,
        "shuriken": 0,
        "pistol": 0,
        "sniper": 0,
        "bullet": 0,
        "slots": {"maxwin": 0, "maxloss": 0, "win": 0, "loss": 0},
        "bj": {"maxwin": 0, "maxloss": 0, "win": 0, "loss": 0},
    }


def insert_new_user(collection, discord_user):
    try:
        collection.insert_one(get_dict(discord_user))
    except pymongo.errors.DuplicateKeyError:
        pass


def get_max_bank(user_obj):
    return user_obj["maxbank"] + random.randint(20, 600)


def get_rob_amount():
    chance = random.randint(1, 501)

    if chance == 1:  # 0.2 %
        percentage = random.randint(90, 101)
    elif chance <= 11:  # 2%
        percentage = random.randint(70, 90)
    elif chance <= 100:  # 20%
        percentage = random.randint(50, 70)
    elif chance <= 150:  # 30%
        percentage = random.randint(30, 50)
    elif chance <= 250:
        percentage = random.randint(15, 30)
    else:
        percentage = random.randint(5, 15)

    return percentage


def seconds_to_timestr(s):
    hours = math.floor((s // 1) / 3600)
    minutes = math.floor((s // 1) % 3600 / 60)
    seconds = s % 60
    time_str = ""

    if hours != 0:
        time_str += f"{hours} hour(s) "
    if minutes != 0 or (minutes == 0 and hours != 0):
        time_str += f"{minutes} minute(s) "
    if hours == 0 and minutes == 0:
        time_str += f"{seconds:.2f} second(s)"
    else:
        time_str += f"{math.floor(seconds)} second(s)"

    return time_str


def load_db(economy, users_in_db):
    users = collection.find({})
    for u in users:
        users_in_db.append(u["_id"])
        economy[u["_id"]] = {}
        # economy[u["_id"]]["fighting"] = False
        for item in u:
            if item != "_id":
                economy[u["_id"]][item] = u[item]


# ---------------------------------- Eco class ---------------------------------------


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_in_db = []  # [u["_id"] for u in users]
        self.economy = {}  # {u["_id"]: u["wallet"] for u in users}
        self.weapon_type = [
            "knife",
            "shuriken",
            "pistol",
            "sniper",
        ]
        self.weapon_value = {
            "knife": 10,
            "shuriken": 25,
            "pistol": 40,
            "sniper": 50,
        }
        self.itemvalue = {
            "laptop": 1500,
            "rod": 200,
            "gun": 5000,
            "lifesaver": 15000,
            "capybara": 1000000000,
            "bunny": 100000,
            "knife": 1000,
            "shuriken": 5000,
            "pistol": 15000,
            "sniper": 50000,
            "bullet": 750,
        }
        load_db(self.economy, self.users_in_db)

    def update_economy(self, member, user_info):
        for item in user_info:
            if item != "_id":
                self.economy[member.id][item] = 0

    def process_user(self, member):
        insert_new_user(collection, member)
        self.economy[member.id] = {}
        self.users_in_db.append(member.id)
        user = get_dict(member)
        self.update_economy(member, user)

    """def is_fighting(self, member):
        return self.economy[member.id]["fighting"]"""

    # @commands.Cog.listener()
    # async def on_ready(self):
    # users = collection.find({})
    # for u in users:
    # self.users_in_db.append(u["_id"])
    # self.economy[u["_id"]] = {}
    # for item in u:
    # if item != "_id":
    # self.economy[u["_id"]][item] = u[item]
    # self.users_in_db = [u["_id"] for u in users]
    # self.economy = {u["_id"]: u["wallet"] for u in users}
    # print(self.users_in_db)
    # print(self.economy)
    # print("Database loaded")

    # @tasks.loop(seconds = 1)
    # async def insert_dict(self):
    # for

    # ---------------------------------- Owner commands ---------------------------------------

    @commands.command()
    @commands.is_owner()
    async def dbstats(self, ctx, member: discord.User):
        user = collection.find_one({"_id": member.id})
        await ctx.author.send(member)
        await ctx.author.send(
            {u: user[u] for u in user} if user else "User not in database!"
        )

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx, member: discord.User, thing, amount: int):
        if (
            thing.lower() not in get_dict(ctx.author)
            and thing.lower() not in self.weapon_type
        ):
            return

        if member.id not in self.users_in_db:
            self.process_user(member)

        collection.update_one({"_id": member.id}, {"$set": {thing: amount}})
        self.economy[member.id][thing] = amount
        await ctx.reply(f"Set {member} {thing} to {amount}")

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, member: discord.User, thing, amount: int):
        if (
            thing.lower() not in get_dict(ctx.author)
            and thing.lower() not in self.weapon_type
        ):
            return

        if member.id not in self.users_in_db:
            self.process_user(member)

        collection.update_one(
            {"_id": member.id},
            {"$set": {thing: self.economy[member.id][thing] + amount}},
        )
        self.economy[member.id][thing] += amount
        await ctx.reply(f"Added {amount} to {member}'s {thing}")

    @commands.command(aliases=["purge"])
    @commands.is_owner()
    async def delete(self, ctx, member: discord.User):
        try:
            collection.delete_one({"_id": member.id})
            self.users_in_db.remove(member.id)
            self.economy.pop(member.id)
            await ctx.reply("User data deleted")

        except Exception as e:
            await ctx.reply(e)
            await ctx.reply("User not in database!")

    # ---------------------------------- Crime commands ---------------------------------------
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fight(self, ctx, member: discord.Member = None, money: int = 0):
        # def is_member(m):
        # return m.author == member

        if not member:
            await ctx.reply("Please enter a valid member!")
            self.fight.reset_cooldown(ctx)
            return

        if member.bot:
            await ctx.reply("You cannot challenge a bot!")
            self.fight.reset_cooldown(ctx)
            return

        if member == ctx.author:
            await ctx.reply("You cannot challenge yourself to a fight!")
            self.fight.reset_cooldown(ctx)
            return

        if ctx.author.id not in self.users_in_db:  # have function for this
            self.process_user(ctx.author)

        if member.id not in self.users_in_db:
            self.process_user(member)

        user_bal = self.economy[ctx.author.id]["wallet"]
        member_bal = self.economy[member.id]["wallet"]
        # self.economy[ctx.author.id]["fighting"] = True
        # self.economy[member.id]["fighting"] = True

        if money < 0:
            await ctx.reply(
                "You cannot challenge someone with negative money!"
            )
            self.fight.reset_cooldown(ctx)
            return
        if member_bal < money:
            await ctx.reply(
                f"That member doesn't have enough money to accept your challenge!"
            )
            self.fight.reset_cooldown(ctx)
            return
        if user_bal < money:
            await ctx.reply(
                "You don't have enough money to challenge that person!"
            )
            self.fight.reset_cooldown(ctx)
            return

        self.economy[member.id]["wallet"] -= money
        self.economy[ctx.author.id]["wallet"] -= money

        view = Challenge(member, 30)
        msg = await ctx.reply(
            f"{member.mention}, {ctx.author.mention} has challenged you to a fight with ${money}!",
            mention_author=False,
            view=view,
        )
        view.message = msg
        await view.wait()

        if view.accepted is False:
            # self.economy[ctx.author.id]["fighting"] = False
            # self.economy[member.id]["fighting"] = False
            self.economy[ctx.author.id]["wallet"] += money
            self.economy[member.id]["wallet"] += money
            return

        winner = await button(ctx, msg, member)
        loser = ctx.author if winner == member else member

        if money > 0:
            self.economy[winner.id]["wallet"] += 2 * money
            # self.economy[loser.id]["wallet"] -= money

            collection.update_one(
                {"_id": winner.id},
                {"$set": {"wallet": self.economy[winner.id]["wallet"]}},
            )
            collection.update_one(
                {"_id": loser.id},
                {"$set": {"wallet": self.economy[loser.id]["wallet"]}},
            )

    @fight.error
    async def fight_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
            return
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("Please enter a valid user or amount of money!")
            self.fight.reset_cooldown(ctx)
            return
        else:
            self.fight.reset_cooldown(ctx)
            raise error

    # @commands.command()

    # button = discord.ui.Button(label="Click me")
    # view.add_item(button)
    # if view.button_pressed is None:
    # await ctx.send("timeout!")

    # ---------------------------------- Crime commands ---------------------------------------

    # @commands.command()
    # @commands.guild_only()
    # @commands.cooldown(1, 3600, commands.BucketType.user)
    # async def drugs(self, ctx):

    @commands.command(aliases=["kill"])
    @commands.guild_only()
    # @commands.is_owner()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def murder(
        self, ctx, member: discord.Member = None, amount: int = 1
    ):
        murder_dict = {
            "knife": "stab",
            "shuriken": "throw a shuriken at",
            "pistol": "shoot",
            "sniper": "shoot",
        }

        if not member:
            await ctx.reply(
                "Please try to enter a valid member to murder!",
                mention_author=False,
            )
            self.murder.reset_cooldown(ctx)
            return

        if amount > 1000:
            amount = 1000
            await ctx.reply(
                "You are only allowed to shoot 1000 times at once!"
            )

        if member.id == ctx.author.id:
            await ctx.reply("Sorry but you are not allowed to commit suicide!")
            self.murder.reset_cooldown(ctx)
            return

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        # If member not in
        if member.id not in self.users_in_db:
            self.process_user(member)

        user = self.economy[ctx.author.id]
        member_info = self.economy[member.id]

        # if member_info["wallet"] == 0:
        # await ctx.reply(
        # "You cannot murder someone who doesn't have money!",
        # mention_author=False,
        # )
        # return

        # print(not any(x > 0 for x in [user[i] for i in user if i in self.weapon_type]))
        # return
        if not any(
            x > 0 for x in [user[i] for i in user if i in self.weapon_type]
        ):
            await ctx.reply(
                "You need a weapon to kill people! Go purchase one at the shop.",
                mention_author=False,
            )
            self.murder.reset_cooldown(ctx)
            return

        for item in self.weapon_type[::-1]:
            if user[item] > 0:
                number = self.weapon_value[item]
                break

        if item == "pistol" or item == "sniper":
            if user["bullet"] < amount:
                if user["knife"] < amount and user["shuriken"] < amount:
                    await ctx.reply(
                        "You need more bullets! Go buy some at the store using -shop!",
                        mention_author=False,
                    )
                    self.murder.reset_cooldown(ctx)
                    return
                else:
                    if user["shuriken"] < amount:
                        item = "knife"
                    else:
                        item = "shuriken"
                    user[item] -= amount
            else:
                user["bullet"] -= amount

        else:
            user[item] -= amount

        chance = random.randint(1, 101)
        print(chance)

        msg = await ctx.reply(
            f"Attempting to {murder_dict[item]} {member}...",
            mention_author=False,
        )
        await asyncio.sleep(3)

        break_chance = random.randint(1, 26)
        # break_chance = 1
        if break_chance == 1 and (item == "pistol" or item == "sniper"):
            user[item] -= 1
            await msg.edit(
                content=f"Your {item} jammed and broke! Go buy a new one at the shop"
            )
        else:
            if chance > number:
                if user["lifesaver"] > 0:
                    user["lifesaver"] -= 1
                    await msg.edit(
                        content=f"You were caught trying to murder {member} but were able to avoid dying as you had a lifesaver."
                    )
                else:
                    member_info["wallet"] += user["wallet"]
                    user["wallet"] = 0
                    await msg.edit(
                        content=f"You were caught trying to murder {member} and were given a death sentence."
                    )
                    # maybe send message saying they got all the money as compensation

            else:
                member_bal = member_info["wallet"]
                # pass  # do stuff with member bal and stuff because successful murder
                if member_info["lifesaver"] >= amount:
                    chance_2 = random.randint(1, 11)

                    if chance_2 > 3 or member_bal <= 10:
                        member_info["lifesaver"] -= amount
                        await msg.edit(
                            content=f"You attempted to kill {member} with a {item} but they survived!"
                        )
                    else:  # steal a tiny amount of money 30% chance x whatever weapon chance
                        percentage = random.randint(5, 11)
                        money = round(member_bal * percentage / 100)
                        await msg.edit(
                            content=f"You held {member} hostage with a {item} and managed to get a ransom of ${money}!"
                        )
                        await member.send(
                            f"You were held hostage by {ctx.author} and you paid them ${money} to be set free!"
                        )
                        member_info["wallet"] -= money
                        user["wallet"] += money

                    # send member dm maybe and allow to be disabled in economy
                else:
                    member_info["wallet"] = 0
                    member_info["lifesaver"] = 0
                    user["wallet"] += member_bal
                    await msg.edit(
                        content=f"You successfully killed {member} with a {item} and inherited all their money!"
                    )
                    await member.send(
                        f"You were killed by {ctx.author} and they inherited all your money!"
                    )

        collection.update_one(
            {"_id": ctx.author.id},
            {
                "$set": {
                    "wallet": user["wallet"],
                    "lifesaver": user["lifesaver"],
                    item: user[item],
                    "bullet": user["bullet"],
                }
            },
        )
        collection.update_one(
            {"_id": member.id},
            {
                "$set": {
                    "wallet": member_info["wallet"],
                    "lifesaver": member_info["lifesaver"],
                }
            },
        )

    @murder.error
    async def murder_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.murder.reset_cooldown(ctx)
            raise error

    @commands.command(aliases=["steal"])
    # @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rob(self, ctx, *, member: discord.User):
        if member.id == ctx.author.id:
            await ctx.reply(
                "You cannot rob yourself, silly", mention_author=False
            )
            self.rob.reset_cooldown(ctx)
            return

        # if member.bot:
        # await ctx.reply("You cannot rob a bot!", mention_author=False)
        # return

        if member.id not in self.users_in_db:
            await ctx.reply(
                "That user has less than 2500 coins, you cannot rob them",
                mention_author=False,
            )
            self.rob.reset_cooldown(ctx)
            return

        if ctx.author.id not in self.users_in_db:
            await ctx.reply(
                "You cannot rob anyone if you dont have 2500 coins",
                mention_author=False,
            )
            self.rob.reset_cooldown(ctx)
            return

        user = self.economy[
            ctx.author.id
        ]  # user = collection.find_one({"_id": ctx.author.id})
        user_bal = user["wallet"]
        target = self.economy[member.id]
        member_bal = target["wallet"]

        if user_bal >= 2500:
            number = random.randint(1, 5)
            if member_bal < 2500:
                await ctx.reply(
                    "That user has less than 2500 coins, you cannot rob them",
                    mention_author=False,
                )
                self.rob.reset_cooldown(ctx)
                return
            elif member_bal >= 2500:
                if number == 1:
                    """if member_bal<=5000:
                        percentage=random.randint(1,75)
                    elif member_bal>5000 and member_bal<=10000:
                        percentage=random.randint(1,50)
                    elif member_bal>10000 and member_bal<=100000:
                        percentage=random.randint(1,25)
                    elif member_bal>100000:
                        percentage=random.randint(1,10)"""
                    percentage = get_rob_amount()
                    max_amount = round(member_bal * percentage / 100)
                    # stolen_amount = random.randint(50, max_amount)
                    stolen_amount = max_amount
                    user_bal += stolen_amount
                    member_bal -= stolen_amount
                    await ctx.reply(
                        f"💸 | You stole ${stolen_amount} off {member}!",
                        mention_author=False,
                    )
                else:
                    if user_bal <= 50000:
                        user_bal -= 2500
                        member_bal += 2500
                        money_lost = 2500
                    else:
                        num = random.randint(5, 15)
                        user_bal -= round(user_bal * num / 100)
                        member_bal += round(user_bal * num / 100)
                        money_lost = round(user_bal * num / 100)
                    await ctx.reply(
                        f"You got caught trying to rob {member} so you paid them ${money_lost} to be quiet!",
                        mention_author=False,
                    )

            self.economy[ctx.author.id]["wallet"] = user_bal
            self.economy[member.id]["wallet"] = member_bal

            collection.update_one(
                {"_id": ctx.author.id}, {"$set": {"wallet": user_bal}}
            )
            collection.update_one(
                {"_id": member.id}, {"$set": {"wallet": member_bal}}
            )

        else:
            await ctx.reply(
                "You cannot rob anyone if you dont have 2500 coins",
                mention_author=False,
            )
            self.rob.reset_cooldown(ctx)

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.reply("You need to state a valid user to Rob!")
            self.rob.reset_cooldown(ctx)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Please enter a valid member to rob!")
            self.rob.reset_cooldown(ctx)
        else:
            self.rob.reset_cooldown(ctx)
            raise error

    # ---------------------------------- Basic economy commands ---------------------------------------
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def chew(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]

        user_bal = user["wallet"]
        bunnies = user["bunny"]

        if bunnies < 1:
            await ctx.reply(
                "Your teeth broke attempting to chew curtains! Go buy a bunny at the shop!",
                mention_author=False,
            )
            self.chew.reset_cooldown(ctx)
            return

        chance = random.randint(1, 101)

        if chance < 3:  # 2% chance
            await ctx.reply(
                "Your bunnies teeth broke attempting to chew curtains!",
                mention_author=False,
            )
            user["bunny"] -= 1
            collection.update_one(
                {"_id": ctx.author.id}, {"$set": {"bunny": bunnies - 1}}
            )
            return

        people = [
            "teacher",
            "friend",
            "mum",
            "dad",
            "owner",
            "principal",
            "tutor",
            "professor",
            "husband",
            "priest",
            "lecturer",
            "child",
        ]
        money = random.randint(1000, 10000)
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["wallet"] += money
        self.economy[ctx.author.id]["maxbank"] = max_bank
        total = user_bal + money

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": total, "maxbank": max_bank}},
        )
        await ctx.reply(
            f"Someone paid you ${money} to vandalise their {random.choice(people)}'s curtains!",
            mention_author=False,
        )

    @chew.error
    async def chew_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.chew.reset_cooldown(ctx)
            raise error

    @commands.command(aliases=["postmeme"])
    @commands.guild_only()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def pm(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]
        laptops = user["laptop"]

        if laptops < 1:
            await ctx.reply(
                "You cannot post memes withut a laptop! Go buy one at the shop",
                mention_author=False,
            )
            self.pm.reset_cooldown(ctx)
            return

        chance = random.randint(1, 101)

        if chance < 3:
            await ctx.reply(
                "Your laptop broke! Go buy a new one at the shop",
                mention_author=False,
            )
            user["laptop"] -= 1
            collection.update_one(
                {"_id": ctx.author.id}, {"$set": {"laptop": user["laptop"]}}
            )
            return

        memes = ["edgy", "funky", "dank", "repost", "cubing", "corona"]
        chance = random.randint(1, 11)
        if chance > 8:
            money = random.randint(400, 1001)
        else:
            money = random.randint(100, 400)

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["wallet"] += money
        self.economy[ctx.author.id]["maxbank"] = max_bank
        total = user_bal + money

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": total, "maxbank": max_bank}},
        )
        await ctx.reply(
            f"You posted a {random.choice(memes)} meme and earned ${money}!",
            mention_author=False,
        )

    @pm.error
    async def pm_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.pm.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fish(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        if user["rod"] < 1:
            await ctx.reply(
                "You cannot fish without a fishing rod! Go buy one at the shop",
                mention_author=False,
            )
            # self.fish.reset_cooldown(ctx)
            return

        chance = random.randint(1, 101)

        if chance < 3:
            await ctx.reply(
                "Your rod broke! Go buy a new one at the shop",
                mention_author=False,
            )
            user["rod"] -= 1
            collection.update_one(
                {"_id": ctx.author.id}, {"$set": {"rod": user["rod"]}}
            )
            return

        fish = [
            "snapper",
            "kingfish",
            "pufferfish",
            "shrimp",
            "catfish",
            "salmon",
            "prawn",
            "tuna",
        ]

        money = random.randint(50, 400)
        user_bal += money
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] = user_bal

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user["wallet"], "maxbank": max_bank}},
        )
        await ctx.reply(
            f"You caught {random.randint(1, 5)} {random.choice(fish)} and earned ${money}!",
            mention_author=False,
        )

    @fish.error
    async def fish_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.fish.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def hunt(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_guns = user["gun"]

        if user_guns < 1:
            await ctx.reply(
                "You cannot hunt without a gun! use the buy command to buy yourself a gun first",
                mention_author=False,
            )
            self.hunt.reset_cooldown(ctx)
            return

        chance = random.randint(1, 101)

        if chance < 3:
            await ctx.reply(
                "Your gun broke! Go buy a new one at the shop",
                mention_author=False,
            )
            user["gun"] -= 1
            collection.update_one(
                {"_id": ctx.author.id}, {"$set": {"gun": user["gun"]}}
            )
            return

        success = random.randint(1, 20)
        if success == 4:
            if user["lifesaver"] < 1:
                await ctx.reply(
                    "You were shot while hunting and you didnt have a lifesaver so you died!",
                    mention_author=False,
                )
                collection.update_one(
                    {"_id": ctx.author.id}, {"$set": {"wallet": 0}}
                )
                return

            else:
                user["lifesaver"] -= 1
                await ctx.reply(
                    "You were shot by a fellow hunter but you had a lifesaver and survived after being taken to hospital",
                    mention_author=False,
                )
                return

        else:
            money = random.randint(500, 5000)
            user["wallet"] += money
            max_bank = get_max_bank(user)
            self.economy[ctx.author.id]["maxbank"] = max_bank
            # self.economy[ctx.author.id]["wallet"] += money
            await ctx.reply(
                f"You went hunting and caught ${money} worth of game!",
                mention_author=False,
            )

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user["wallet"], "maxbank": max_bank}},
        )

    @hunt.error
    async def hunt_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.hunt.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def busk(self, ctx):
        luck = random.randint(1, 60)

        if luck > 30:
            if luck == 50:
                money = random.randint(200, 501)
            else:
                money = random.randint(100, 200)
        else:
            money = random.randint(50, 100)

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += money
        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user["wallet"] + money, "maxbank": max_bank}},
        )

        duration = random.randint(1, 60)
        instruments = ["🎺", "🎻", "🎸", "🎷", "🥁", "📯", "🎹"]
        await ctx.reply(
            f"{random.choice(instruments)} | You busked for {duration} minutes and earned ${money}!",
            mention_author=False,
        )

    @busk.error
    async def busk_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.busk.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def beg(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        chance = random.randint(1, 11)
        if chance == 1:
            money = random.randint(100, 201)
        else:
            money = random.randint(1, 100)

        user_bal += money
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += money

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )
        await ctx.reply(
            f"You begged and earned ${money}", mention_author=False
        )

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.beg.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def work(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]

        money = random.randint(160, 1000)
        user_bal = user["wallet"] + money
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += money

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )

        jobs = [
            "nurse",
            "doctor",
            "banker",
            "salesperson",
            "lawyer",
            "zookeeper",
            "movie star",
            "actor",
            "programmer",
            "teacher",
            "musician",
            "truck driver",
            "conductor",
            "bus driver",
            "taxi driver",
            "model",
            "judge",
            "umpire",
            "referee",
            "professional rugby player",
            "professional football player",
        ]
        await ctx.reply(
            f"You worked as a {random.choice(jobs)} and earned ${money}",
            mention_author=False,
        )

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.work.reset_cooldown(ctx)
            raise error

    @commands.command(aliases=["scout"])
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def search(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]

        places = [
            "the dump",
            "a rubbish bin",
            "a trash can",
            "your parent's dressing room",
            "the school playground",
            "the bus stop",
            "the backseat of a taxi",
            "a dumpster",
            "the dump",
            "your parent's wallet",
            "the coffee shop",
        ]

        number = random.randint(1, 20)
        if number == 1:
            money = random.randint(300, 501)
        elif number > 15:
            money = random.randint(200, 300)
        else:
            money = random.randint(1, 200)

        user_bal = user["wallet"] + money
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += money

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )
        await ctx.reply(
            f"You scouted {random.choice(places)} and found ${money}!",
            mention_author=False,
        )

    @search.error
    async def search_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.search.reset_cooldown(ctx)
            raise error

    # ---------------------------------- Daily hourly etc ---------------------------------------

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"] + 20000

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += 20000

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )
        await ctx.reply(
            "You successfully collected your 20000 daily coins!",
            mention_author=False,
        )

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.daily.reset_cooldown(ctx)
            raise error

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def hourly(self, ctx):
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"] + 1000

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] += 1000

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )
        await ctx.reply(
            "You successfully collected your 1000 hourly coins!",
            mention_author=False,
        )

    @hourly.error
    async def hourly_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.hourly.reset_cooldown(ctx)
            raise error

    # ---------------------------------- Commands that interact with shop items ---------------------------------------

    @commands.command()
    @commands.guild_only()
    async def shop(self, ctx):
        embed = discord.Embed(
            title="Shop",
            description="A place where you can buy things using -buy <item> <amount>",
            color=0xEEE657,
        )
        embed.add_field(
            name="Laptop-$1500",
            value="You can post memes with this laptop.",
            inline=False,
        )
        embed.add_field(name="Rod-$200", value="You can fish with this!")
        embed.add_field(
            name="Lifesaver-$15000",
            value="You may die from hunting so why not have one of these handy?",
            inline=False,
        )
        embed.add_field(
            name="Gun-$5000",
            value="You can hunt with this. But beware as there is a chance you will be shot by someone else!",
            inline=False,
        )
        embed.add_field(
            name="Capybara- $1000000000",
            value="Collectable plushie",
            inline=False,
        )
        embed.add_field(
            name="Bunny- $100000",
            value="Chew curtains fastly with your bunny to earn some quick cash!",
            inline=False,
        )
        embed.add_field(
            name="Bullet- $750",
            value="You need this to shoot people",
            inline=False,
        )
        embed.add_field(
            name="Knife- $1000",
            value="Use this to murder people - 10% success rate",
            inline=False,
        )
        embed.add_field(
            name="Shuriken- $5000",
            value="Use this to murder people - 25 % success rate",
            inline=False,
        )
        embed.add_field(
            name="Pistol- $15000",
            value="Use this to murder people - 40 % success rate",
            inline=False,
        )
        embed.add_field(
            name="Sniper- $50000",
            value="Use this to murder people - 50 % success rate",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def buy(self, ctx, item=None, amount=None):
        if not item:
            await ctx.reply("Please enter a valid item!", mention_author=False)
            return
        if not amount:
            amount = 1

        item = item.lower()

        if item not in self.itemvalue:
            await ctx.reply(
                "That is not a valid item! use -shop to check what items are on sale",
                mention_author=False,
            )
            return

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        try:
            amount = int(amount)
        except ValueError:
            if amount.lower() == "all" or amount.lower() == "max":
                amount = user_bal // self.itemvalue[item]
                if amount <= 0:
                    await ctx.reply(
                        "Sorry, you do not have enough money.",
                        mention_author=False,
                    )
                    return
            else:
                await ctx.reply(
                    f"Please enter a valid number of {item}(s)!",
                    mention_author=False,
                )
                return
        if amount < 1:
            await ctx.reply(
                "You cannot buy 0 or negative items!", mention_author=False
            )
            return

        # if item == "lifesaver":
        # if user["lifesaver"] >= 10:
        # await ctx.reply("The number of lifesavers is capped at 10")
        # return
        # if user["lifesaver"] + amount > 10:
        # amount = 10 - user["lifesaver"]
        # await ctx.reply("The number of lifesavers is capped at 10")
        if user_bal >= self.itemvalue[item] * amount:
            user["wallet"] -= self.itemvalue[item] * amount
            user[item] += amount
            # self.economy[ctx.author.id]["wallet"] -= itemvalue[item] * amount
            # self.economy[ctx.author.id][item] += amount

            collection.update_one(
                {"_id": ctx.author.id},
                {"$set": {"wallet": user["wallet"], item: user[item]}},
            )
            await ctx.reply(
                f"You successfully bought {amount} {item}(s)!",
                mention_author=False,
            )
        else:
            await ctx.reply(
                "Sorry, you do not have enough money.", mention_author=False
            )

    @commands.command()
    @commands.guild_only()
    async def sell(self, ctx, item=None, amount=None):
        if not item:
            await ctx.reply("Please enter a valid item!", mention_author=False)
            return
        if not amount:
            amount = 1

        item = item.lower()

        if item not in self.itemvalue:
            await ctx.reply(
                "That is not a valid item! use -shop to check what items you can sell",
                mention_author=False,
            )
            return

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]

        try:
            amount = int(amount)
        except ValueError:
            if amount.lower() == "all" or amount.lower() == "max":
                amount = user[item]
                if amount == 0:
                    await ctx.reply(
                        f"You do not have enough of {item}!",
                        mention_author=False,
                    )
                    return
            else:
                await ctx.reply(
                    f"You did not enter a valid number of {item}(s)!",
                    mention_author=False,
                )

        if amount <= user[item]:
            user["wallet"] += self.itemvalue[item] * amount
            user[item] -= amount
            # self.economy[ctx.author.id]["wallet"] += itemvalue[item] * amount
            # self.economy[ctx.author.id][item] -= amount
            collection.update_one(
                {"_id": ctx.author.id},
                {"$set": {"wallet": user["wallet"], item: user[item]}},
            )
            await ctx.reply(
                f"You successfully sold {amount} {item}(s)!",
                mention_author=False,
            )
        else:
            await ctx.reply(
                f"You do not have enough of {item}!", mention_author=False
            )

    @commands.command(aliases=["inventory"])
    @commands.guild_only()
    async def inv(self, ctx):
        items = [key for key in self.itemvalue]
        user_item_amount = {}
        user_item_list = []

        for item in items:
            user_item_amount[item] = (
                0
                if ctx.author.id not in self.users_in_db
                else self.economy[ctx.author.id][item]
            )
            user_item_list.append(
                f"{item.capitalize()}(s): {user_item_amount[item]}"
            )

        embed = discord.Embed(
            title=f"{ctx.author}'s inventory",
            description="\n".join(user_item_list),
            color=0xFFFF00,
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/759351806873567238/1091936550436229282/image.png?width=431&height=466"
        )
        await ctx.reply(embed=embed, mention_author=False)

    # fix this use the oly lb with users in server
    @commands.command(aliases=["leaderboard", "lb"])
    @commands.guild_only()
    async def rich(self, ctx, *, item="wallet"):
        lb_titles = {
            "wallet": "💰Top 5 richest users💰",
            "net worth": "💰Top 5 richest users💰",
            "bank": "💰Bank Leaderboard💰",
            "maxbank": "💰Bank Capacity💰",
            "laptop": "💻Laptop Leaderboard💻",
            "gun": "🔫Gun Leaderboard🔫",
            "lifesaver": "🧬Lifesaver Leaderboard🧬",
            "capybara": "Capybara Leaderboard",
            "instrument": "🎻Instrument Leaderboard🎻",
            "rod": "🎣Rod Leaderboard🎣",
            "bunny": "🐰Bunny Leaderboard🐰",
        }
        """units = {
            "laptop": "laptops",
            "gun": "guns",
            "lifesaver": "lifesavers",
            "capybara": "capybaras",
            "instrument": "instruments",
            "rod": "rods",
        }"""

        item = item.lower()

        if (
            item not in get_dict(ctx.author)
            and item != "net worth"
            or item == "_id"
        ):
            await ctx.reply("Please enter a valid item!", mention_author=False)
            return

        guild = self.bot.get_guild(ctx.guild.id)
        user_balances = {}
        users = []
        lb_list = []
        users = []

        for key in self.economy:
            user = guild.get_member(key)
            if user is not None:
                users.append(user)

        if item != "net worth":
            for u in range(len(users)):
                user_bal = self.economy[users[u].id][item]
                user_balances[
                    f"{users[u].name}#{users[u].discriminator}"
                ] = user_bal

        else:
            for u in range(len(users)):
                user_bal = 0
                for i in get_dict(ctx.author):
                    if i != "_id" and i != "maxbank":
                        if i in self.itemvalue:
                            user_bal += (
                                self.economy[users[u].id][i]
                                * self.itemvalue[i]
                            )
                        else:
                            user_bal += self.economy[users[u].id][i]

                user_balances[
                    f"{users[u].name}#{users[u].discriminator}"
                ] = user_bal

        length = len(user_balances)
        if length > 5:
            length = 5

        for key, value in sorted(
            user_balances.items(), reverse=True, key=lambda item: item[1]
        ):
            if value != 0:
                string = (
                    f" {key} : ${value}"
                    if (
                        item == "wallet"
                        or item == "bank"
                        or item == "maxbank"
                        or item == "net worth"
                    )
                    else f" {key} : {value}"
                )
                lb_list.append(string)

        if len(lb_list) < 1:
            lb_list.append(
                "🥇Nobody : $0"
                if (
                    item == "wallet"
                    or item == "bank"
                    or item == "maxbank"
                    or item == "net worth"
                )
                else f"🥇Nobody : 0"
            )
        else:
            if len(lb_list) > 0:
                lb_list[0] = f"🥇{lb_list[0]}"
            if len(lb_list) > 1:
                lb_list[1] = f"🥈{lb_list[1]}"
            if len(lb_list) > 2:
                lb_list[2] = f"🥉{lb_list[2]}"
            if len(lb_list) > 3:
                lb_list[3] = f"4️⃣{lb_list[3]}"
            if len(lb_list) > 4:
                lb_list[4] = f"5️⃣{lb_list[4]}"

        lb_string = "\n".join(lb_list[0:5])

        embed = discord.Embed(
            title=f"{item.capitalize()} Leaderboard"
            if item not in lb_titles
            else lb_titles[item],
            description=lb_string,
            color=0xEEE657,
        )
        await ctx.send(embed=embed)

    # ---------------------------------- Gambling commands ---------------------------------------
    @commands.command(aliases=["stats"])
    @commands.guild_only()
    async def gamblestats(self, ctx, member: discord.User = None):
        if not member:
            member = ctx.author

        if member.id not in self.users_in_db:
            self.process_user(member)

        commands = ["bj", "slots"]
        stats = {
            "bj": [],
            "slots": [],
        }

        for c in commands:
            max_win = self.economy[member.id][c]["maxwin"]
            max_loss = self.economy[member.id][c]["maxloss"]
            win = self.economy[member.id][c]["win"]
            loss = self.economy[member.id][c]["loss"]
            stats[c].append(f"Net Winnings: ${win - loss}")
            stats[c].append(f"Total Winnings: ${win}")
            stats[c].append(f"Total losses: ${loss}")
            stats[c].append(f"Maximum win: ${max_win}")
            stats[c].append(f"Maximum loss: ${max_loss}")

        embed = discord.Embed(
            title=f"{member}'s gambling stats",
            description="",
            color=0xEEE657,
        )

        embed.add_field(name="BlackJack", value="\n".join(stats["bj"]))
        embed.add_field(name="Slots", value="\n".join(stats["slots"]))

        await ctx.reply(embed=embed, mention_author=False)

    @gamblestats.error
    async def gamblestats_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.reply(
                "Please mention a valid user!", mention_author=False
            )
        else:
            raise error

    @commands.command(aliases=["bj"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack(self, ctx, money=None):
        MAX_GAMBLE = 500000

        if not money:
            money = 0

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        try:
            money = int(money)
        except ValueError:
            if money.lower() == "max" or money.lower() == "all":
                money = min(user_bal, MAX_GAMBLE)
            else:
                self.blackjack.reset_cooldown(ctx)
                await ctx.reply(
                    "You must enter a valid amount of money!",
                    mention_author=False,
                )
                return

        if user_bal < money:
            self.blackjack.reset_cooldown(ctx)
            await ctx.reply(
                "You cannot gamble more than you have!", mention_author=False
            )
            return

        if money < 0:
            self.blackjack.reset_cooldown(ctx)
            await ctx.reply(
                "You cannot gamble negative money!", mention_author=False
            )
            return

        if money > MAX_GAMBLE:
            money = MAX_GAMBLE
            await ctx.reply(
                f"You can only gamble ${MAX_GAMBLE}", mention_author=False
            )

        self.economy[ctx.author.id][
            "wallet"
        ] -= money  # remove money for a bit

        win_rate = {"W": 1, "D": 0, "L": -1, "BJ": 1.5}
        possible_cards = {str(i): i for i in range(2, 11)} | {
            "J": 10,
            "Q": 10,
            "K": 10,
            "A": 11,
        }

        card_1, card_2 = get_starting_cards(possible_cards)
        score = get_starting_score(possible_cards, card_1, card_2)
        player_hand = [card_1, card_2]
        dealer_card_1, dealer_card_2 = get_starting_cards(possible_cards)
        dealer_hand = [dealer_card_1, dealer_card_2]

        embed = discord.Embed(
            title=f"Capsino: ${money}",
            description=f"**Your Hand**: [{' '.join(player_hand)}] ({score})\n**Dealers Hand**: [{dealer_hand[0]} ?]",
            color=0xFFFF00,
        )

        msg = await ctx.reply(embed=embed)

        bj = BlackJack(ctx.author)
        bj.hit = True

        while score < 21 and bj.hit:
            bj = BlackJack(ctx.author)
            msg = await msg.edit(view=bj)
            bj.message = msg
            await bj.wait()

            if bj.hit or bj.double:
                score = run_bj(possible_cards, player_hand, score)
                embed = discord.Embed(
                    title=f"Capsino ${money}",
                    description=f"**Your Hand**: [{' '.join(player_hand)}] ({score})\n**Dealers Hand**: [{dealer_hand[0]} ?]",
                    color=0xFFFF00,
                )
                msg = await msg.edit(embed=embed, view=bj)

        dealer_hand, dealer_score = get_dealer_score(
            possible_cards, dealer_hand
        )
        dealer_msg = (
            f"**Dealer Hand**: [{' '.join(dealer_hand)}] ({dealer_score})"
        )
        result = get_result(player_hand, score, dealer_hand, dealer_score)

        multiplier = (
            win_rate[result] if not bj.double else win_rate[result] * 2
        )
        if result == "L" and bj.double:
            multiplier = -1

        amount = round(multiplier * money)
        user_bal += amount

        """if result == "L":
            self.economy[ctx.author.id]["bj"]["loss"] += amount
            if abs(amount) > self.economy[ctx.author.id]["bj"]["maxloss"]:
                self.economy[ctx.author.id]["bj"]["maxloss"] = abs(amount)
        
        if result == "W" or result == "BJ":
            self.economy[ctx.author.id]["bj"]["win"] += amount
            if abs(amount) > self.economy[ctx.author.id]["bj"]["maxwin"]:
                self.economy[ctx.author.id]["bj"]["maxwin"] = abs(amount)"""

        self.economy[ctx.author.id]["wallet"] = user_bal
        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank

        if result == "W" or result == "BJ":
            title = f"Capsino: {ctx.author} won ${abs(amount)}!"

            self.economy[ctx.author.id]["bj"]["win"] += amount
            if abs(amount) > self.economy[ctx.author.id]["bj"]["maxwin"]:
                self.economy[ctx.author.id]["bj"]["maxwin"] = abs(amount)

        elif result == "D":
            title = "Capsino: Draw!"
        else:
            title = f"Capsino: Dealer wins ${money}!"

            self.economy[ctx.author.id]["bj"]["loss"] += amount
            if abs(amount) > self.economy[ctx.author.id]["bj"]["maxloss"]:
                self.economy[ctx.author.id]["bj"]["maxloss"] = abs(amount)

        collection.update_one(
            {"_id": ctx.author.id},
            {
                "$set": {
                    "wallet": user_bal,
                    "maxbank": max_bank,
                    "bj": self.economy[ctx.author.id]["bj"],
                }
            },
        )

        embed = discord.Embed(
            title=title,
            description=f"**Your Hand**: [{' '.join(player_hand)}] ({score})\n{dealer_msg}",
            color=0xFFFF00,
        )
        await msg.edit(embed=embed)

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        else:
            self.blackjack.reset_cooldown(ctx)
            raise error

    @commands.command(aliases=["slots"])
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gamble(self, ctx, money=None):
        success = random.randint(1, 4)
        if not money:
            self.gamble.reset_cooldown(ctx)
            await ctx.reply(
                "Please specify an amount to gamble!", mention_author=False
            )
            return

        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        try:
            money = int(money)
        except ValueError:
            if money.lower() == "max" or money.lower() == "all":
                money = user_bal
            else:
                await self.gamble.reset_cooldown(ctx)
                await ctx.reply(
                    "You must enter a valid amount of money!",
                    mention_author=False,
                )
                return

        if user_bal < money:
            await ctx.reply(
                "You cannot gamble more than you have!", mention_author=False
            )
            self.gamble.reset_cooldown(ctx)
            return
        if money <= 0:
            await ctx.reply(
                "You cannot gamble $0 or negative money!", mention_author=False
            )
            self.gamble.reset_cooldown(ctx)
            return

        msg = await ctx.reply("🎰 | Spinning......", mention_author=False)
        if success == 1:
            multiplier = random.randint(1, 501)
            if multiplier == 500 or multiplier == 69:
                money *= 10

            user_bal += money
            self.economy[ctx.author.id]["wallet"] = user_bal
            self.economy[ctx.author.id]["slots"]["win"] += money
            if money > self.economy[ctx.author.id]["slots"]["maxwin"]:
                self.economy[ctx.author.id]["slots"]["maxwin"] = money

            await asyncio.sleep(2)
            await msg.edit(
                content=f"The slot machine spins and you win ${money}!"
            )
        else:
            user_bal -= money
            self.economy[ctx.author.id]["wallet"] = user_bal
            self.economy[ctx.author.id]["slots"]["loss"] += money
            if money > self.economy[ctx.author.id]["slots"]["maxloss"]:
                self.economy[ctx.author.id]["slots"]["maxloss"] = money

            await asyncio.sleep(2)
            await msg.edit(
                content=f"the slot machine spins and you lose ${money}!"
            )

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank

        collection.update_one(
            {"_id": ctx.author.id},
            {
                "$set": {
                    "wallet": user_bal,
                    "maxbank": max_bank,
                    "slots": self.economy[ctx.author.id]["slots"],
                }
            },
        )

    @gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("Please specify a valid amount to gamble!")
            self.gamble.reset_cooldown(ctx)
        else:
            self.gamble.reset_cooldown(ctx)
            raise error

    @commands.command(aliases=["stonks", "stocks"])
    @commands.guild_only()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def invest(self, ctx, money=None):
        MAX_INVEST = 100000

        if not money:
            await ctx.reply(
                "Please enter a valid amount to invest!", mention_author=False
            )
            self.invest.reset_cooldown(ctx)
            return

        success = random.randint(1, 3)
        if ctx.author.id not in self.users_in_db:
            self.process_user(ctx.author)

        user = self.economy[ctx.author.id]
        user_bal = user["wallet"]

        try:
            money = int(money)
        except ValueError:
            if money.lower() == "max" or money.lower() == "all":
                money = min(user_bal, MAX_INVEST)
            else:
                await self.invest.reset_cooldown(ctx)
                return await ctx.reply(
                    "You must enter a valid amount of money!",
                    mention_author=False,
                )

        if money > user_bal or money > MAX_INVEST:
            if money > MAX_INVEST and money <= user_bal:
                money = MAX_INVEST
                await ctx.reply(
                    f"You cannot invest more than ${money}! But since I am nice I will let you invest $100000",
                    mention_author=False,
                )
            else:
                await ctx.reply(
                    "You cannot invest more than you have! But since I am nice, I'll let you invest all your money",
                    mention_author=False,
                )  # this and the more money than you have thing works
                money = user_bal
        elif money <= 0:
            await ctx.reply(
                "You cannot invest negative or 0 money!", mention_author=False
            )
            self.invest.reset_cooldown(ctx)
            return

        if success == 1:
            await ctx.reply(
                f"You invested money in the stock market but your investment didn't do well so you lost ${money}!",
                mention_author=False,
            )
            user_bal -= money

        else:
            chance = random.randint(1, 15)
            if chance == 3:
                multiplier = random.randint(3, 5)
            else:
                multiplier = random.randint(1, 2)
            money = money * multiplier
            user_bal += money
            await ctx.reply(
                f"Your investment paid off! You earned ${money}!",
                mention_author=False,
            )

        max_bank = get_max_bank(user)
        self.economy[ctx.author.id]["maxbank"] = max_bank
        self.economy[ctx.author.id]["wallet"] = user_bal

        collection.update_one(
            {"_id": ctx.author.id},
            {"$set": {"wallet": user_bal, "maxbank": max_bank}},
        )

    @invest.error
    async def invest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Woah there, slow down, please try again in {seconds_to_timestr(error.retry_after)}!"
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("Please specify a valid amount to invest!")
            self.invest.reset_cooldown(ctx)
        else:
            self.invest.reset_cooldown(ctx)
            raise error

    # ---------------------------------- Commands related to balance ---------------------------------------

    @commands.command(aliases=["transfer"])
    @commands.guild_only()
    async def give(self, ctx, member: discord.User = None, money: int = None):
        if not member:
            await ctx.reply("You need to specify a user to give money to!")
            return

        if not money:
            await ctx.reply("You need to specify an amount to give!")
            return

        # if member.bot:
        # await ctx.reply("You cannot give money to a bot!")
        # return

        if money <= 0:
            await ctx.reply(
                "You cannot give someone $0 or negative money!",
                mention_author=False,
            )
            return

        if ctx.author.id not in self.users_in_db:
            await ctx.reply(
                "You cannot give more money than you own!",
                mention_author=False,
            )
            return

        user = self.economy[
            ctx.author.id
        ]  # user = collection.find_one({"_id": ctx.author.id})

        if member.id not in self.users_in_db:
            self.process_user(member)

        target = self.economy[member.id]
        user_bal = user["wallet"]
        member_bal = target["wallet"]

        if money > user_bal:
            await ctx.reply(
                "You cannot give more money than you own!",
                mention_author=False,
            )
            return

        member_bal += money
        user_bal -= money
        self.economy[ctx.author.id]["wallet"] = user_bal
        self.economy[member.id]["wallet"] = member_bal

        collection.update_one(
            {"_id": ctx.author.id}, {"$set": {"wallet": user_bal}}
        )
        collection.update_one(
            {"_id": member.id}, {"$set": {"wallet": member_bal}}
        )

        await ctx.reply(
            f"Successfully transfered ${money} to {member}",
            mention_author=False,
        )

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            await ctx.reply("Please specify a valid user to give money to!")
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("Please specify a valid amount to give!")
        else:
            raise error

    @commands.command(aliases=["dep"])
    @commands.guild_only()
    async def deposit(self, ctx, money=None):
        if not money:
            await ctx.reply(
                "You did not specify an amount to deposit!",
                mention_author=False,
            )
            return

        if ctx.author.id not in self.users_in_db:
            await ctx.reply(
                "You cannot deposit more money than you have!",
                mention_author=False,
            )
            return

        user = self.economy[
            ctx.author.id
        ]  # user = collection.find_one({"_id": ctx.author.id})
        user_bal = user["wallet"]
        user_bank = user["bank"]
        max_bank = user["maxbank"]

        try:
            money = int(money)
        except ValueError:
            if money.lower() == "all":
                if user_bank == max_bank:
                    await ctx.reply(
                        "Your bank is already full!", mention_author=False
                    )
                    return
                if user_bal >= max_bank - user_bank:
                    money = max_bank - user_bank
                else:
                    money = user_bal
            else:
                await ctx.reply(
                    "You did not send a valid amount to deposit!",
                    mention_author=False,
                )
                return

        if money <= 0:
            await ctx.reply(
                "You cannot deposit $0 or negative money!",
                mention_author=False,
            )
            return
        elif money > user_bal:
            await ctx.reply(
                "You cannot deposit more than you own!", mention_author=False
            )
            return
        elif money + user_bank > max_bank:
            await ctx.reply(
                "You cannot deposit more than you can fit in your bank!",
                mention_author=False,
            )
            return
        else:
            user["wallet"] -= money
            user["bank"] += money
            # self.economy[ctx.author.id]["wallet"] -= money
            collection.update_one(
                {"_id": ctx.author.id},
                {"$set": {"wallet": user["wallet"], "bank": user["bank"]}},
            )
            await ctx.reply(
                f"Successfully deposited ${money}!", mention_author=False
            )

    @commands.command(aliases=["with"])
    @commands.guild_only()
    async def withdraw(self, ctx, money=None):
        if not money:
            await ctx.reply(
                "You did not specify an amount to withdraw!",
                mention_author=False,
            )
            return

        if ctx.author.id not in self.users_in_db:
            await ctx.reply(
                "You cannot withdraw more than what is in your bank!",
                mention_author=False,
            )
            return

        user = self.economy[
            ctx.author.id
        ]  # user = collection.find_one({"_id": ctx.author.id})
        user_bal = user["wallet"]
        user_bank = user["bank"]

        try:
            money = int(money)
        except ValueError:
            if money.lower() == "all":
                money = user_bank
            else:
                await ctx.reply(
                    "You did not send a valid amount to withdraw!",
                    mention_author=False,
                )
                return
        if money < 0:
            await ctx.reply(
                "You cannot withdraw negative money!", mention_author=False
            )
            return
        elif money > user_bank:
            await ctx.reply(
                "You cannot withdraw more than what is in your bank!",
                mention_author=False,
            )
        else:
            user_bal += money
            user_bank -= money

            self.economy[ctx.author.id]["wallet"] += money
            self.economy[ctx.author.id]["bank"] -= money
            collection.update_one(
                {"_id": ctx.author.id},
                {"$set": {"wallet": user_bal, "bank": user_bank}},
            )
            await ctx.reply(
                f"Successfully withdrew ${money}", mention_author=False
            )

    @commands.command(aliases=["balance"])
    @commands.guild_only()
    async def bal(self, ctx, *, member: discord.User = None):
        if not member:
            member = ctx.author

        # if member.bot:
        # user_bal = 0
        # user_bank = 0
        # user_max = 0

        if member.id not in self.users_in_db:
            self.process_user(member)

        user = self.economy[member.id]
        user_bal = user["wallet"]
        user_bank = user["bank"]
        user_max = user["maxbank"]

        embed = discord.Embed(
            title=f"{member}'s balance",
            description=f"Wallet: ${user_bal}\nBank: {user_bank}/{user_max}",
            color=0xFFFF00,
        )
        # update_user(collection, eco, ctx.author)
        await ctx.send(embed=embed)


# discord.ext.commands.errors.CommandInvokeError: Command raised an exception: InvalidDocument: cannot encode object: <Member id=646597016205656064 name='Venimental' discriminator='1289' bot=False nick=None guild=<Guild id=696453389625720873 name='Veni Bot & pycubescrambler python module support' shard_id=None chunked=True member_count=20>>, of type: <class 'discord.member.Member'>


async def setup(bot):
    await bot.add_cog(Economy(bot))
