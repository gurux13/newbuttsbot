from twitchio.ext import commands
from message_handler import MessageHandler
from db import db_session
from sqlalchemy.ext.asyncio import AsyncSession
from twitchbot import ButtsBot
from models import *
class SelfMessageHandler(MessageHandler):
    def __init__(self):
        self.command_mapping = {
            "joinme": self.on_joinme,
            "leaveme": self.on_leaveme,
            "setword": self.on_setword,
            "setfrequency": self.on_setfrequency,
            "setbuttificationrate": self.on_setbuttificationrate,
            "ignoreme": self.on_ignoreme,
            "unignoreme": self.on_unignoreme
        }
    @db_session
    async def on_leaveme(self, message, bot: ButtsBot, session: AsyncSession):
        had_sub = await bot.unsubscribe_from_chat(self.get_message_sender_id(message))
        existing_sub = await session.get(ChatSubscription, self.get_message_sender_id(message))
        if existing_sub is None:
            print("No subscription found for", self.get_message_sender_id(message), 'wtf?')
        else:
            had_sub = had_sub or existing_sub.is_subscribed
            existing_sub.is_subscribed = False
        if had_sub:
            await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, I have left you. No more butt.", bot)
        else:
            await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, I was not even there. No butt for you.", bot)
            
    @db_session
    async def on_joinme(self, message, bot: ButtsBot, session: AsyncSession):
        subscribed = await bot.subscribe_to_chat(self.get_message_sender_id(message))
        existing_sub = await session.get(ChatSubscription, self.get_message_sender_id(message))
        if existing_sub is None:
            new_sub = get_default_subscription(self.get_message_sender_id(message))
            session.add(new_sub)
        else:
            existing_sub.is_subscribed = True
        message_text = f"@{self.get_message_sender_name(message)}," + ("I am now subscribed to your chat. Let there be butt." if subscribed else "I am already subscribed to your chat. Let there be butt.")
        await self.reply_in_chat(message, message_text, bot)
    
    @db_session
    async def on_setword(self, message, bot: ButtsBot, session: AsyncSession):
        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2:
            await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, please provide a word.", bot)
            return
        
        new_word = command_parts[1].strip()
        existing_sub = await session.get(ChatSubscription, self.get_message_sender_id(message))
        
        if existing_sub is None:
            new_sub = get_default_subscription(self.get_message_sender_id(message))
            new_sub.butt_word = new_word
            new_sub.is_subscribed = False
            sub = new_sub
            session.add(new_sub)
        else:
            existing_sub.butt_word = new_word
            sub = existing_sub
        
        await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, your butt word has been set to '{new_word}'.{'Note that I am not subscribed to your chat, !joinme to subscribe.' if not sub.is_subscribed else ''}", bot)
    
    @db_session
    async def on_setfrequency(self, message, bot: ButtsBot, session: AsyncSession):
        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2 or not command_parts[1].strip().isdigit():
            await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, please provide a valid frequency number.", bot)
            return
        
        new_frequency = int(command_parts[1].strip())
        existing_sub = await session.get(ChatSubscription, self.get_message_sender_id(message))
        
        if existing_sub is None:
            new_sub = get_default_subscription(self.get_message_sender_id(message))
            new_sub.frequency = new_frequency
            new_sub.is_subscribed = False
            sub = new_sub
            session.add(new_sub)
        else:
            existing_sub.frequency = new_frequency
            sub = existing_sub
        
        await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, your frequency has been set to '{new_frequency}'.{' Note that I am not subscribed to your chat, !joinme to subscribe.' if not sub.is_subscribed else ''}", bot)
    
    @db_session
    async def on_setbuttificationrate(self, message, bot: ButtsBot, session: AsyncSession):
        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2 or not command_parts[1].strip().isdigit():
            await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, please provide a valid rate number.", bot)
            return
        
        new_rate = int(command_parts[1].strip())
        existing_sub = await session.get(ChatSubscription, self.get_message_sender_id(message))
        
        if existing_sub is None:
            new_sub = get_default_subscription(self.get_message_sender_id(message))
            new_sub.rate = new_rate
            new_sub.is_subscribed = False
            sub = new_sub
            session.add(new_sub)
        else:
            existing_sub.rate = new_rate
            sub = existing_sub
        
        await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, your buttification rate has been set to '{new_rate}'.{' Note that I am not subscribed to your chat, !joinme to subscribe.' if not sub.is_subscribed else ''}", bot)
    
    @db_session
    async def on_ignoreme(self, message, bot: ButtsBot, session: AsyncSession):
        chatter = await session.get(Chatter, self.get_message_sender_id(message))
        if chatter is None:
            chatter = Chatter(twitch_id=self.get_message_sender_id(message), ignore=True)
            session.add(chatter)
        else:
            chatter.ignore = True
        await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, you will be ignored from now on. Sad butt.", bot)
    
    @db_session
    async def on_unignoreme(self, message, bot: ButtsBot, session: AsyncSession):
        chatter = await session.get(Chatter, self.get_message_sender_id(message))
        if chatter is None:
            chatter = Chatter(twitch_id=self.get_message_sender_id(message), ignore=False)
            session.add(chatter)
        else:
            chatter.ignore = False
        await self.reply_in_chat(message, f"@{self.get_message_sender_name(message)}, you will no longer be ignored. Happy butt.", bot)
    
    async def on_message(self, message, bot: commands.Bot):
        print("message received in my chat", message)
        text = message.text
        if text.startswith("!"):
            command = text[1:].split(" ")[0]
            if command in self.command_mapping:
                print("Command found", command)
                await self.command_mapping[command](message, bot)
            else:
                reply_text = f'Command {command} not found. Available commands: {", ".join(['!' + c for c in self.command_mapping.keys()])}'
                await self.reply_in_chat(message, reply_text, bot)
        