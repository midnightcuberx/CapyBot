import discord
import random


class FightView(discord.ui.View):
    def __init__(self, author, health, timeout):
        self.author = author
        self.health = health
        self.button_pressed = False
        self.damage = 0
        super().__init__(timeout=timeout)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        await self.message.channel.send(
            f"{self.author} timed out and ran away from the fight!"
        )
        await self.disable_all_items()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    def get_damage(self):
        chance = random.randint(1, 100)
        if chance == 1:
            self.damage = 100
        elif chance > 1 and chance < 5:
            t = random.randint(70, 90)
            self.damage = 15 + round(self.health * t / 100)
            if self.damage > 99:
                self.damage = 99
        elif chance > 75:
            t = random.randint(30, 50)
            self.damage = 10 + round(self.health * t / 100)
        else:
            b = random.randint(0, 5)
            t = random.randint(0, 30)
            self.damage = b + round(self.health * t / 100)

    # creates a button when pressed you send message
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.get_damage()

        await interaction.response.send_message(
            f"You dealt {self.damage} damage to your opponent!", ephemeral=True
        )
        self.button_pressed = True
        self.stop()

    @discord.ui.button(label="Run away", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"{self.author} ran away from the fight!"
        )
        self.button_pressed = False
        await self.disable_all_items()
        self.stop()


class Challenge(discord.ui.View):
    def __init__(self, author, timeout):
        self.author = author
        self.accepted = False
        super().__init__(timeout=timeout)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        await self.message.channel.send(
            f"{self.author} declined your challenge by timeout!"
        )
        await self.disable_all_items()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    # creates a button when pressed you send message
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"{self.author} accepted your challenge!"
        )
        self.accepted = True
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            f"{self.author} declined your challenge!"
        )
        self.accepted = False
        await self.disable_all_items()
        self.stop()
