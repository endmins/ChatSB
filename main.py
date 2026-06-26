import os
import asyncio
import random
import datetime
import selfcord
from dotenv import load_dotenv
from conversations import SCENARIOS

load_dotenv()

class KessokuHouse:
    def __init__(self):
        self.tokens = [t.strip() for t in os.getenv("TOKENS", "").split(",") if t.strip()]
        self.vc_id = int(os.getenv("VC_ID", 0))
        self.clients = {}
        self.count_file = "daily_count.txt"

    def get_daily_status(self):
        today = str(datetime.date.today())
        if not os.path.exists(self.count_file):
            return today, 0
        with open(self.count_file, "r") as f:
            date, count = f.read().split(",")
        return date, int(count)

    def update_daily_count(self):
        today, count = self.get_daily_status()
        with open(self.count_file, "w") as f:
            f.write(f"{today},{count + 1}")

    async def start_instance(self, token):
        client = selfcord.Client()
        @client.event
        async def on_ready():
            channel = client.get_channel(self.vc_id)
            if channel: await channel.connect()
        self.clients[token] = client
        await client.start(token)

    async def execute_scenario(self):
        date, count = self.get_daily_status()
        if date != str(datetime.date.today()):
            count = 0 # Reset for new day
        
        if count >= 3:
            print("[LIMIT] Daily limit reached. Going to sleep.")
            return

        print(f"[SYSTEM] Running conversation {count + 1}/3...")
        scenario = random.choice(SCENARIOS)
        last_message = None

        for name, text in scenario:
            client = next((c for c in self.clients.values() if c.user and c.user.name == name), None)
            if not client: continue
            
            channel = client.get_channel(self.vc_id)
            if not channel: continue

            await asyncio.sleep(random.uniform(3.0, 5.0))
            await channel.trigger_typing()
            await asyncio.sleep(len(text) / 6.0)

            if last_message:
                last_message = await last_message.reply(text)
            else:
                last_message = await channel.send(text)
        
        self.update_daily_count()
        print("[SYSTEM] Sequence finished. Daily limit updated.")

async def main():
    house = KessokuHouse()
    await asyncio.gather(*(house.start_instance(t) for t in house.tokens))
    await asyncio.sleep(10)
    await house.execute_scenario()

if __name__ == "__main__":
    asyncio.run(main())