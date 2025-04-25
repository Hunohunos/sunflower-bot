import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask

# Store previous messages
message_history = []

# Initialize Flask app for keeping the service alive
app = Flask(__name__)

# Set up the Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@app.route("/")
def home():
    return "Bot is alive"

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

# Async function to start the bot and the Flask server
async def start_bot():
    # Start the Flask app in the background
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(os.environ["DISCORD_TOKEN"]))

    # Run Flask app (this will keep the bot alive)
    app.run(host="0.0.0.0", port=8080)

# Running both the Flask web server and the Discord bot with asyncio
if __name__ == "__main__":
    asyncio.run(start_bot())
