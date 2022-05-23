import discord
import asyncio
import datetime
import logging

from discord import app_commands
from discord.ext import commands

# Importing commands view
from discord_bot.bot_ui import CheckModal

logger = logging.getLogger('discord_bot')


class EventCog(commands.GroupCog, name="event"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.x = list()
        super().__init__()  
    
    @app_commands.command(name="add", description='Add custom event')
    async def add_custom_event(self, interaction: discord.Interaction, event: str) -> None:
        """ /event add 'event' """
        self.x.append(str(event))
        await interaction.response.send_message(f'adding... {event}', ephemeral=True)
    
    @app_commands.command(name="remove", description='Remove custom event')
    async def remove_custom_event(self, interaction: discord.Interaction, event: str) -> None:
        """ /event remove 'event' """
        self.x.remove(str(event))
        await interaction.response.send_message(f'removing... {event}', ephemeral=True)
    
    @app_commands.command(name='create', description='Create Destiny2 event')   
    async def create_custom_event(self, interaction: discord.Interaction) -> None:
        """ /event create """
        pass
        #view = View()
        #await interaction.response.send_message('Creating custom event...', view=view, ephemeral=True)
    
    @app_commands.command(name='list', description='Custom events list')
    async def event_list(self, interaction: discord.Interaction) -> None:
        if len(self.x) != 0:
           await interaction.response.send_message(f"{', '.join(self.x)}", ephemeral=True) 
        else:
           await interaction.response.send_message(f'Event list is empty!', ephemeral=True)


class GuardianCog(commands.GroupCog, name='guardian'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
        
    @app_commands.command(name='check', description='Check Destiny 2 characters loadout')
    async def guardian_check(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CheckModal())
        logger.info(f'{interaction.user.display_name} used guardian check command.')
        

class UtilityCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
        
    @app_commands.command(name='countdown', description='Countdown timer')
    async def countdown(self, interaction: discord.Interaction, time: int, update: int):
        await interaction.response.send_message('Starting countdown!', ephemeral=True)
        timer = time * 60
        minutes = 0
        message = None
        while timer > 0:
            if message is None:
                minutes = str(datetime.timedelta(seconds=timer))
                timer -= update
                message = await interaction.channel.send(content=f'Time left: `{minutes}`')
                await asyncio.sleep(update)
            elif message is not None and interaction.channel.last_message_id != message.id:
                await message.delete()
                minutes = str(datetime.timedelta(seconds=timer))
                timer -= update 
                message = await interaction.channel.send(content=f'Time left: `{minutes}`')
                await asyncio.sleep(update)
            elif message is not None and interaction.channel.last_message_id == message.id:
                minutes = str(datetime.timedelta(seconds=timer))
                timer -= update
                await message.edit(content=f'Time left: `{minutes}`')
                await asyncio.sleep(update)
        if timer <= 0:
            await message.delete()
            await interaction.channel.send(interaction.user.mention)
                    
async def setup(bot: commands.Bot) -> None:
    commands_list = [EventCog(bot), GuardianCog(bot), UtilityCommands(bot)] 
    for command in commands_list:
        await bot.add_cog(command, guild=discord.Object(id=760629187932454935))
