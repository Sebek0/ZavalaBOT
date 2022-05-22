import os
import aiohttp
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from custom_logging import CustomFormatter

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        
        formatter = CustomFormatter()
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('discord_bot')
        self.logger.addHandler(stream_handler)
        
        self.logger.setLevel(logging.INFO)
        
        super().__init__(command_prefix='.', intents=intents)
    
    async def on_ready(self) -> None:
        await self.wait_until_ready()
        try:
            await bot.tree.sync(guild=discord.Object(id=guild_id))
            self.logger.info('Synced application commands with Discord.')
        except aiohttp.ClientResponseError:
            self.logger.error('Syncing the commands failed.')
        except discord.Forbidden:
            self.logger.error('The client does not have the applications.commands'
                              'scope in the guild.')
            
        self.logger.info(f'Bot logged in as {self.user}')
        self.logger.info(f'{self.user} is ready to use.')
        
    async def setup_hook(self) -> None:
        try:
            await self.load_extension('discord_bot.cogs.commands')
            await self.load_extension('discord_bot.cogs.listeners')
        except discord.DiscordException as discord_error:
            self.logger.error(discord_error)
              
bot = Bot()

def main():
    bot.run(discord_token)

if __name__ == '__main__':
    main()
    
    