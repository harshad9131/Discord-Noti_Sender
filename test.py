import discord
import requests
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# ====== CONFIG ======
TOKEN = os.getenv("DISCORD_TOKEN")   # paste your bot token here
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))   # paste your channel ID here
CHECK_INTERVAL = 3600  # check every hour
# ====================

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sent_today = set()  # to avoid duplicate alerts

async def check_contests():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Could not find the channel. Check CHANNEL_ID!")
        return

    while not client.is_closed():
        print("🔎 Checking Codeforces contests...")
        try:
            response = requests.get("https://codeforces.com/api/contest.list", timeout=10).json()
            contests = response['result']

            for contest in contests:
                if contest['phase'] != "BEFORE":
                    continue  # only upcoming contests

                start_time = datetime.utcfromtimestamp(contest['startTimeSeconds'])
                tomorrow = datetime.utcnow() + timedelta(days=1)

                # If contest is tomorrow
                if start_time.date() == tomorrow.date():
                    key = contest['id']
                    if key not in sent_today:
                        msg = (
                            f"@everyone 🚀 **Upcoming Codeforces Contest!**\n"
                            f"**Contest:** {contest['name']}\n"
                            f"**Start Time:** {start_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
                            f"**Link:** https://codeforces.com/contest/{contest['id']}"
                        )
                        await channel.send(msg)
                        print(f"✅ Sent alert for {contest['name']}")
                        sent_today.add(key)
        except Exception as e:
            print(f"❌ Error fetching Codeforces: {e}")

        # reset alerts at midnight UTC
        if datetime.utcnow().hour == 0:
            sent_today.clear()

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f"✅ Bot logged in as {client.user}")
    await client.get_channel(CHANNEL_ID).send("@everyone Bot is online! 🎉")

# ---- Async main to run bot and tasks ----
async def main():
    async with client:
        asyncio.create_task(check_contests())
        await client.start(TOKEN)

asyncio.run(main())
