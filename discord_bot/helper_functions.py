import discord
import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

async def purge_checkpoint_channel(bot: discord.Client, amount=5):
    checkpoint_channel = bot.get_channel(int(os.getenv('CHECKPOINTS_CHANNEL_ID')))
    async for message in checkpoint_channel.history(limit=amount):
        if message.content == '[Original Message Deleted]':
            await asyncio.sleep(1)
            await message.delete()
