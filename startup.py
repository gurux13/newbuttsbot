from sqlalchemy import Select
from db import db_session
from models import ChatSubscription
from sqlalchemy.ext.asyncio import AsyncSession
from twitchbot import ButtsBot
class StartupHandler:
    def __init__(self):
        pass

    @db_session
    async def on_bot_ready(self, bot: ButtsBot, session: AsyncSession):
        
        result = await session.execute(Select(ChatSubscription).where(ChatSubscription.is_subscribed == True))
        for subscription in result.scalars():
            await bot.subscribe_to_chat(subscription.broadcaster_id)