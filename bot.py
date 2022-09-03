import asyncio
import os
import logging

import aiohttp
import discord
import yaml

from discord.ext import commands, tasks
from dotenv import load_dotenv
from custom_logging import CustomFormatter
from bungie_api_wrapper.manifest import Manifest

load_dotenv()

# Will load configuration variables from yaml file to dictionary.
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

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
        allowed_mentions = discord.AllowedMentions.all()
        super().__init__(command_prefix='.', allowed_mentions=allowed_mentions,
                         intents=intents)
        
    async def setup_hook(self) -> None:
        logger.debug('About to start loading extenstions...')
        try:
            await self.load_extension('discord_bot.cogs.commands')
            if config['server_logging']:
                await self.load_extension('discord_bot.cogs.listeners')
            if not config['development']:
                self.bg_task = self.loop.create_task(self.check_bungie_manifest_version())
            logger.info('Loaded extensions.')
        except discord.DiscordException as discord_error:
            logger.error('{}'.format(discord_error))
    
    async def on_ready(self) -> None:
        logger.debug('About to start {}...'.format(self.user))
        
        try:
            await bot.tree.sync(guild=discord.Object(id=guild_id))
            logger.info('Synced application commands with Discord.')
        except aiohttp.ClientResponseError:
            logger.error('Syncing the commands failed.')
        except discord.Forbidden:
            logger.error('The client does not have the applications.commands'
                              'scope in the guild.')
            
        logger.info('Bot logged in as {}'.format(self.user))
        logger.info('{} is ready to use.'.format(self.user))
    
    # Check if Bungie API manifest is up to date with bot startup.   
    async def check_bungie_manifest_version(self):
        await self.wait_until_ready()
        while not self.is_closed():
            self.manifest.check_manifest()
            await asyncio.sleep(86400)
            
    
bot = Bot()

def main():
    bot.run(discord_token)

if __name__ == '__main__':
    main()
    
    