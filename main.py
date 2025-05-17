from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands, tasks
import random
import os
import datetime
import asyncio

# Store previous messages
message_history = []
MAX_HISTORY = 10000  # Hard cap

# Set up bot intents and instance
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

last_user_message_time = datetime.datetime.utcnow()
mimic_sent = False  # To prevent repeat mimics

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    random_mimic_loop.start()

@bot.event
async def on_message(message):
    global last_user_message_time, mimic_sent

    if message.author.bot:
        return

    last_user_message_time = datetime.datetime.utcnow()
    mimic_sent = False  # Reset mimic trigger

    # Store message
    message_history.append(message)
    if len(message_history) > MAX_HISTORY:
        message_history.pop(0)

    # Respond to "hello"
    if "hello" in message.content.lower():
        await message.channel.send(f"Hey {message.author.display_name}!")

    # Check if bot was pinged
    bot_was_mentioned = bot.user in message.mentions

    # Determine whether to mimic: either pinged or 1-in-10 chance
    should_mimic = bot_was_mentioned or random.randint(1, 10) == 1

    if should_mimic and len(message_history) > 1:
        valid_choices = [msg for msg in message_history if not msg.author.bot and msg != message]
        if valid_choices:
            random_message = random.choice(valid_choices)

            # Strip bot mention if present
            content = random_message.content.replace(f"<@{bot.user.id}>", "").strip()

            # Include attachments
            files = [await a.to_file() for a in random_message.attachments] if random_message.attachments else None

            await message.channel.send(content=content, files=files)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="fuhgeddaboudit")
@commands.has_permissions(manage_messages=True)
async def clearhistory(ctx):
    """Clear the message history (admin only)."""
    message_history.clear()
    await ctx.send(f"{ctx.author.display_name}? huh whuh what am I doing here, what the fuck?")

@clearhistory.error
async def clearhistory_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Absolutely not, go PLANT yourself.")

@bot.command(name="plsrember")
async def plsrember(ctx):
    """Load old messages from current channel."""
    loaded = 0
    try:
        async for msg in ctx.channel.history(limit=5255):
            if not msg.author.bot:
                message_history.append(msg)
                loaded += 1
                if len(message_history) >= MAX_HISTORY:
                    break
        await ctx.send(f"I... remember everything now. all your {loaded} sin is in my brain.")
    except discord.Forbidden:
        await ctx.send("I don't... remember, sorry.")
    except Exception as e:
        await ctx.send(f"Something went wrong: {e}")

@tasks.loop(minutes=10)
async def random_mimic_loop():
    global mimic_sent

    if mimic_sent:
        return

    now = datetime.datetime.utcnow()
    time_since_last = (now - last_user_message_time).total_seconds()

    if time_since_last >= 1800 and len(message_history) >= 2:
        if random.randint(1, 25) == 1:
            valid_messages = [m for m in message_history if not m.author.bot]
            if len(valid_messages) < 2:
                return

            random_reply_to = random.choice(valid_messages)
            random_message = random.choice([m for m in valid_messages if m.id != random_reply_to.id])

            content = random_message.content.replace(f"<@{bot.user.id}>", "").strip()
            files = [await a.to_file() for a in random_message.attachments] if random_message.attachments else None

            try:
                await random_reply_to.reply(content=content, files=files)
                mimic_sent = True
            except discord.HTTPException:
                pass

# Run the bot with your token from the environment variable
bot.run(os.environ["DISCORD_TOKEN"])
