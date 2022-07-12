import os
import logging

import aiohttp
import discord
import yaml

from discord.ext import commands
from dotenv import load_dotenv
from custom_logging import CustomFormatter
from bungie_api_wrapper.manifest import Manifest

load_dotenv()

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    print(config)

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
        if not config['development']:
            self.manifest = Manifest()
        super().__init__(command_prefix='.', intents=intents)
    
    async def on_ready(self) -> None:
        logger.debug('About to start {}...'.format(self.user))
        
        await self.wait_until_ready()
        try:
            await bot.tree.sync(guild=discord.Object(id=guild_id))
            logger.info('Synced application commands with Discord.')
        except aiohttp.ClientResponseError:
            logger.error('Syncing the commands failed.')
        except discord.Forbidden:
            logger.error('The client does not have the applications.commands'
                              'scope in the guild.')
        
        # Checking if Bungie API manifest is up to date with bot startup.
        if not config['development']:
            self.manifest.check_manifest()
            
        logger.info('Bot logged in as {}'.format(self.user))
        logger.info('{} is ready to use.'.format(self.user))
        
    async def setup_hook(self) -> None:
        logger.debug('About to start loading extenstions...')
        try:
            await self.load_extension('discord_bot.cogs.commands')
            await self.load_extension('discord_bot.cogs.listeners')
            logger.info('Loaded extensions.')
        except discord.DiscordException as discord_error:
            logger.error('{}'.format(discord_error))
              
bot = Bot()

def main():
    bot.run(discord_token)

if __name__ == '__main__':
    main()
    
    