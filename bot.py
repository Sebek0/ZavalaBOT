# client_bot.py
import os
import discord
import sys
import json

from discord.ext import commands
from discord import Embed
from dotenv import load_dotenv
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        
        super().__init__(command_prefix='.', intents=intents)
    
    async def on_ready(self) -> None:
        await self.wait_until_ready()
        await bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f'We have logged in as {self.user}')
        print(f'{self.user} is ready to use!')
        
    async def setup_hook(self) -> None:
        await self.load_extension('discord_bot.cogs.commands')
        await self.load_extension('discord_bot.cogs.listeners')
              
bot = Bot()

def main():
    bot.run(discord_token)

if __name__ == '__main__':
    main()
    
    