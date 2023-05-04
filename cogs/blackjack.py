import discord
import random
import math

def get_starting_cards(possible_cards):
    card_1 = random.choice(list(possible_cards.keys()))
    card_2 = random.choice(list(possible_cards.keys()))

    return card_1, card_2


def get_starting_score(possible_cards, card_1, card_2):
    score = possible_cards[card_1]
    score += possible_cards[card_2]
    return ace_filter([card_1, card_2], score)


def get_dealer_score(possible_cards, dealer_hand):

    score = sum([possible_cards[s] for s in dealer_hand])

    while score <= 16:
        score = run_bj(possible_cards, dealer_hand, score)

    return dealer_hand, score


def ace_filter(hand, score):
    ace_count = hand.count("A")
    num = min(ace_count, max(0, math.ceil((score - 21) / 10)))
    score -= num * 10
    return score


def run_bj(possible_cards, hand, score):

    card = random.choice(list(possible_cards.keys()))
    hand.append(card)
    score = sum([possible_cards[s] for s in hand])

    if score > 21:
        score = ace_filter(hand, score)

    return score


def is_blackjack(hand, score):
    return len(hand) == 2 and score == 21


def get_result(player_hand, score, dealer_hand, dealer_score):

    if score > 21:
        return "L"

    if dealer_score > 21:
        return "W"

    if is_blackjack(player_hand, score) and not is_blackjack(dealer_hand, dealer_score):
        result = "BJ"
    elif (
        is_blackjack(dealer_hand, dealer_score)
        and not is_blackjack(player_hand, score)
        or score < dealer_score
    ):
        result = "L"
    elif (
        is_blackjack(dealer_hand, dealer_score)
        and is_blackjack(player_hand, score)
        or score == dealer_score
    ):
        result = "D"
    else:
        result = "W"

    return result

class BlackJack(discord.ui.View):
    def __init__(self, author):
        self.author = author
        self.hit = False
        self.double = False
        super().__init__(timeout=30)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        await self.message.channel.send(
            f"{self.author.mention}, You timed out!", reference=self.message
        )
        await self.disable_all_items()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    # creates a button when pressed you send message
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def Hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Hit", ephemeral=True)
        self.hit = True
        self.stop()

    @discord.ui.button(label="Double", style=discord.ButtonStyle.primary)
    async def double_down(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("Double Down", ephemeral=True)
        self.double = True
        await self.disable_all_items()
        self.stop()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Stand", ephemeral=True)
        await self.disable_all_items()
        self.stop()
