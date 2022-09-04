import asyncio
import datetime
import logging
import os

import discord

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from bungie_api_wrapper.manifest import Manifest
from bungie_api_wrapper.async_main import *

# Importing commands view
from discord_bot.bot_ui import *

# Importing commands embeds
from discord_bot.embeds import BungieClanEmbed, LookingForGroupEmbed

logger = logging.getLogger('discord_bot')
load_dotenv


class GuardianCog(commands.GroupCog, name='guardian'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
        self.url = 'https://cdn.discordapp.com/icons/585134417568202836/a_d6a73cfaf80df5157ddf2e889c49ba73.gif?size=1024'
        
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
                self.characters_history = await get_character_history(name, code, 3)
                
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
            
            # check if user is in clan server, then fetch his avatar url
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
                embed = discord.Embed(description=f'{discord_user.mention}',
                                      timestamp=datetime.datetime.now())
            else:
                embed = discord.Embed(description=f'{username}',
                                      timestamp=datetime.datetime.now())
                
            for character, value in decoded_data.items():
                in_game_time = int(value['minutesPlayedTotal']) / 60
                last_time_login = value['dateLastPlayed'].replace("T", " ").replace("Z", "")
                if character == 'Warlock':
                    char_emoji = '<:warlock:1001823857818218497>'
                elif character == 'Hunter':
                    char_emoji = '<:hunter:1001823855431651340>'
                elif character == 'Titan':
                    char_emoji = '<:titan:1001823856526368769>'
                embed.add_field(
                    name=f'{char_emoji} **{character}**',
                    value=f'Race: **{value["raceName"]}** \n \
                            Light: **{value["light"]}** \n \
                            Last login: **{last_time_login}** \n \
                            In-game time: **{int(in_game_time)} hours**'
                )

            embed.set_author(name=username)
            embed.set_footer(text='ZEN • Commander Zavala @2022', icon_url=self.url)
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
    async def clan_info(self, interaction: discord.Interaction, group_id: str = None):
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


class LookingForGroupCommands(commands.GroupCog, name='lfg'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
    
    @app_commands.checks.has_role('Clan Members')
    @app_commands.command(name='pve', description='Create PvE lfg event.')
    async def pve_event(self, interaction: discord.Interaction, name: str,
                        description: str, slots: int = 3):
        lfg_event = LookingForGroupEmbed()
        members = []
        now = datetime.datetime.now()
        date_now = now.strftime("%d-%m-%Y %H:%M:%S")
        guild = self.bot.get_guild(int(os.getenv('GUILD_ID')))
        pve_role = guild.get_role(int(os.getenv('PVE_ROLE_ID')))
        
        try: 
            lfg_event = lfg_event.lfg_embed(
                name=name,
                description=description,
                event_type='pve',
                slots=slots,
                members=members,
                author=interaction.user,
                interaction=interaction,
                date=date_now
            )
            view = LFGView(
            name=name,
            description=description,
            event_type='pve',
            slots=slots,
            members=members,
            author=interaction.user,
            interaction=interaction,
            date=date_now
            )
            await interaction.response.send_message(content=pve_role.mention,
                                                    embed=lfg_event, view=view)
                                                    
        except Exception as e:
            await interaction.response.send_message(content=f'Error occurred!', ephemeral=True)
            logger.error(e)
    
    @app_commands.checks.has_role('Clan Members')
    @app_commands.command(name='pvp', description='Create PvP lfg event.')
    async def pvp_event(self, interaction: discord.Interaction, name: str,
                        description: str, slots: int = 3):
        lfg_event = LookingForGroupEmbed()
        members = []
        now = datetime.datetime.now()
        date_now = now.strftime("%d-%m-%Y %H:%M:%S")
        guild = self.bot.get_guild(int(os.getenv('GUILD_ID')))
        pvp_role = guild.get_role(int(os.getenv('PVP_ROLE_ID')))
        try:
            lfg_event = lfg_event.lfg_embed(
                name=name,
                description=description,
                event_type='pvp',
                slots=slots,
                members=members,
                author=interaction.user,
                interaction=interaction,
                date=date_now
            )
            view = LFGView(
            name=name,
            description=description,
            event_type='pvp',
            slots=slots,
            members=members,
            author=interaction.user,
            interaction=interaction,
            date=date_now
            )
            await interaction.response.send_message(content=pvp_role.mention,
                                                    embed=lfg_event, view=view)
                                                    
        except Exception as e:
            await interaction.response.send_message(content=f'Error occurred!', ephemeral=True)
            logger.error(e)
    
    @app_commands.checks.has_role('Clan Members')
    @app_commands.command(name='raid', description='Create Raid lfg event.')
    async def raid_event(self, interaction: discord.Interaction, name: str,
                        description: str):
        lfg_event = LookingForGroupEmbed()
        members = []
        slots = 6
        now = datetime.datetime.now()
        date_now = now.strftime("%d-%m-%Y %H:%M:%S")
        guild = self.bot.get_guild(int(os.getenv('GUILD_ID')))
        raid_role = guild.get_role(int(os.getenv('PVE_ROLE_ID')))
        try:
            lfg_event = lfg_event.lfg_embed(
                name=name,
                description=description,
                event_type='raid',
                slots=slots,
                members=members,
                author=interaction.user,
                interaction=interaction,
                date=date_now
            )
            view = LFGView(
            name=name,
            description=description,
            event_type='raid',
            slots=slots,
            members=members,
            author=interaction.user,
            interaction=interaction,
            date=date_now
            )
            await interaction.response.send_message(content=raid_role.mention,
                                                    embed=lfg_event, view=view)
                                                    
        except Exception as e:
            await interaction.response.send_message(content=f'Error occurred!', ephemeral=True)
            logger.error(e)

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
    
    @app_commands.checks.has_role('Founding Fathers')
    @app_commands.command(name='purge', description='Deletes the selected number of messages')
    async def purge(self, interaction: discord.Interaction, amount: int = 5):
        purge_ch = self.bot.get_channel(int(interaction.channel.id))
        await interaction.response.defer()
        async for message in purge_ch.history(limit=amount):
            await asyncio.sleep(1)
            await message.delete()
        await interaction.followup.send(f'Removed {amount} messages!', ephemeral=True)
    
        
async def setup(bot: commands.Bot) -> None:
    commands_list = [ClanCog(bot), GuardianCog(bot), UtilityCommands(bot),
                     LookingForGroupCommands(bot)] 
    for command in commands_list:
        await bot.add_cog(command, guild=discord.Object(id=int(os.getenv('GUILD_ID'))))
