from twitchio.ext import commands
from twitchbot import ButtsBot
class MessageHandler:
    def __init__(self):
        pass
    async def reply_in_chat(self, reply_to, text: str, bot: ButtsBot):
        await bot.get_context(reply_to).channel.send_message(sender=bot.identity_data.bot_id, token_for=bot.identity_data.bot_id, message=text)
    def get_message_text(self, message):
        return message.text
    def get_message_sender_id(self, message):
        return message.chatter.id
    def get_message_broadcaster_id(self, message):
        return message.broadcaster.id
    def get_message_sender_name(self, message):
        return message.chatter.name