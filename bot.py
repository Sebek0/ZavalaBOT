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

formatter = CustomFormatter()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger('discord_bot')
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()   
        super().__init__(command_prefix='.', intents=intents)
    
    async def on_ready(self) -> None:
        logger.debug(f'About to start {self.user}...')
        await self.wait_until_ready()
        try:
            await bot.tree.sync(guild=discord.Object(id=guild_id))
            logger.info('Synced application commands with Discord.')
        except aiohttp.ClientResponseError:
            logger.error('Syncing the commands failed.')
        except discord.Forbidden:
            logger.error('The client does not have the applications.commands'
                              'scope in the guild.')
            
        logger.info(f'Bot logged in as {self.user}')
        logger.info(f'{self.user} is ready to use.')
        
    async def setup_hook(self) -> None:
        logger.debug('About to start loading extenstions...')
        try:
            await self.load_extension('discord_bot.cogs.commands')
            await self.load_extension('discord_bot.cogs.listeners')
            logger.info('Loaded extensions.')
        except discord.DiscordException as discord_error:
            logger.error(f'{discord_error}')
              
bot = Bot()

def main():
    bot.run(discord_token)

if __name__ == '__main__':
    main()
    
    