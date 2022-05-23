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
        
    @discord.ui.button(label='Delete check', custom_id='delete',
                       style=discord.ButtonStyle.danger)
    async def delete_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button):
        await interaction.message.delete()
        logger.info(f'{interaction.user.display_name} deleted {interaction.message.content}')
 
 
class WarlockButton(discord.ui.Button):
    def __init__(self, decoded_data, user_name):
        super().__init__(
            label='Warlock',
            custom_id='warlock',
            style=discord.ButtonStyle.green
        )
        self.warlock_embed = ClassEmbed(decoded_data)
        self.user_name = user_name
        
    async def callback(self, interaction: discord.Interaction):
        delete_view = DeleteMessageView()
        warlock_embed = await self.warlock_embed.embed('Warlock', 0x008f11,
                                                       self.user_name, 'https://bit.ly/3llqjRv')
        await interaction.response.edit_message(embed=warlock_embed, view=delete_view)
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
    
    async def callback(self, interaction: discord.Interaction):
        delete_view = DeleteMessageView()
        titan_embed = await self.titan_embed.embed('Titan', 0xc80404,
                                                   self.user_name, 'https://bit.ly/3llqjRv')
        await interaction.response.edit_message(embed=titan_embed, view=delete_view)
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
        
    async def callback(self, interaction: discord.Interaction):
        delete_view = DeleteMessageView()
        hunter_embed = await self.hunter_embed.embed('Hunter', 0x0d0490,
                                                     self.user_name, 'https://bit.ly/3llqjRv')
        await interaction.response.edit_message(embed=hunter_embed, view=delete_view)
        logger.info(f'{interaction.user.display_name} interacted with {self.label}.')
        
class SelectCharacterView(discord.ui.View):
    def __init__(self, decoded_data, user_name):
        super().__init__(timeout=3000)
        characters = {
            'Titan': TitanButton(decoded_data, user_name),
            'Warlock': WarlockButton(decoded_data, user_name),
            'Hunter': HunterButton(decoded_data, user_name)
        }

        for character in decoded_data.keys():
            if character in characters.keys():
                self.add_item(characters[character])

    async def on_error(self, error: Exception, interaction: discord.Interaction,
                       item: discord.ui.Item[Any]):
        await item.response.send_message("Could not fetch character equipment!",
                                         ephemeral=True)
        await item.message.delete(delay=3)
        return await super().on_error(error, item, interaction)
    
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