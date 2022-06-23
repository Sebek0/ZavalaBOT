import discord
import asyncio
import datetime
import logging
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from bungie_api_wrapper.manifest import Manifest
from bungie_api_wrapper.async_main import *


# Importing commands view
from discord_bot.bot_ui import *

# Importing commands embeds
from discord_bot.embeds import BungieClanEmbed

logger = logging.getLogger('discord_bot')
load_dotenv


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
            command_author_id = interaction.user.id
            username = str(username)
            name = username.split('#')[0]
            code = int(username.split('#')[1])
            man = Manifest()
                      
            self.characters_data = {}
            self.characters_history = {}
            
            # this thing makes it possible to gather multiple request in the same
            # time, doing that makes overall time for command to execute is halfed.
            async def fetch_characters(self):
                self.characters_data = await get_characters(name, code, 3)
            async def fetch_history(self):
                self.characters_history = await get_character_history_test(name, code, 3)
                
            await asyncio.gather(
                fetch_characters(self),
                fetch_history(self)
            )
            
            # old way to make requests, it works but very slowly.
            
            #characters_data = await get_characters(name, code, 3)
            #characters_history = await get_character_history_test(name, code, 3)
            
            decoded_data = man.decode_characters_from_manifest(self.characters_data)
            class_view = SelectCharacterView(decoded_data, str(username),
                                             self.characters_history, command_author_id)
            
            # check if user is in clan server then fetch his avatar url
            checked_user = discord.utils.get(interaction.guild.members,
                                             display_name=username)
            if checked_user:
                user = interaction.guild.get_member(checked_user.id)
                if user.display_avatar:
                    user_icon = user.display_avatar
                else:
                    user_icon = user.default_avatar
            
            discord_user = discord.utils.get(interaction.guild.members,
                                             display_name=username)
            if discord_user is not None:
                embed = discord.Embed(description=f'{discord_user.mention}')
            else:
                embed = discord.Embed(description=f'{username}')
                
            for character, value in decoded_data.items():
                in_game_time = int(value['minutesPlayedTotal']) / 60
                last_time_login = value['dateLastPlayed'].replace("T", " ").replace("Z", "")
                embed.add_field(
                    name=f'<:tricorn:983458457069969429> **{character}**',
                    value=f'Race: **{value["raceName"]}** \n \
                            Light: **{value["light"]}** \n \
                            Last login: **{last_time_login}** \n \
                            In-game time: **{int(in_game_time)} hours**'
                )

            embed.set_author(name=username, icon_url=user_icon)
            await interaction.followup.send(embed=embed, view=class_view)
            logger.info(f'{interaction.user.display_name} used guardian check command.')
        

class ClanCog(commands.GroupCog, name='clan'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
    
    @app_commands.command(name='leaderboard', description='Display Destiny 2 clan leaderboard.')
    async def clan_leaderboard(self, interaction: discord.Interaction):
        leaderboard_type = SelectClanLeaderboardType()
        await interaction.response.defer()
        await interaction.followup.send(content='Test', view=leaderboard_type)
        
    @app_commands.command(name='info', description='Display Destiny 2 clan informations.')
    async def clan_info(self, interaction: discord.Interaction, group_id: int = None):
        await interaction.response.defer()
        delete_view = DeleteMessageView()
        if group_id is None:
            group_id = os.getenv('BUNGIE_GROUP_ID')
            clan_info = await get_clan_informations(group_id)
            clan_rewards = await get_destiny_clan_weekly_rewards(group_id)
            clan_embed = BungieClanEmbed()
            clan_embed = await clan_embed.info_embed(
                name=clan_info['name'],
                callsign=clan_info['callsign'],
                motto=clan_info['motto'],
                about=clan_info['about'],
                author_icon_url=self.bot.user.display_avatar,
                clan_icon_url=clan_info['clan_icon_url'],
                founder_name=clan_info['founder'],
                level_cap=clan_info['level_cap'],
                members_list=clan_info['members_list'],
                members_count=clan_info['members_count'],
                creation_date=clan_info['creation_date'],
                exp=clan_info['exp'],
                level=clan_info['level'],
                interaction=interaction,
                rewards=clan_rewards
            )
            await interaction.followup.send(embed=clan_embed, view=delete_view)
            logger.info(f'{interaction.user.display_name} used clan info command.')
        else:
            clan_info = await get_clan_informations(group_id)
            clan_embed = BungieClanEmbed()
            clan_embed = await clan_embed.info_embed(
                name=clan_info['name'],
                callsign=clan_info['callsign'],
                motto=clan_info['motto'],
                about=clan_info['about'],
                author_name=self.bot.user.display_name,
                author_icon_url=self.bot.user.display_avatar,
                clan_icon_url=clan_info['clan_icon_url'],
                founder_name=clan_info['founder'],
                level_cap=clan_info['level_cap'],
                members_list=clan_info['members_list'],
                members_count=clan_info['members_count'],
                creation_date=clan_info['creation_date'],
                exp=clan_info['exp'],
                level=clan_info['level']
            )
            await interaction.followup.send(embed=clan_embed, view=delete_view)
            logger.info(f'{interaction.user.display_name} used clan info command.')
        

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
        await bot.add_cog(command, guild=discord.Object(id=585134417568202836))
