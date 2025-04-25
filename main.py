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

    # 1 in 5 chance to mimic a random past message
    if random.randint(1, 5) == 1 and len(message_history) > 1:
        valid_choices = [msg for msg in message_history if not msg.author.bot and msg != message]
        if valid_choices:
            random_message = random.choice(valid_choices)
            await message.channel.send(f"{random_message.content}")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run the bot with your token from the environment variable
bot.run(os.environ["DISCORD_TOKEN"])
