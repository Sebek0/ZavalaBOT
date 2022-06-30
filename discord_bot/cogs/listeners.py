import discord
import logging
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from discord_bot.embeds import MessageLogEmbed, ChannelLogEmbed
from discord_bot.helper_functions import purge_checkpoint_channel

load_dotenv()
logger = logging.getLogger('discord_bot')


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))
        super().__init__()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            log_embed = MessageLogEmbed()
            log_message = await log_embed.embed('new', message.author, message)
            log_channel = self.bot.get_channel(self.log_channel_id)
            await log_channel.send(embed=log_message)
            logger.info(f'{message.author} sent message in {message.channel.name}.')
            
        if message.channel.id == int(os.getenv('CHECKPOINTS_CHANNEL_ID')):
            await purge_checkpoint_channel(self.bot)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot:
            log_embed = MessageLogEmbed()
            log_message = await log_embed.embed('update', before.author,
                                                before=before,
                                                after=after)
            log_channel = self.bot.get_channel(self.log_channel_id)
            await log_channel.send(embed=log_message)
            logger.info(f'{before.author} updated message in {before.channel.name}.')
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            log_embed = MessageLogEmbed()
            log_message = await log_embed.embed('delete', message.author, message)
            log_channel = self.bot.get_channel(self.log_channel_id)
            await log_channel.send(embed=log_message)
            logger.info(f'Message in {message.channel.name} has been deleted.')
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_embed = ChannelLogEmbed()
        log_message = await log_embed.embed('new', channel)
        log_channel = self.bot.get_channel(self.log_channel_id)
        await log_channel.send(embed=log_message)  
        logger.info(f'Channel {channel.name} has been created.')
        
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_embed = ChannelLogEmbed()
        log_message = await log_embed.embed('update', before=before, after=after)
        log_channel = self.bot.get_channel(self.log_channel_id)
        await log_channel.send(embed=log_message)   
        logger.info(f'Channel {before.name} has been updated to {after.name}.')  
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_embed = ChannelLogEmbed()
        log_message = await log_embed.embed('delete', channel)
        log_channel = self.bot.get_channel(self.log_channel_id)
        await log_channel.send(embed=log_message)
        logger.info(f'Channel {channel.name} has been deleted.')
                  
    @commands.Cog.listener()    
    async def on_disconnect(self):
        pass
    
    @commands.Cog.listener()    
    async def on_error(self, event, *args, **kwargs):
        pass
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        channel = self.get_channel(id=957923111876042852)
        await channel.send(invite.inviter, invite.code)
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        pass
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass
    
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        pass
    
    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        print(thread)
        #channel = self.get_chnanel(id=957923111876042852)
        #await channel.send(thread.guild, thread.name, thread.owner)
    
    @commands.Cog.listener()   
    async def on_thread_remove(self, thread):
        print(thread) 
    
    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        print(before, after)
       
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))