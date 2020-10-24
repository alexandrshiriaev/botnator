import discord
from discord.ext import commands
import datetime
import os
import psycopg2
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.log_channel = self.bot.get_channel(671768631603888158)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 660793084703145985:
            embed = discord.Embed(
                description = f'Участник {member.mention} присоединился на сервер.',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            await self.log_channel.send(embed=embed)
            await member.add_roles(member.guild.get_role(671376663338156033))

    # @commands.Cog.listener()
    # async def on_member_remove(self, member):
    #     embed = discord.Embed(
    #         description = f'Участник {member.mention} покинул сервер.',
    #         color = discord.Color.orange(),
    #         timestamp = datetime.datetime.utcnow()
    #     )
    #     await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild.id == 660793084703145985:
            if before.content != after.content:
                if not after.author.bot:
                    self.author = after.author
                    embed = discord.Embed(
                        description = f'[Сообщение]({before.jump_url}) было изменено',
                        color = discord.Color.orange(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.add_field(name='Старый контент:', value=f'```{before.content}```', inline=False)
                    embed.add_field(name='Новый контент:', value=f'```{after.content}```', inline=False)
                    embed.add_field(name='Автор', value=self.author.mention, inline=True)
                    embed.add_field(name='Канал', value=after.channel.mention, inline=True)
                    await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild.id == 660793084703145985:
            if message.channel.id != 742047899856404522:
                if not message.author.bot:
                    self.author = message.author
                    embed = discord.Embed(
                        description = 'Сообщение было удалено',
                        color = discord.Color.orange(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.add_field(name='Удалённое сообщение', value=f'```{message.content}```', inline=False)
                    embed.add_field(name='Автор', value=self.author.mention, inline=True)
                    embed.add_field(name='Канал', value=message.channel.mention, inline=True)
                    await self.log_channel.send(embed=embed)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id == 660793084703145985:
            if before.display_name != after.display_name:
                embed = discord.Embed(
                    description = f'{after.mention} сменил псевдоним.',
                    color = discord.Color.orange(),
                    timestamp = datetime.datetime.utcnow()
                )
                embed.add_field(name='Старый псевдоним', value=f'```{before.display_name}```', inline=False)
                embed.add_field(name='Новый псевдоним', value=f'```{after.display_name}```', inline=False)
                await self.log_channel.send(embed=embed)        

    @commands.command()
    @commands.has_any_role(668888227817586688, 671056120433082419, 742063102111252610)
    async def message(self, ctx, channel : discord.TextChannel, *, arg):
        if ctx.guild.id == 660793084703145985:
            title, description = arg.split('|')
            title = title.strip()
            description = description.strip()
            guild = ctx.guild
            embed = discord.Embed(
                title=title,
                description=description,
                color = discord.Color.orange()
            )
            embed.set_footer(text=f'С уважением, модерация {guild.name}!')
            await channel.send(embed=embed)
            embed1 = discord.Embed(
                description = f'В канале {channel.mention} было размещено новое сообщение.',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed1.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            embed1.add_field(name='Контент', value=description, inline=False)
            await self.log_channel.send(embed=embed1)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.guild.id == 660793084703145985:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description = f'Участник {member.mention} был выгнан с сервера',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            if reason != None:
                embed.add_field(name='Причина', value=f'{reason}', inline=False)
            await self.log_channel.send(embed=embed)
            embed1 = discord.Embed(
                description = f'{member.mention}, Вы были выгнаны с сервера **{ctx.guild.name}**',
                color = discord.Color.orange()
            )
            embed1.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            embed1.add_field(name='Причина', value=f'{reason}', inline=False)
            try: 
                await member.send(embed=embed1)
            except:
                print('Cannot send message to user.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.guild.id == 660793084703145985:
            await member.ban(reason=reason)
            embed = discord.Embed(
                description = f'Участник {member.mention} был забанен на сервере',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            if reason != None:
                embed.add_field(name='Причина', value=f'{reason}', inline=False)
            await self.log_channel.send(embed=embed)
            embed1 = discord.Embed(
                description = f'{member.mention}, Вы были забанены на сервере **{ctx.guild.name}**',
                color = discord.Color.orange()
            )
            embed1.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            if reason != None:
                embed1.add_field(name='Причина', value=f'{reason}', inline=False)
            try: 
                await member.send(embed=embed1)
            except:
                print('Cannot send message to user.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        if ctx.guild.id == 660793084703145985:
            banned_users = await ctx.guild.bans()
            user_name, user_discriminator = member.split('#')
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (user_name, user_discriminator):
                    await ctx.guild.unban(user)
                    embed = discord.Embed(
                        description = f'Пользовать {user.mention} был разбанен на сервере',
                        color = discord.Color.orange(),
                        timestamp = datetime.datetime.utcnow()
                    )
                    embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
                    embed1 = discord.Embed(
                        description = f'{user.mention}, Вы были разблокированы на сервере **{ctx.guild.name}**.',
                        color = discord.Color.orange()
                    )
                    try: 
                        await user.send(embed=embed1)
                    except:
                        print('Cannot send message to user.')
                    await self.log_channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        user_id = member.id
        if ctx.guild.id == 660793084703145985:
            con = psycopg2.connect(
                host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                database = 'dfe269uifoco1o',
                user = 'ncdnwynzrmqjnc',
                password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                port = 5432
                )
            cur = con.cursor()
            cur.execute(f"SELECT user_id, amount_of_warns FROM warns WHERE user_id='{user_id}'")
            selected = cur.fetchone()
            if selected != None:
                if selected[1] < 2:
                    cur.execute(f"UPDATE warns SET amount_of_warns={selected[1] + 1} WHERE user_id='{selected[0]}'")
                else:
                    cur.execute(f"UPDATE warns SET amount_of_warns=0 WHERE user_id='{selected[0]}'")
                    kick = True
            else:
                cur.execute(f"INSERT INTO warns (user_id, amount_of_warns) VALUES ('{user_id}', 1)")
                selected = (user_id, 0)
            con.commit()
            cur.close()
            con.close()
            embed = discord.Embed(
                description = f'Участнику {member.mention} было сделано предупреждение',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            embed.add_field(name='Причина', value=reason, inline=False)
            embed.add_field(name='Количество предупреждений', value=selected[1] + 1)
            embed1 = discord.Embed(
                description = f'{member.mention}, Вы были предупреждены модератором {ctx.message.author.mention}',
                color = discord.Color.orange()
            )
            embed1.add_field(name='Причина', value=reason, inline=False)
            embed1.add_field(name='Количество предупреждений', value=selected[1] + 1, inline=False)
            embed1.set_footer(text=f'С уважением, модерация {ctx.guild.name}!')
            await self.log_channel.send(embed=embed)
            try:
                await member.send(embed=embed1)
            except:
                print('Cannot send message to user.')
            if kick:
                embed2 = discord.Embed(
                    description = f'Участник {member.mention} был выгнан с сервера за максимальное количество предупреждений',
                    color = discord.Color.orange(),
                    timestamp = datetime.datetime.utcnow()
                )
                embed3 = discord.Embed(
                    description = f'{member.mention}, Вы были выгнаны с сервера за максимальное количество предупреждений',
                    color = discord.Color.orange(),
                )
                await member.kick()
                await self.log_channel.send(embed=embed2)
                try: 
                    await member.send(embed=embed3)
                except:
                    print('Cannot send message to user.')
            
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unwarn(self, ctx, member: discord.Member):
        user_id = member.id
        if ctx.guild.id == 660793084703145985:
            con = psycopg2.connect(
                host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                database = 'dfe269uifoco1o',
                user = 'ncdnwynzrmqjnc',
                password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                port = 5432
                )
            cur = con.cursor()
            cur.execute(f"SELECT user_id, amount_of_warns FROM warns WHERE user_id='{user_id}'")
            selected = cur.fetchone()
            if selected == None or selected[1] == 0:
                cur.close()
                con.close()
                embed = discord.Embed(
                    description = f'Участник {member.mention} не имеет предупреждений',
                    color = discord.Color.orange()
                )
                await self.log_channel.send(embed=embed)
            else:
                cur.execute(f"UPDATE warns SET amount_of_warns={selected[1] - 1} WHERE user_id='{selected[0]}'")
                con.commit()
                cur.close()
                con.close()
                embed = discord.Embed(
                    description = f'Участнику {member.mention} было снято предупреждение',
                    color = discord.Color.orange(),
                    timestamp = datetime.datetime.utcnow()
                )
                embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
                embed.add_field(name='Количество предупреждений', value=selected[1] - 1)
                embed1 = discord.Embed(
                    description = f'{member.mention}, с вас было снято предупреждение',
                    color = discord.Color.orange()
                )
                embed1.add_field(name='Количество предупреждений', value=selected[1] - 1, inline=False)
                await self.log_channel.send(embed=embed)
                try: 
                    await member.send(embed=embed1)
                except:
                    print('Cannot send message to user.')

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member, time: int, *, reason):
        muted_role = ctx.guild.get_role(743717823037308929)
        if ctx.guild.id == 660793084703145985:
            if not (muted_role in member.roles):
                await member.add_roles(muted_role)
                embed = discord.Embed(
                    description = f'Участник {member.mention} был заглушён',
                    color = discord.Color.orange(),
                    timestamp = datetime.datetime.utcnow()
                )
                embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
                embed.add_field(name='Причина', value=reason, inline=False)
                embed.add_field(name='Время', value=str(time) + ' секунд', inline=False)
                await self.log_channel.send(embed=embed)
                embed1 = discord.Embed(
                    description = f'{member.mention}, Вы были заглушены на сервере **{ctx.guild.name}**',
                    color = discord.Color.orange()
                )
                embed1.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
                embed1.add_field(name='Причина', value=reason, inline=False)
                embed1.add_field(name='Время', value=str(time) + ' секунд', inline=False)
                try: 
                    await member.send(embed=embed1)
                except:
                    print('Cannot send message to user.')

                await asyncio.sleep(time)
                if (muted_role in member.roles):
                    await member.remove_roles(muted_role)
            else:
                embed = discord.Embed(
                    description = f'Участник {member.mention} был уже заглушён. Используйте команду `!unmute` для того, чтобы разглушить пользователя.',
                    color = discord.Color.orange()
                )
                await self.log_channel.send(embed=embed)
    
    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = ctx.guild.get_role(743717823037308929)
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            embed = discord.Embed(
                description = f'Участник {member.mention} был разглушён',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention)
            embed1 = discord.Embed(
                description = f'{member.mention}, Вы были разглушены на сервере **{ctx.guild.name}**',
                color = discord.Color.orange()
            )
            await self.log_channel.send(embed=embed)
            try: 
                await member.send(embed=embed1)
            except:
                print('Cannot send message to user.')
        else:
            embed = discord.Embed(
                description = f'Участник {member.mention} не имеет заглушки. Используйте команду `!mute` для того, чтобы заглушить пользователя.',
                color= discord.Color.orange()
            )
            await self.log_channel.send(embed=embed)


    @commands.command()
    async def ticket(self, ctx, moderator: discord.Member, *, reason):
        if ctx.guild.id == 660793084703145985:
            if ctx.guild.get_channel(671399645578264606) == ctx.channel:
                embed = discord.Embed(
                    description = f'Жалоба на модератора {moderator.mention}',
                    color = discord.Color.orange(),
                )
                embed.set_footer(text='Спасибо за ваше обращение, вы помогаете делать наш сервер лучше 😉')
                embed.add_field(name='Автор', value=ctx.message.author.mention, inline=False)
                embed.add_field(name='Суть жалобы', value=reason, inline=False)
                await ctx.send(embed=embed)
        
    @commands.command()
    async def suggestion(self, ctx, *, text):
        if ctx.channel.id == 743746501817401346:
            await ctx.message.delete()
            embed = discord.Embed(
                color = discord.Color.orange()
            )
            embed.add_field(name='Автор', value=ctx.message.author.mention, inline=False)
            embed.add_field(name='Суть предложения', value=text, inline=False)
            embed.set_footer(text='Спасибо за ваше обращение, вы помогаете делать наш сервер лучше 😉')
            message = await ctx.channel.send(embed=embed)
            await message.add_reaction('✔')
            await message.add_reaction('❌')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        if ctx.guild.id == 660793084703145985:
        # if ctx.guild.get_channel(671768631603888158) != ctx.channel:
            await ctx.channel.purge(limit=amount + 1)
            embed = discord.Embed(
                description = f'Удалено {amount} сообщений',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention)
            embed.add_field(name='Канал', value=ctx.channel.mention)
            await self.log_channel.send(embed=embed)

    @commands.command()
    async def report(self, ctx, member: discord.Member, *, reason):
        if ctx.guild.id == 660793084703145985:
            embed = discord.Embed(
                description = f'Ваша жалоба на участника {member.mention} была передана модерации сервера.',
                color = discord.Color.orange()
            )
            embed.set_footer(text='Спасибо за ваше обращение, вы помогаете делать наш сервер лучше 😉')
            await ctx.send(embed=embed)
            embed1 = discord.Embed(
                description = f'Жалоба на участника {member.mention}',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed1.add_field(name='Автор', value=ctx.message.author.mention, inline=False)
            embed1.add_field(name='Суть жалобы', value=reason, inline=False)
            await self.log_channel.send(embed=embed1)

def setup(bot):
    bot.add_cog(Moderation(bot))