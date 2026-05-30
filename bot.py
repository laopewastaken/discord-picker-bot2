import discord
import random
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

SOURCE_CHANNEL_ID = 1500337463900766238
TARGET_CHANNEL_ID = 1500338896188346398


# ─────────────────────────────
# THREAD TIERS
# ─────────────────────────────

COMMON_THREAD_IDS = {
    1500338384231465050, #SAACC
    1500338187833311323, #SAMA
    1500338030899236964 #EMS
}
UNCOMMON_THREAD_IDS = {
}
RARE_THREAD_IDS = {
}
SUPER_RARE_THREAD_IDS = {
    1500338794270822460, #SAACC Holo
    1500338708606615664, #SAMA Holo
    1500338580877344828 #EMS Holo
}
EPIC_THREAD_IDS = {
    1510026120060473435 #%5 Sig
}
LEGENDARY_THREAD_IDS = {
}



# ─────────────────────────────
# STATS
# ─────────────────────────────

stats_counter = {
    "A": 0,
    "B": 0,
    "C": 0,
    "D": 0,
    "E": 0,
    "F": 0
}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ─────────────────────────────
# THREAD LOADER
# ─────────────────────────────

async def get_all_threads(channel):
    threads = []
    threads.extend(channel.threads)

    async for t in channel.archived_threads(limit=None):
        threads.append(t)

    return threads


async def collect_messages(channel):

    threads = await get_all_threads(channel)

    pools = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": [],
        "F": []
    }

    for thread in threads:

        async for msg in thread.history(limit=100):
            if msg.author.bot:
                continue

            if thread.id in COMMON_THREAD_IDS:
                pools["A"].append(msg)
            elif thread.id in UNCOMMON_THREAD_IDS:
                pools["B"].append(msg)
            elif thread.id in RARE_THREAD_IDS:
                pools["C"].append(msg)
            elif thread.id in SUPER_RARE_THREAD_IDS:
                pools["D"].append(msg)
            elif thread.id in EPIC_THREAD_IDS:
                pools["E"].append(msg)
            elif thread.id in LEGENDARY_THREAD_IDS:
                pools["F"].append(msg)

    return pools


# ─────────────────────────────
# MESSAGE HANDLING
# ─────────────────────────────

def extract_text(message):
    parts = []

    if message.content:
        parts.append(message.content)

    if message.embeds:
        e = message.embeds[0]
        if e.title:
            parts.append(e.title)
        if e.description:
            parts.append(e.description)

    return "\n".join(parts).strip()


async def send_message(message, channel):
    content = extract_text(message)

    files = []
    for att in message.attachments:
        try:
            files.append(await att.to_file())
        except:
            pass

    if files:
        await channel.send(content=content or None, files=files)
    else:
        await channel.send(content=content or "(No content)")


# ─────────────────────────────
# TIER PICKER
# ─────────────────────────────

def pick_tier():

    r = random.random()

    if r < 0.001:
        return "F"  # Legendary
    elif r < 0.010:
        return "E"  # Epic
    elif r < 0.040:
        return "D"  # Super Rare
    elif r < 0.110:
        return "C"  # Rare
    elif r < 0.460:
        return "B"  # Uncommon
    else:
        return "A"  # Common


# ─────────────────────────────
# MAIN COMMAND
# ─────────────────────────────

@bot.command()
async def roll(ctx, amount: int):

    if amount <= 0:
        await ctx.send("Give me a number above 0.")
        return

    if amount > 100:
        await ctx.send("Max 100 rolls.")
        return

    source = bot.get_channel(SOURCE_CHANNEL_ID)
    target = bot.get_channel(TARGET_CHANNEL_ID)

    if not source or not target:
        await ctx.send("Channel not found.")
        return

    pools = await collect_messages(source)

    used = set()
    sent = 0
    attempts = 0
    max_attempts = amount * 15

    # ───────── NEW: recap storage ─────────
    recap_texts = []

    while sent < amount and attempts < max_attempts:
        attempts += 1

        tier = pick_tier()
        pool = pools.get(tier, [])

        if not pool:
            pool = pools["A"]

        if not pool:
            continue

        msg = random.choice(pool)

        if msg.id in used:
            continue

        used.add(msg.id)

        await send_message(msg, target)

        text = extract_text(msg)
        if text:
            recap_texts.append(text)

        stats_counter[tier] += 1
        sent += 1

    # ───────── FINAL RECAP MESSAGE ─────────
    if recap_texts:
        formatted = "; ".join(f"`{t}`" for t in recap_texts)

        await target.send(
            f"{ctx.author.mention}, your last {len(recap_texts)} rolls:\n{formatted}"
        )


# ─────────────────────────────
# STATS
# ─────────────────────────────

@bot.command()
async def stats(ctx):

    total = sum(stats_counter.values())

    if total == 0:
        await ctx.send("No rolls yet.")
        return

    await ctx.send(
        "📊 **Tier Stats**\n"
        f"A (Common): {stats_counter['A']}\n"
        f"B (Uncommon): {stats_counter['B']}\n"
        f"C (Rare): {stats_counter['C']}\n"
        f"D (Super Rare): {stats_counter['D']}\n"
        f"E (Epic): {stats_counter['E']}\n"
        f"F (Legendary): {stats_counter['F']}\n"
    )


@bot.command()
async def resetstats(ctx):
    global stats_counter
    stats_counter = {k: 0 for k in stats_counter}
    await ctx.send("📊 Stats reset.")


bot.run(TOKEN)
