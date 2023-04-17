import discord
import math
from .viewclasses import FightView


async def button(ctx, msg, member: discord.User):
    # view = discord.ui.View()
    count = 0
    # user_health = 100
    # member_health = 100
    user_health = 100
    member_health = 100

    # Set up view and basic stuff
    view = FightView(ctx.author, timeout=30)
    msg = await msg.edit(content=f"{ctx.author}'s turn", view=view)
    view.message = msg
    await view.wait()
    member_health -= view.damage
    button_pressed = view.button_pressed

    while button_pressed and user_health > 0 and member_health > 0:
        if count % 2 == 0:
            view = FightView(member, timeout=30)
            msg = await msg.edit(
                content=f"**{member}'s turn**\n{ctx.author}'s health: {user_health}\n{member}'s health: {member_health}",
                view=view,
            )
        else:
            view = FightView(ctx.author, timeout=30)
            msg = await msg.edit(
                content=f"**{ctx.author}'s turn**\n{ctx.author}'s health: {user_health}\n{member}'s health: {member_health}",
                view=view,
            )

        view.message = msg
        await view.wait()

        if count % 2 == 0:
            user_health -= view.damage
        else:
            member_health -= view.damage

        button_pressed = view.button_pressed
        count += 1

    if button_pressed is False:
        winner = ctx.author if count % 2 == 1 else member
    else:
        winner = ctx.author if user_health > 0 else member  # doesnt work if runaway

    await msg.edit(
        content=f"**{ctx.author} vs {member}**\n{winner.mention} won in {math.ceil((count+1)/2)} round(s)!"
    )

    return winner
