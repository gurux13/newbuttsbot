import asyncio
from twitchbot import Twitch, TwitchCallbacks, get_twitch_identity_data_from_env
from self_message_handler import SelfMessageHandler
from foreign_message_handler import ForeignMessageHandler
from startup import StartupHandler

    
class TrueTwitchCallbacks(TwitchCallbacks):
    def __init__(self):
        self.self_message_handler = SelfMessageHandler()
        self.foreign_message_handler = ForeignMessageHandler()
        self.startup_handler = StartupHandler()
    async def on_self_message(self, message, bot):
        await self.self_message_handler.on_message(message, bot)
    async def on_foreign_message(self, message, bot):
        await self.foreign_message_handler.on_message(message, bot)
    async def on_ready(self, bot):
        await self.startup_handler.on_bot_ready(bot)
        
      
async def main():
    identity = get_twitch_identity_data_from_env()
    twitch = Twitch(identity, TrueTwitchCallbacks())
    await twitch.start()
    
if __name__ == '__main__':
    asyncio.run(main())