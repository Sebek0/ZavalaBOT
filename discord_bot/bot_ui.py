from time import time
import discord
import logging

from discord_bot.embeds import ClassEmbed
from dotenv import load_dotenv
from typing import Any
from bungie_api_wrapper.async_main import get_characters
from bungie_api_wrapper.manifest import Manifest

load_dotenv()

logger = logging.getLogger('discord_bot')


class DeleteMessageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=3000)
        
    @discord.ui.button(label='Delete', custom_id='delete',
                       style=discord.ButtonStyle.danger)
    async def delete_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button):
        await interaction.message.delete()
        logger.info(f'{interaction.user.display_name} deleted {interaction.message.content}')
 
 
class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label='Delete',
            custom_id='delete',
            style=discord.ButtonStyle.gray
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        logger.info(f'{interaction.user.display_name} deleted {interaction.message.content}')


class ActivityHistoryButton(discord.ui.Button):
    def __init__(self, character_history):
        super().__init__(
            label='History',
            custom_id='activity_history',
            style=discord.ButtonStyle.gray
        )
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content='dziala')
        
        
class WarlockButton(discord.ui.Button):
    def __init__(self, decoded_data, user_name):
        super().__init__(
            label='Warlock',
            custom_id='warlock',
            style=discord.ButtonStyle.green
        )
        self.warlock_embed = ClassEmbed(decoded_data)
        self.user_name = user_name
        self.decoded_data = decoded_data
        self.user_name = user_name
        
    async def callback(self, interaction: discord.Interaction):
        select_char_view = SelectCharacterView(self.decoded_data, self.user_name)
        warlock_embed = await self.warlock_embed.embed('Warlock', 0x008f11,
                                                       self.user_name, 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/b3e79364-9b2c-4b75-8a81-7b99a0eb3b05/dblevlj-08ca9cdd-7036-47ae-ac22-5be96691129e.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2IzZTc5MzY0LTliMmMtNGI3NS04YTgxLTdiOTlhMGViM2IwNVwvZGJsZXZsai0wOGNhOWNkZC03MDM2LTQ3YWUtYWMyMi01YmU5NjY5MTEyOWUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.YrfDlGCFex9PB5fra4EGrp1I8LSvODkMvVHGW0WqqaM')
        await interaction.response.edit_message(embed=warlock_embed, view=select_char_view)
        logger.info(f'{interaction.user.display_name} interacted with {self.label}.')
        

class TitanButton(discord.ui.Button):
    def __init__(self, decoded_data, user_name):
        super().__init__(
            label='Titan',
            custom_id='titan',
            style=discord.ButtonStyle.red
        )
        self.titan_embed = ClassEmbed(decoded_data)
        self.user_name = user_name
        self.decoded_data = decoded_data
        self.user_name = user_name
    
    async def callback(self, interaction: discord.Interaction):
        select_char_view = SelectCharacterView(self.decoded_data, self.user_name)
        titan_embed = await self.titan_embed.embed('Titan', 0xc80404,
                                                   self.user_name, 'https://bit.ly/3llqjRv')
        await interaction.response.edit_message(embed=titan_embed, view=select_char_view)
        logger.info(f'{interaction.user.display_name} interacted with {self.label}.')


class HunterButton(discord.ui.Button):
    def __init__(self, decoded_data, user_name):
        super().__init__(
            label='Hunter',
            custom_id='hunter',
            style=discord.ButtonStyle.blurple
        )
        self.hunter_embed = ClassEmbed(decoded_data)
        self.user_name = user_name
        self.decoded_data = decoded_data
        self.user_name = user_name
        
    async def callback(self, interaction: discord.Interaction):
        select_char_view = SelectCharacterView(self.decoded_data, self.user_name)
        select_char_view.add_item(ActivityHistoryButton(self.user_name))
        hunter_embed = await self.hunter_embed.embed('Hunter', 0x0d0490,
                                                     self.user_name, 'https://bit.ly/3llqjRv')
        await interaction.response.edit_message(embed=hunter_embed, view=select_char_view)
        logger.info(f'{interaction.user.display_name} interacted with {self.label}.')


class ClanLeaderboardPVPButton(discord.ui.Button):
    def __init__(self, label, custom_id, style):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style
        )
        
    async def callback(self, interaction: discord.Interaction):
        if self.custom_id == 'cl_pvp':
            pvp_leaderboard_view = ClanLeaderboardPVP()
            await interaction.response.edit_message(content='PVP Leaderboard TEST',
                                                view=pvp_leaderboard_view)
        elif self.custom_id == 'cl_too':
            await interaction.response.edit_message(content='Trials', view=None)
        elif self.custom_id == 'cl_ib':
            await interaction.response.edit_message(content='Iron Banner', view=None)
        elif self.custom_id == 'cl_qp':
            await interaction.response.edit_message(content='Quickplay', view=None)
        elif self.custom_id == 'cl_comp':
            await interaction.response.edit_message(content='Survival', view=None) 
        

class ClanLeaderboardPVEButton(discord.ui.Button):
    def __init__(self, label, custom_id, style):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style
        )
    
    async def callback(self, interaction: discord.Interaction):
        if self.custom_id == 'cl_pve':
            pve_leaderboard_view = ClanLeaderboardPVE()
            await interaction.response.edit_message(content='PVE Leaderboard TEST',
                                                    view=pve_leaderboard_view)


class SelectClanLeaderboardType(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        leaderboard_types = {
            'pvp': ClanLeaderboardPVPButton(label='PvP', custom_id='cl_pvp',
                                            style=discord.ButtonStyle.red),
            'pve': ClanLeaderboardPVEButton(label='PvE', custom_id='cl_pve',
                                            style=discord.ButtonStyle.blurple)
        }
        
        for leaderboard_type in leaderboard_types.keys():
            self.add_item(leaderboard_types[leaderboard_type])
            
    async def on_error(self, error: Exception, interaction: discord.Interaction,
                       item: discord.ui.Item[Any]):
        await interaction.response.send_message(error, ephemeral=True)
        await interaction.message.delete(delay=3)
        return await super().on_error(error, item, interaction)
    
    async def on_timeout(self):
        return await super().on_timeout()


class ClanLeaderboardPVP(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        pvp_leaderboards = {
            'too': ClanLeaderboardPVPButton(label='Trials of Osiris', custom_id='cl_too',
                                            style=discord.ButtonStyle.gray),
            'ib': ClanLeaderboardPVPButton(label='Iron banner', custom_id='cl_ib',
                                           style=discord.ButtonStyle.gray),
            'qp': ClanLeaderboardPVPButton(label='Quickplay', custom_id='cl_qp',
                                           style=discord.ButtonStyle.gray),
            'comp': ClanLeaderboardPVPButton(label='Competitive', custom_id='cl_comp',
                                             style=discord.ButtonStyle.gray)
        }
        
        for pvp in pvp_leaderboards.keys():
            self.add_item(pvp_leaderboards[pvp])
    
    async def on_error(self, error: Exception, interaction: discord.Interaction,
                       item: discord.ui.Item[Any]):
        await interaction.response.send_message(error, ephemeral=True)
        await interaction.message.delete(delay=3)
        return await super().on_error(error, item, interaction)
    
    async def on_timeout(self):
        return await super().on_timeout()


class ClanLeaderboardPVE(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        pve_leaderboard = {
            'strike': ClanLeaderboardPVEButton(label='Strikes', custom_id='cl_strike',
                                               style=discord.ButtonStyle.gray),
            'raid': ClanLeaderboardPVEButton(label='Raids', custom_id='cl_raid',
                                             style=discord.ButtonStyle.gray),
            'gambit': ClanLeaderboardPVEButton(label='Gambit', custom_id='cl_gambit',
                                               style=discord.ButtonStyle.gray)
        }
        
        for pve in pve_leaderboard.keys():
            self.add_item(pve_leaderboard[pve])
    
    async def on_error(self, error: Exception, interaction: discord.Interaction,
                       item: discord.ui.Item[Any]):
        await interaction.response.send_message(error, ephemeral=True)
        await interaction.message.delete(delay=3)
        return await super().on_error(error, item, interaction)
    
    async def on_timeout(self):
        return await super().on_timeout()


class SelectCharacterView(discord.ui.View):
    def __init__(self, decoded_data, user_name):
        super().__init__(timeout=60)
        characters = {
            'Titan': TitanButton(decoded_data, user_name),
            'Warlock': WarlockButton(decoded_data, user_name),
            'Hunter': HunterButton(decoded_data, user_name)
        }

        self.add_item(DeleteButton())
        for character in decoded_data.keys():
            if character in characters.keys():
                self.add_item(characters[character])

    async def on_error(self, interaction: discord.Interaction, error: Exception,
                       item: discord.ui.Item[Any]) -> None:
        logger.error(f'{interaction} - {error} - {item}')
        await interaction.response.send_message("Could not fetch character equipment!",
                                         ephemeral=True)
        return await super().on_error(interaction, error, item)
    
    async def on_timeout(self):
        return await super().on_timeout()
    
  
class CheckModal(discord.ui.Modal, title="Commander Zavala"):
    answer = discord.ui.TextInput(label='User name and code',
                                  style=discord.TextStyle.short, required=True,
                                  placeholder='Example: Guardian1623#6521',
                                  max_length=50)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        answer = str(self.answer)
        name = answer.split('#')[0]
        code = int(answer.split('#')[1])
        man = Manifest()
        
        characters_data = await get_characters(name, code, 3)
        decoded_data = man.decode_characters_from_manifest(characters_data)
        class_view = SelectCharacterView(decoded_data, str(answer)) 
        
        # check if user is in clan server then fetch his avatar url
        checked_user = discord.utils.get(interaction.guild.members, display_name=self.answer)
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

        #embed.set_author(name=self.answer, icon_url=user_icon)
        await interaction.followup.send(embed=embed, view=class_view)
        self.stop()
        
        



