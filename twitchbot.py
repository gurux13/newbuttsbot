import twitchio
from twitchio.ext import commands
from twitchio import eventsub
from twitchio import web
import logging
import asyncio
from dataclasses import dataclass
import os

@dataclass
class TwitchIdentityData:
    client_id: str
    client_secret: str
    bot_id: str
    user_token: str
    user_refresh_token: str

def get_twitch_identity_data_from_env():
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    bot_id = os.getenv('TWITCH_BOT_ID')
    user_token = os.getenv('TWITCH_USER_TOKEN')
    user_refresh_token = os.getenv('TWITCH_USER_REFRESH_TOKEN')

    if not all([client_id, client_secret, bot_id, user_token, user_refresh_token]):
        raise ValueError("One or more environment variables are missing")

    return TwitchIdentityData(
        client_id=client_id,
        client_secret=client_secret,
        bot_id=bot_id,
        user_token=user_token,
        user_refresh_token=user_refresh_token
    )

class TwitchCallbacks:
    def __init__(self):
        pass
    async def on_self_message(self, message, bot: 'ButtsBot'):
        print("message received in my chat", message)
    async def on_foreign_message(self, message, bot: 'ButtsBot'):
        print("message received in a different chat", message)
    async def on_ready(self, bot: 'ButtsBot'):
        print("Bot is online!")
    
class ButtsBot(commands.Bot):
    def __init__(self, identity_data:TwitchIdentityData, callbacks: TwitchCallbacks, *args, **kwargs):
        self.identity_data = identity_data
        self.callbacks = callbacks
        self.subscriptions = {}
        super().__init__(*args, **kwargs, client_id=identity_data.client_id, client_secret=identity_data.client_secret, bot_id=identity_data.bot_id, prefix='!')

    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f'Bot is online!')
        await self.add_token(self.identity_data.user_token, self.identity_data.user_refresh_token)
        await self.callbacks.on_ready(self)
        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=self.identity_data.bot_id, # '702609083',
            user_id=self.identity_data.bot_id,
        )
        sub = await self.subscribe_websocket(payload=subscription, as_bot=True,token_for=self.identity_data.bot_id)

    async def subscribe_to_chat(self, broadcaster_id: str):
        if broadcaster_id in self.subscriptions:
            print("Already subscribed to chat messages for broadcaster", broadcaster_id)
            return False
        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=broadcaster_id,
            user_id=self.identity_data.bot_id,
        )
        sub = await self.subscribe_websocket(payload=subscription, as_bot=True,token_for=self.identity_data.bot_id)
        if sub is None:
            print("Already subscribed to chat messages for broadcaster", broadcaster_id)
            return False
        self.subscriptions[broadcaster_id] = sub['data'][0]['id']
        print("Subscribed to chat messages for broadcaster", broadcaster_id, 'with id', sub['data'][0]['id'])
        return True
    async def unsubscribe_from_chat(self, broadcaster_id: str) -> bool:
        if broadcaster_id not in self.subscriptions:
            print("Not subscribed to chat messages for broadcaster", broadcaster_id)
            return False
        sub_id = self.subscriptions[broadcaster_id]
        await self.delete_eventsub_subscription(sub_id, token_for=self.identity_data.bot_id)
        print("Unsubscribed from chat messages for broadcaster", broadcaster_id)
        return True

    async def event_message(self, message):
        'Runs every time a message is sent in chat.'
        if (message.chatter.id == self.identity_data.bot_id):
            print("Ignoring my own message", message)
            return
        if (message.broadcaster.id == self.identity_data.bot_id):
            # Chat message in my own chat
            await self.callbacks.on_self_message(message, self)
        else:
            # Chat message in a different chat
            await self.callbacks.on_foreign_message(message, self)

        
        # await self.get_context(message).channel.send_message(sender=BOT_ID, token_for=BOT_ID, message="HELLO " + message.chatter.name    + ", " + message.text)
        # make sure the bot ignores itself and the streamer
        
        # await message.channel.send(message.content)
        

class Twitch:
    def __init__(self, identity: TwitchIdentityData, callbacks: TwitchCallbacks):
        self.identity = identity
        self.callbacks = callbacks
        self.bot = ButtsBot(identity, callbacks)
    async def start(self):
        await self.bot.start()