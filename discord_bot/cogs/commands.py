import discord
import asyncio
import datetime
import logging

from discord import app_commands
from discord.ext import commands

from bungie_api_wrapper.manifest import Manifest
from bungie_api_wrapper.async_main import get_characters

# Importing commands view
from discord_bot.bot_ui import CheckModal, SelectCharacterView

logger = logging.getLogger('discord_bot')


class GuardianCog(commands.GroupCog, name='guardian'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
        
    @app_commands.command(name='check', description='Check Destiny 2 characters loadout')
    async def guardian_check(self, interaction: discord.Interaction,
                             username: str = None):
        if username is None:
            await interaction.response.send_modal(CheckModal())
            logger.info(f'{interaction.user.display_name} used modal guardian check command.')
        else:
            await interaction.response.defer()
            username = str(username)
            name = username.split('#')[0]
            code = int(username.split('#')[1])
            man = Manifest()
            
            characters_data = await get_characters(name, code, 3)
            decoded_data = man.decode_characters_from_manifest(characters_data)
            class_view = SelectCharacterView(decoded_data, str(username)) 
            
            # check if user is in clan server then fetch his avatar url
            checked_user = discord.utils.get(interaction.guild.members, display_name=username)
            if checked_user:
                user = interaction.guild.get_member(checked_user.id)
                if user.display_avatar:
                    user_icon = user.display_avatar
                else:
                    user_icon = user.default_avatar
                    
            embed = discord.Embed()
            
            for character, value in decoded_data.items():
                in_game_time = int(value['minutesPlayedTotal']) / 60
                last_time_login = value['dateLastPlayed'].replace("T", " ").replace("Z", "")
                embed.add_field(
                    name=f':lock: **{character}**',
                    value=f'Race: **{value["raceName"]}** \n \
                            Light: **{value["light"]}** \n \
                            Last login: **{last_time_login}** \n \
                            In-game time: **{int(in_game_time)} hours**'
                )

            #embed.set_author(name=username, icon_url=user_icon)
            await interaction.followup.send(embed=embed, view=class_view)
            logger.info(f'{interaction.user.display_name} used guardian check command.')
        

class ClanCog(commands.GroupCog, name='clan'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
    
    @app_commands.command(name='members', description='Display Destiny 2 clan members.')
    async def clan_members(self, interaction: discord.Interaction):
        pass
    
    @app_commands.command(name='admins', description='Display Destiny 2 clan admins.')
    async def clan_admins(self, interaction: discord.Interaction):
        pass
    
    @app_commands.command(name='leaderboard', description='Display Destiny 2 clan leaderboard.')
    async def clan_leaderboard(self, interaction: discord.Interaction):
        pass
    
    @app_commands.command(name='info', description='Display Destiny 2 clan informations.')
    async def clan_info(self, interaction: discord.Interaction):
        pass
        

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
    commands_list = [ClanCog(bot), GuardianCog(bot), UtilityCommands(bot)] 
    for command in commands_list:
        await bot.add_cog(command, guild=discord.Object(id=760629187932454935))
