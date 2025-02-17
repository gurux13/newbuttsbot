from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Chatter(Base):
    __tablename__ = 'chatters'

    twitch_id = Column(String, nullable=False, primary_key=True)
    ignore = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class ChatSubscription(Base):
    __tablename__ = 'chat_subscriptions'

    broadcaster_id = Column(String, nullable=False, primary_key=True)
    is_subscribed = Column(Boolean, nullable=False)
    butt_word = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    rate = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
def get_default_subscription(broadcaster_id: str):
    return ChatSubscription(broadcaster_id = broadcaster_id, is_subscribed=True, frequency=30, rate=10, butt_word='butt')