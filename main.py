import os
import asyncio
import random
import selfcord
from dotenv import load_dotenv
from conversations import SCENARIOS

load_dotenv()

class KessokuBot:
    def __init__(self):
        self.tokens = os.getenv("TOKENS", "").split(",")
        self.vc_id = int(os.getenv("VC_ID", 0))
        self.clients = {}

    async def initialize_clients(self):
        for token in self.tokens:
            token = token.strip()
            if not token: continue
            
            client = selfcord.Client()
            self.clients[token] = client
            asyncio.create_task(client.start(token))

    async def run_conversation(self, scenario_index=None):
        scenario = SCENARIOS[scenario_index or random.randint(0, len(SCENARIOS) - 1)]
        
        for name, text in scenario:
            # Logic to find the active client and send to VC text chat
            for client in self.clients.values():
                if client.user and client.user.name == name:
                    channel = client.get_channel(self.vc_id)
                    if channel:
                        await channel.trigger_typing()
                        await asyncio.sleep(random.uniform(1.0, 2.0))
                        await channel.send(text)
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                    break

async def main():
    bot = KessokuBot()
    await bot.initialize_clients()
    await asyncio.sleep(5) # Wait for connections
    await bot.run_conversation()

if __name__ == "__main__":
    asyncio.run(main())