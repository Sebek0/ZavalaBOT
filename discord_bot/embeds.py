from unicodedata import name
import discord

from datetime import datetime
from discord.ext import commands


class ClassEmbed(discord.Embed):
    def __init__(self, decoded_data):
        super().__init__()
        self.decoded_data = decoded_data
        self.url = 'https://cdn.discordapp.com/icons/585134417568202836/a_d6a73cfaf80df5157ddf2e889c49ba73.gif?size=1024'
        
    async def embed(self, character_class_name, color, user_name, class_icon):
        d = self.decoded_data[str(character_class_name)]
        class_embed = discord.Embed(
            color=color,
            title=f'{character_class_name}',
            type='rich',
            timestamp=datetime.now(),
            description='Moblity: **{}** \n Resilience: **{}** \n Recovery: **{}** \n \
                Discipline: **{}** \n Intellect: **{}** \n Strength: **{}**' \
                .format(d['stats']['Mobility'], d['stats']['Resilience'],
                        d['stats']['Recovery'], d['stats']['Discipline'],
                        d['stats']['Intellect'], d['stats']['Strength'])
        )
        
        in_game_time = int(d['minutesPlayedTotal']) / 60
        last_time_login = d['dateLastPlayed'].replace("T", " ").replace("Z", "")
        class_embed.add_field(
            name='Class informations:',
            value='Race: **{}** \n Light: **{}** \n Last login: **{}** \n In-game time: **{} hours**' \
                .format(d['raceName'], d['light'], last_time_login, int(in_game_time)),
            inline=False
        )
        kinetic_perks = ''
        energy_perks = ''
        power_perks = ''
        
        for v in d['items']['Kinetic Weapons']['perks'].values():
            kinetic_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Energy Weapons']['perks'].values():
            energy_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Power Weapons']['perks'].values():
            power_perks += f'• __{v["name"]} __\n'
            
        class_embed.add_field(
            name='Items:',
            value='**Kinetic:** `{}` \n {} \n **Energy:** `{}` \n {} \n **Heavy:** `{}` \n {}' \
                .format(d['items']['Kinetic Weapons']['common_data']['item_name'],
                        kinetic_perks,
                        d['items']['Energy Weapons']['common_data']['item_name'],
                        energy_perks,
                        d['items']['Power Weapons']['common_data']['item_name'],
                        power_perks),
            inline=True
        )
        
        helmet_perks = ''
        gauntlets_perks = ''
        armor_perks = ''
        legs_perks = ''
        class_item_perks = ''
        
        for v in d['items']['Helmet']['perks'].values():
            helmet_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Gauntlets']['perks'].values():
            gauntlets_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Chest Armor']['perks'].values():
            armor_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Leg Armor']['perks'].values():
            legs_perks += f'• __{v["name"]} __\n'
        for v in d['items']['Class Armor']['perks'].values():
            class_item_perks += f'• __{v["name"]} __\n'
            
        class_embed.add_field(
            name='Armors:',
            value='**Helmet:** `{}` \n {} \n **Gauntlets:** `{}` \n {} \n **Armor:** `{}` \n {} \n **Legs:** `{}` \n {} \n **Class:** `{}` \n {}' \
                .format(d['items']['Helmet']['common_data']['item_name'],
                        helmet_perks,
                        d['items']['Gauntlets']['common_data']['item_name'],
                        gauntlets_perks,
                        d['items']['Chest Armor']['common_data']['item_name'],
                        armor_perks,
                        d['items']['Leg Armor']['common_data']['item_name'],
                        legs_perks,
                        d['items']['Class Armor']['common_data']['item_name'],
                        class_item_perks),
            inline=True
        )
        class_embed.set_thumbnail(url=f'https://www.bungie.net{d["emblemPath"]}')
        class_embed.set_author(name=user_name, icon_url=class_icon)
        class_embed.set_footer(text='ZEN • Commander Zavala @2022', icon_url=self.url)
        return class_embed


class MessageLogEmbed(discord.Embed):
    def __init__(self):
        self.url = 'https://cdn.discordapp.com/icons/585134417568202836/a_d6a73cfaf80df5157ddf2e889c49ba73.gif?size=1024'
        super().__init__()
    
    async def embed(self, event, user, message=None, before=None, after=None):
        if event == 'update':
            event_name = 'Update message'
            embed_color = 0xe67e22
        elif event == 'delete':
            event_name = 'Delete message'
            embed_color = 0xe74c3c
        elif event == 'new':
            event_name = 'New message'
            embed_color = 0x2ecc71
            
        message_embed = discord.Embed(
            color=embed_color,
            title=event_name,
            type='rich',
            timestamp=datetime.now()
        )
             
        if before == None:
            message_embed.add_field(
                name='Channel',
                value=f'{message.channel.name} (@{message.channel.id})',
                inline=False
            )
        elif message == None:
            message_embed.add_field(
                name='Channel',
                value=f'{before.channel.name} (@{before.channel.id})',
                inline=False
            )
        
        if event == 'update':
            message_embed.add_field(
                name='Content before',
                value=before.content,
                inline=True
            )
            message_embed.add_field(
                name='Content after',
                value=after.content
            )
        elif event == 'new' or 'delete':
            message_embed.add_field(
                name='Content',
                value=message.content
            )
        
        message_embed.set_thumbnail(url=user.display_avatar)
        message_embed.set_author(name=f'{user.display_name} [{user.name}#{user.discriminator}] (@{user.id})', icon_url=user.display_avatar)
        message_embed.set_footer(text='ZEN • Commander Zavala @2022', icon_url=self.url)
        return message_embed

class ChannelLogEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        
    async def embed(self, event, channel=None, before=None, after=None):
        if event == 'update':
            event_name = 'Update channel'
            embed_color = 0xe67e22
        elif event == 'delete':
            event_name = 'Delete channel'
            embed_color = 0xe74c3c
        elif event == 'new':
            event_name = 'New channel'
            embed_color = 0x2ecc71
            
        channel_embed = discord.Embed(
            color=embed_color,
            title=event_name,
            type='rich',
            timestamp=datetime.now()
        )
        
        if before == None:
            channel_embed.add_field(
                name='Category',
                value=f'{channel.category} (@{channel.category_id})',
                inline=False
            )
        elif channel == None:
            channel_embed.add_field(
                name='Category',
                value=f'{before.category} (@{before.category_id})',
                inline=False
            )           
        if event == 'update':
            channel_embed.add_field(
                name='Channel before',
                value=before.name,
                inline=True
            )
            channel_embed.add_field(
                name='Channel after',
                value=after.name,
                inline=True
            )
        elif event == 'new' or 'delete':
            channel_embed.add_field(
                name='Name',
                value=channel.name
            )
        
        channel_embed.set_footer(text='ZEN • Commander Zavala @2022', icon_url=self.url)
        return channel_embed
    
    
class BungieClanEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        
    async def info_embed(self, name, callsign, motto, about, author_icon_url,
                          clan_icon_url, founder_name, level_cap, interaction,
                          members_list, members_count, creation_date, exp, level,
                          rewards):
        
        members = ''
        for member in members_list:
            user = discord.utils.get(interaction.guild.members, display_name=member)
            if user is not None:
                members += f'{member} - {user.mention} \n'
            else:
                members += f'{member} \n'
        
        clan_rewards = ''
        for key, value in rewards.items():
            if value == True:
                clan_rewards += f'{key}: ✅ \n'
            else:
                clan_rewards += f'{key}: ❌ \n'
        
                                            
        embed = discord.Embed(title=f'{name} [{callsign}]', description=motto,
                              color=0xff1a1a, timestamp=datetime.now())
        embed.set_author(name='Commander Zavala', icon_url=author_icon_url)
        embed.set_thumbnail(url=clan_icon_url)
        embed.add_field(name='About', value=about, inline=False)
        embed.add_field(name='Founder', value=founder_name, inline=True)
        embed.add_field(name='Creation date', value=creation_date, inline=True)
        embed.add_field(name='Progression', value=f'Exp: {exp}/600000 \n' \
                        f'Level: {level}/{level_cap}', inline=False)
        embed.add_field(name=f'Weekly engrams:', value=clan_rewards, inline=True)
        embed.add_field(name=f'Members [{members_count}]', value=members,
                        inline=False)
        embed.set_image(url='https://bungie.net/img/Themes/Group_Community1/struct_images/group_top_banner.jpg')
        embed.set_footer(text='ZEN • Commander Zavala @2022', icon_url=self.url)
        
        return embed