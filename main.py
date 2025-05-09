from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import random
import os

# Store previous messages
message_history = []

# Set up bot intents and instance
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Store the message
    message_history.append(message)
    if len(message_history) > 100:
        message_history.pop(0)

    # Respond to "hello"
    if "hello" in message.content.lower():
        await message.channel.send(f"Hey {message.author.display_name}!")

    # Check if bot was pinged
    bot_was_mentioned = bot.user in message.mentions

    # Determine whether to mimic: either pinged or 1-in-5 chance
    should_mimic = bot_was_mentioned or random.randint(1, 5) == 1

    if should_mimic and len(message_history) > 1:
        valid_choices = [msg for msg in message_history if not msg.author.bot and msg != message]
        if valid_choices:
            random_message = random.choice(valid_choices)
            content_to_send = ""

            # If the message was a reply, include the quoted part
            if random_message.reference and random_message.reference.message_id:
                try:
                    replied_to = await message.channel.fetch_message(random_message.reference.message_id)
                    if replied_to:
                        content_to_send += f"> {replied_to.author.display_name}: {replied_to.content}\n"
                except discord.NotFound:
                    pass

            # Add the message content
            content_to_send += random_message.content

            # Include image attachments, if any
            files = [await a.to_file() for a in random_message.attachments] if random_message.attachments else None

            # Send the mimicked message
            await message.channel.send(content=content_to_send, files=files)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="fuhgeddaboudit")
@commands.has_permissions(manage_messages=True)
async def clearhistory(ctx):
    """Clear the message history (admin only)."""
    message_history.clear()
    await ctx.send(f"{ctx.author.display_name}? huh whuh what am i doing here, what the fuck?")

@clearhistory.error
async def clearhistory_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Absolutely not, go PLANT yourself.")

# Run the bot with your token from the environment variable
bot.run(os.environ["DISCORD_TOKEN"])
