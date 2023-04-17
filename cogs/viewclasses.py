import discord
import random


class FightView(discord.ui.View):
    def __init__(self, author, timeout):
        self.author = author
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

    # creates a button when pressed you send message
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        chance = random.randint(1, 11)
        if chance != 1:
            self.damage = random.randint(1, 11)
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
        await self.message.channel.send(f"{self.author} declined your challenge!")
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
