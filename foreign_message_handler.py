from twitchio.ext import commands
from message_handler import MessageHandler
from db import db_session
from sqlalchemy.ext.asyncio import AsyncSession
from twitchbot import ButtsBot
from models import *
from buttify import Buttifier
import random
class ForeignMessageHandler(MessageHandler):
    def __init__(self):
        self.butts = Buttifier()
        pass

    @db_session
    async def on_message(self, message, bot: ButtsBot, session: AsyncSession):
        print("message received in foreign chat", message)
        text = self.get_message_text(message)
        if text.startswith("!"):
            return
        subscription_info:ChatSubscription = await session.get(ChatSubscription, self.get_message_broadcaster_id(message))
        if subscription_info is None:
            print("No subscription found for", self.get_message_broadcaster_id(message), 'wtf?')
            bot.unsubscribe_from_chat(self.get_message_broadcaster_id(message))
            return
        if not subscription_info.is_subscribed:
            print("Should not be subscribed to chat messages for broadcaster", self.get_message_broadcaster_id(message))
            bot.unsubscribe_from_chat(self.get_message_broadcaster_id(message))
            return
        
        if random.randint(1, subscription_info.frequency) != 1:
            print("Not the time to buttify")
            return

        chatter:Chatter = await session.get(Chatter, self.get_message_sender_id(message))
        if chatter and chatter.ignore:
            print("Ignoring message from", self.get_message_sender_id(message),'as requested')
            return
        
        text = message.text
        buttified = self.butts.replace_nth_syllable(text, subscription_info.rate, subscription_info.butt_word, self.get_message_emote_text(message))
        if buttified != text:
            await self.reply_in_chat(message, buttified, bot)
      