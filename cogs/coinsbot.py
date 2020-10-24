import discord
from discord.ext import commands
import datetime
import os
import psycopg2
import asyncio
import random
import json

class Coinsbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.log_channel = self.bot.get_channel(671768631603888158)
        self.guild = self.bot.get_guild(660793084703145985)
        self.array_of_roles = [
            [self.guild.get_role(671377070273593384), 50], [self.guild.get_role(671377583622848563), 200], [self.guild.get_role(671377584793059358), 500]
        ]
        self.array_of_tickets = [
            ['Цветовая роль', 2000], ['Уникальная роль', 5000]
        ]
        self.array_of_crates = [
            ['Маленький кейс', 100, [
                {'type': 'coins', 'value': 75, 'chance': 30},
                {'type': 'coins', 'value': 90, 'chance': 25},
                {'type': 'coins', 'value': 125, 'chance': 15},
                {'type': 'role', 'value': self.guild.get_role(671377070273593384), 'chance': 23},
                {'type': 'role', 'value': self.guild.get_role(671377583622848563), 'chance': 7}
                ]], 
            ['Средний кейс', 500, [
                {'type': 'coins', 'value': 400, 'chance': 35},
                {'type': 'coins', 'value': 250, 'chance': 25},
                {'type': 'coins', 'value': 750, 'chance': 13},
                {'type': 'role', 'value': self.guild.get_role(671377584793059358), 'chance': 20},
                {'type': 'colored_ticket', 'value': 1, 'chance': 7}
            ]], 
            ['Большой кейс', 2500, [
                {'type': 'coins', 'value': 1100, 'chance': 20},
                {'type': 'colored_ticket', 'value': 1, 'chance': 34},
                {'type': 'coins', 'value': 2200, 'chance': 25},
                {'type': 'coins', 'value': 3300, 'chance': 14},
                {'type': 'unique_ticket', 'value': 1, 'chance': 7},
                   
            ]]
        ]
        self.ore_dict = [
            ['Камень', 2, 'stone'],
            [
                ['Уголь', 5, 45, 'coal'],
                ['Лазурит', 12, 10, 'lapis'],
                ['Красная пыль', 10, 15, 'redstone'],
                ['Железо', 7, 30, 'iron'],
            ],
            [
                ['Золото', 60, 70, 'gold'],
                ['Алмазы', 125, 15, 'diamond'],
                ['Изумруд', 150, 10, 'emerald'],
                ['Незерит', 200, 5, 'netherite']
            ]
        ]
        self.opencrate_data = None 
        self.unique_role_data = None
        self.coinflip_data = None
        self.mine_data = None
        self.path = 'cogs\coinsbot.json'
        self.unavailable_to_mine = []

    async def get_ores(self, cur, user_id: str):
        cur.execute(f"SELECT coal, lapis, redstone, iron, gold, diamond, emerald, netherite, user_id, stone FROM mine WHERE user_id='{user_id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO mine (coal, lapis, redstone, iron, gold, diamond, emerald, netherite, user_id, stone) VALUES (0, 0, 0, 0, 0, 0, 0, 0, '{user_id}', 0)")
            selected = [0, 0, 0, 0, 0, 0, 0, 0, user_id, 0]
        return selected

    async def set_ores(self, cur, user_id: str, ores):
        if await self.get_ores != None:
            cur.execute(f"UPDATE mine SET coal={ores[0]}, lapis={ores[1]}, redstone={ores[2]}, iron={ores[3]}, gold={ores[4]}, diamond={ores[5]}, emerald={ores[6]}, netherite={ores[7]}, stone={ores[8]} WHERE user_id='{user_id}'")
        else:
            cur.execute(f"INSERT INTO mine (coal, lapis, redstone, iron, gold, diamond, emerald, netherite, user_id, stone) VALUES (0, 0, 0, 0, 0, 0, 0, 0, '{user_id}', 0)")
            cur.execute(f"UPDATE mine SET coal={ores[0]}, lapis={ores[1]}, redstone={ores[2]}, iron={ores[3]}, gold={ores[4]}, diamond={ores[5]}, emerald={ores[6]}, netherite={ores[7]}, stone={ores[8]} WHERE user_id='{user_id}'")


    async def get_warns(self, cur, user_id: str):
        cur.execute(f"SELECT user_id, amount_of_warns FROM warns WHERE user_id='{user_id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            selected = (user_id, 0)
        return selected[1]

    async def get_coins(self, cur, user_id: str):
        cur.execute(f"SELECT user_id, coins FROM warns WHERE user_id='{user_id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            selected = (user_id, 0)
        return selected[1]

    async def set_coins(self, cur, user_id: str, coins):
        if await self.get_coins(cur, user_id) != None:
            cur.execute(f"UPDATE warns SET coins={coins} WHERE user_id='{user_id}'")
        else:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            cur.execute(f"UPDATE warns SET coins={coins} WHERE user_id='{user_id}'")
        
    async def get_unique(self, cur, user_id: str):
        cur.execute(f"SELECT user_id, unique_ticket FROM warns WHERE user_id='{user_id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            selected = (user_id, 0)
        return selected[1]

    async def set_unique(self, cur, user_id: str, value):
        if await self.get_coins(cur, user_id) != None:
            cur.execute(f"UPDATE warns SET unique_ticket={value} WHERE user_id='{user_id}'")
        else:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            cur.execute(f"UPDATE warns SET unique_ticket={value} WHERE user_id='{user_id}'")

    async def get_colored(self, cur, user_id: str):
        cur.execute(f"SELECT user_id, colored_ticket FROM warns WHERE user_id='{user_id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            selected = (user_id, 0)
        return selected[1]

    async def set_colored(self, cur, user_id: str, value):
        if await self.get_coins(cur, user_id) != None:
            cur.execute(f"UPDATE warns SET colored_ticket={value} WHERE user_id='{user_id}'")
        else:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{user_id}', 0, 0, 0, 0, 0)")
            cur.execute(f"UPDATE warns SET unique_ticket={value} WHERE user_id='{user_id}'")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            for role in reversed(after.roles):
                if role.name == 'Магистр':
                    array_of_roles_for_delete = [self.guild.get_role(671377583622848563), self.guild.get_role(671377070273593384), self.guild.get_role(671376663338156033)]
                    break
                elif role.name == 'Мастер':
                    array_of_roles_for_delete = [self.guild.get_role(671377070273593384), self.guild.get_role(671376663338156033)]
                    break
                elif role.name == 'Бывалый':
                    array_of_roles_for_delete = [self.guild.get_role(671376663338156033)]
                    break
            for role in reversed(after.roles):
                if role.name == 'Почётный шахтёр':
                    array_of_roles_for_delete1 = [self.guild.get_role(747401227846942763), self.guild.get_role(747401276228108378)]
                    break
                elif role.name == 'Опытный шахтёр':
                    array_of_roles_for_delete1 = [self.guild.get_role(747401276228108378)]
                    break
            try:
                for role in array_of_roles_for_delete:
                    await after.remove_roles(role)
            except:
                pass
            try:
                for role in array_of_roles_for_delete1:
                    await after.remove_roles(role)
            except:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 661114969168805898:
            if not message.content.startswith('!'):
                con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                )
                cur = con.cursor()
                coins = await self.get_coins(cur, str(message.author.id))
                await self.set_coins(cur, str(message.author.id), coins + 1)
                con.commit()
                cur.close()
                con.close()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user_id = payload.user_id
        emoji = payload.emoji
        message_id = payload.message_id
        role_channel = self.guild.get_channel(671746023751942165)
        nswf_channel = self.guild.get_channel(742047899856404522)
        member = self.guild.get_member(payload.user_id)
        if message_id == 747793900432916540 or message_id == 747793897068953620 or message_id == 747793894049054771:
            if emoji.name == '✔':
                con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                )
                cur = con.cursor()
                if message_id == 747793900432916540:
                    necessary_role = [
                        self.guild.get_role(747401195248812053), {'gold': 50, 'diamond': 15, 'emerald': 10, 'netherite': 5}
                    ]
                elif message_id == 747793897068953620:
                    necessary_role = [
                        self.guild.get_role(747401227846942763), {'coal': 50, 'iron': 30, 'redstone': 15, 'lapis': 10}
                    ]
                elif message_id == 747793894049054771:
                    necessary_role = [
                        self.guild.get_role(747401276228108378), {'stone': 100}
                    ]
                if (necessary_role[0] == self.guild.get_role(747401195248812053) and self.guild.get_role(747401227846942763) in member.roles) or (necessary_role[0] == self.guild.get_role(747401227846942763) and self.guild.get_role(747401276228108378) in member.roles) or necessary_role[0] == self.guild.get_role(747401276228108378):
                    if (necessary_role[0] == self.guild.get_role(747401195248812053) and not (necessary_role[0] in member.roles)) or (necessary_role[0] == self.guild.get_role(747401227846942763) and not (necessary_role[0] in member.roles or self.guild.get_role(747401195248812053) in member.roles)) or (necessary_role[0] == self.guild.get_role(747401276228108378) and not (necessary_role[0] in member.roles or self.guild.get_role(747401195248812053) in member.roles or self.guild.get_role(747401195248812053) in member.roles)):
                        selected = {}
                        if self.get_ores(cur, str(user_id)) != None:
                            for resources in necessary_role[1]:
                                cur.execute(f"SELECT {resources} FROM mine WHERE user_id='{user_id}'")
                                selected.update({resources: cur.fetchone()[0]})
                        for resources in necessary_role[1]:
                            if selected[resources] >= necessary_role[1][resources]:
                                pass
                            else:
                                embed = discord.Embed(
                                    title = 'Покупка роли',
                                    description = f'{member.mention}, у вас недостаточно ресурсов для покупки этой роли.',
                                    color = discord.Color.orange()
                                )
                                message = await role_channel.send(embed=embed)
                                await asyncio.sleep(15)
                                await message.delete()
                                break
                        else:
                            embed = discord.Embed(
                                title = 'Покупка роли',
                                description = f'{member.mention}, вы уверены, что хотите преобрести эту роль? Для подтверждения действия нажмите на реакцию "✔" под этим сообщением в течении 15 секунд.',
                                color = discord.Color.orange()
                            )
                            message = await role_channel.send(embed=embed)
                            await message.add_reaction('✔')
                            await message.add_reaction('❌')
                            await asyncio.sleep(15)
                            message = await role_channel.fetch_message(message.id)
                            for reaction in message.reactions:
                                if reaction.emoji == '✔':
                                    async for user in reaction.users():
                                        if user == member:
                                            for resources in necessary_role[1]:
                                                cur.execute(f"UPDATE mine SET {resources}={(selected[resources] - necessary_role[1][resources])} WHERE user_id='{user_id}'")
                                                con.commit()
                                            await member.add_roles(necessary_role[0])
                                            embed = discord.Embed(
                                                title = 'Покупка роли',
                                                description = f'Вы преобрели роли {necessary_role[0].mention}. Для того, чтобы проверить количество оставшихся ресурсов в вашем инвентаре используйте команду `!stats`.',
                                                color = discord.Color.orange()
                                            )
                                            message1 = await role_channel.send(embed=embed)
                            else:
                                await asyncio.sleep(10)
                                await message.delete()
                                try:
                                    await message1.delete()
                                except:
                                    pass
                    else:
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'{member.mention}, у вас уже есть эта или более привилегированная роль.',
                            color = discord.Color.orange()
                        )
                        message = await role_channel.send(embed=embed)
                        await asyncio.sleep(15)
                        await message.delete()
                else:
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description = f'{member.mention}, для покупки этой роли - сначала вам необходимо преобрести предыдущую.',
                        color = discord.Color.orange()
                    )
                    message = await role_channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()

        if message_id == 744838540181110825 or message_id == 744838536863416381 or message_id == 744838533155651604:
            if emoji.name == '✔':
                if message_id == 744838540181110825:
                    necessary_role = self.array_of_roles[2]
                elif message_id == 744838536863416381:
                    necessary_role = self.array_of_roles[1]
                elif message_id == 744838533155651604:
                    necessary_role = self.array_of_roles[0]
                con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                        )
                cur = con.cursor()
                coins = await self.get_coins(cur, str(user_id))
                if coins >= necessary_role[1]:
                    if not (necessary_role[0] in self.guild.get_member(user_id).roles):
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'{member.mention}, вы уверены, что хотите преобрести эту роль? Для подтверждения действия нажмите на реакцию "✔" под этим сообщением в течении 15 секунд.',
                            color = discord.Color.orange()
                        )
                        embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**', inline=False)
                        embed.add_field(name='Стоимость роли', value=f'**{necessary_role[1]} коинов**', inline=False)
                        message = await role_channel.send(embed=embed)
                        await message.add_reaction('✔')
                        await message.add_reaction('❌')
                        await asyncio.sleep(15)
                        message = await role_channel.fetch_message(message.id)
                        for reaction in message.reactions:
                            if reaction.emoji == '✔':
                                async for user in reaction.users():
                                    if user == member:
                                        await self.set_coins(cur, str(user_id), coins - necessary_role[1])
                                        con.commit()
                                        await member.add_roles(necessary_role[0])
                                        embed = discord.Embed(
                                            title = 'Покупка роли',
                                            description = f'{member.mention}, вы преобрели роль {necessary_role[0].mention}',
                                            color = discord.Color.orange()
                                        )
                                        coins = await self.get_coins(cur, str(user_id))
                                        embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**')
                                        message1 = await role_channel.send(embed=embed)
                        else:
                            await asyncio.sleep(10)
                            await message.delete()
                            try:
                                await message1.delete()
                            except:
                                pass
                    else:
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'{member.mention}, у вас уже есть эта роль.',
                            color = discord.Color.orange()
                        )
                        message = await role_channel.send(embed=embed)
                        await asyncio.sleep(15)
                        await message.delete()
                else:
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description = f'{member.mention}, у вас недостаточно коинов для покупки этой роли.',
                        color = discord.Color.orange()
                    )
                    message = await role_channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                cur.close()
                con.close()
        if message_id == 745363796469481617 or message_id == 745363800504664064:
            if emoji.name == '✔':
                if message_id == 745363796469481617:
                    necessary_ticket = self.array_of_tickets[0]
                elif message_id == 745363800504664064:
                    necessary_ticket = self.array_of_tickets[1]
                con = psycopg2.connect(
                            host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                            database = 'dfe269uifoco1o',
                            user = 'ncdnwynzrmqjnc',
                            password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                            port = 5432
                        )
                cur = con.cursor()
                coins = await self.get_coins(cur, str(user_id))
                if coins >= necessary_ticket[1]:
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'{member.mention}, вы уверены, что хотите преобрести этот билет? Для подтверждения действия нажмите на реакцию "✔" под этим сообщением в течении 15 секунд.',
                            color = discord.Color.orange()
                        )
                        embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**', inline=False)
                        embed.add_field(name='Стоимость роли', value=f'**{necessary_ticket[1]} коинов**', inline=False)
                        message = await role_channel.send(embed=embed)
                        await message.add_reaction('✔')
                        await message.add_reaction('❌')
                        await asyncio.sleep(15)
                        message = await role_channel.fetch_message(message.id)
                        for reaction in message.reactions:
                            if reaction.emoji == '✔':
                                async for user in reaction.users():
                                    if user == member:
                                        await self.set_coins(cur, str(user_id), coins - necessary_ticket[1])
                                        con.commit()
                                        if necessary_ticket[0] == 'Цветовая роль':
                                            member_have_tickets = await self.get_colored(cur, str(user_id))
                                            await self.set_colored(cur, str(user_id), member_have_tickets + 1)
                                            con.commit()
                                            embed = discord.Embed(
                                                title = 'Покупка роли',
                                                description = f'{member.mention}, вы преобрели билет на цветовую роль.',
                                                color = discord.Color.orange()
                                            )
                                            coins = await self.get_coins(cur, str(user_id))
                                            embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**')
                                            message1 = await role_channel.send(embed=embed)
                                        elif necessary_ticket[1] == 'Уникальная роль':
                                            member_have_tickets = await self.get_unique(cur, str(user_id))
                                            await self.set_unique(cur, str(user_id), member_have_tickets + 1)
                                            con.commit()
                                            embed = discord.Embed(
                                                title = 'Покупка роли',
                                                description = f'{member.mention}, вы преобрели билет на уникальную роль.',
                                                color = discord.Color.orange()
                                            )
                                            coins = await self.get_coins(cur, str(user_id))
                                            embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**')
                                            message1 = await role_channel.send(embed=embed)      
                        else:
                            await asyncio.sleep(10)
                            await message.delete()
                            try:
                                await message1.delete()
                            except:
                                pass
                else:
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description = f'{member.mention}, у вас недостаточно коинов для покупки этого билета.',
                        color = discord.Color.orange()
                    )
                    message = await role_channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                cur.close()
                con.close()
        try:
            if message_id == self.coinflip_data[2].id and user_id == self.coinflip_data[1].id:
                con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                )
                cur = con.cursor()
                if random.randint(0, 1) == 1:
                    win = True
                else:
                    win = False
                member = self.coinflip_data[0]
                member1 = self.coinflip_data[1]
                money = self.coinflip_data[3]
                channel = self.coinflip_data[2].channel
                coins = await self.get_coins(cur, str(member.id))
                coins1 = await self.get_coins(cur, str(member1.id))
                if win:
                    await self.set_coins(cur, str(member.id), coins + money)
                    await self.set_coins(cur, str(member1.id), coins1 - money)
                    con.commit()
                    embed = discord.Embed(
                        title = 'Coinflip',
                        description = f'{self.coinflip_data[0].mention} сыграл в **Coinflip** с {self.coinflip_data[1].mention} на **{money} коинов**.',
                        color = discord.Color.orange()
                    )
                    embed.add_field(name='Победитель', value=f'{self.coinflip_data[0].mention}', inline=False)
                    message = await channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                else:
                    await self.set_coins(cur, str(member.id), coins - money)
                    await self.set_coins(cur, str(member1.id), coins1 + money)
                    con.commit()
                    embed = discord.Embed(
                        title = 'Coinflip',
                        description = f'{member.mention} сыграл в **Coinflip** с {member1.mention} на **{money} коинов**.',
                        color = discord.Color.orange()
                    )
                    embed.add_field(name='Победитель', value=f'{member1.mention}', inline=False)
                    message = await channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                    self.coinflip_data = None
                cur.close()
                con.close()
        except:
            pass
        try:
            if message_id == self.opencrate_data[0]:
                message = await nswf_channel.fetch_message(message_id)
                if not member.bot:
                    self.opencrate_data = None
                    if emoji.name == '1️⃣' or emoji.name == '2️⃣' or emoji.name == '3️⃣':
                        if emoji.name == '1️⃣':
                            opened_case = self.array_of_crates[0]
                        elif emoji.name == '2️⃣':
                            opened_case = self.array_of_crates[1]
                        elif emoji.name == '3️⃣':
                            opened_case = self.array_of_crates[2]
                        con = psycopg2.connect(
                            host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                            database = 'dfe269uifoco1o',
                            user = 'ncdnwynzrmqjnc',
                            password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                            port = 5432
                            )
                        cur = con.cursor()
                        coins = await self.get_coins(cur, str(user_id))
                        if coins >= opened_case[1]:
                            start_chance = 0
                            randomed_int = random.randint(0, 100)
                            for prizes in opened_case[2]:
                                if randomed_int >= start_chance and randomed_int <= start_chance + prizes['chance']:
                                    prize = prizes
                                start_chance += (prizes['chance'] + 1)
                            await self.set_coins(cur, str(user_id), coins - opened_case[1])
                            con.commit()
                            coins = await self.get_coins(cur, str(user_id))
                            colored_tickets = await self.get_colored(cur, str(user_id))
                            unique_tickets = await self.get_unique(cur, str(user_id))
                            if prize['type'] == 'coins':
                                await self.set_coins(cur, str(user_id), coins + prize['value'])
                                con.commit()
                                embed = discord.Embed(
                                    title = 'Открытие кейсов',
                                    description = f'{member.mention} открыл **{opened_case[0]}** и выиграл **{prize["value"]} коинов**.',
                                    color = discord.Color.orange()
                                )
                                message1 = await nswf_channel.send(embed=embed)
                            elif prize['type'] == 'role':
                                have_role = False
                                for role in reversed(member.roles):
                                    if (role.name == 'Магистр' or role.name == 'Мастер' or role.name == 'Бывалый') and role.name != prize['value'].name and role.position > prize['value'].position:
                                        have_role = True
                                
                                if not (prize['value'] in member.roles) and not have_role:
                                    await member.add_roles(prize['value'])
                                    embed = discord.Embed(
                                        title = 'Открытие кейсов',
                                        description = f'{member.mention} открыл **{opened_case[0]}** и выиграл **роль {prize["value"].mention}**.',
                                        color = discord.Color.orange()
                                    )
                                elif (prize['value'] in member.roles) or have_role:
                                    for role_array in self.array_of_roles:
                                        if role_array[0] == prize['value']:
                                            coins = await self.get_coins(cur, str(user_id))
                                            await self.set_coins(cur, str(user_id), coins + role_array[1])
                                            con.commit()
                                            embed = discord.Embed(
                                                title = 'Открытие кейсов',
                                                description = f'{member.mention} открыл **{opened_case[0]}** и выиграл **роль {prize["value"].mention}**. Однако у него уже есть эта роль, поэтому он получает **{role_array[1]} коинов**.',
                                                color = discord.Color.orange()
                                            )
                                message1 = await nswf_channel.send(embed=embed)
                            elif prize['type'] == 'colored_ticket':
                                await self.set_colored(cur, str(user_id), colored_tickets + prize['value'])
                                con.commit()
                                embed = discord.Embed(
                                    title = 'Открытие кейсов',
                                    description = f'{member.mention} открыл **{opened_case[0]}** и выиграл **{prize["value"]} билет на цветовую роль**.',
                                    color = discord.Color.orange()
                                )
                                message1 = await nswf_channel.send(embed=embed)
                            elif prize['type'] == 'unique_ticket':
                                await self.set_unique(cur, str(user_id), unique_tickets + prize['value'])
                                con.commit()
                                embed = discord.Embed(
                                    title = 'Открытие кейсов',
                                    description = f'{member.mention} открыл **{opened_case[0]}** и выиграл **{prize["value"]} билет на уникальную роль**.',
                                    color = discord.Color.orange()
                                )
                                message1 = await nswf_channel.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title = 'Открытие кейсов',
                                description = f'{member.mention}, у вас недостаточно коинов для открытия кейса.',
                                color = discord.Color.orange()
                            )
                            embed.add_field(name='Стоимость кейса', value=f'**{opened_case[1]} коинов**', inline=False)
                            embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**', inline=False)
                            message1 = await nswf_channel.send(embed=embed)
                        await asyncio.sleep(15)
                        await message1.delete()
                        try:
                            await message.delete()
                        except:
                            pass
                        cur.close()
                        con.close()
        except:
            pass
        
        try:
            if message_id == self.mine_data[0].id and user_id == self.mine_data[1]:
                mine_data = self.mine_data
                self.mine_data = None
                message = mine_data[0]
                stone = mine_data[2]
                first_ore = mine_data[3]
                second_ore = mine_data[4]
                con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                )
                cur = con.cursor()
                if emoji.name == '✔':
                    if await self.get_coins(cur, str(mine_data[1])) != None:
                        necessary_coins = ((stone[0][1] * stone[1]) + (first_ore[0][1] * first_ore[1]) + (second_ore[0][1] * second_ore[1]))
                        coins = await self.get_coins(cur, str(mine_data[1]))
                        await self.set_coins(cur, str(mine_data[1]), coins + necessary_coins)
                        con.commit()
                        embed = discord.Embed(
                            title = 'Шахта',
                            description = f'{self.guild.get_member(user_id).mention}, вы успешно продали добытые ресурсы на сумму **{necessary_coins} коинов**',
                            color = discord.Color.orange()
                        )
                        embed.add_field(name='Ваш баланс', value=f'**{(necessary_coins + coins)} коинов**')
                        new_message = await message.channel.send(embed=embed)
                        await asyncio.sleep(15)
                        await new_message.delete()
                elif emoji.name == '❌':
                    if await self.get_ores(cur, str(mine_data[1])) != None:
                        cur.execute(f"SELECT {stone[0][2]}, {first_ore[0][3]}, {second_ore[0][3]} FROM mine WHERE user_id='{mine_data[1]}'")
                        selected = cur.fetchone()
                        cur.execute(f"UPDATE mine SET {stone[0][2]}={(selected[0] + stone[1])}, {first_ore[0][3]} = {(selected[1] + first_ore[1])}, {second_ore[0][3]} = {(selected[2] + second_ore[1])} WHERE user_id='{mine_data[1]}'")
                        con.commit()
                        embed = discord.Embed(
                            title = 'Шахта',
                            description = f'{self.guild.get_member(user_id).mention}, все ваши добытые ресурсы были добавлены вам в инвентарь.',
                            color = discord.Color.orange()
                        )
                        new_message = await message.channel.send(embed=embed)
                        await asyncio.sleep(15)
                        await new_message.delete()        
                try:
                    await message.delete()
                except:
                    pass
                cur.close()
                con.close()
        except:
            pass

        try:
            if message_id == self.unique_role_data[0]:
                member1 = self.unique_role_data[1]
                if emoji.name == '✔' and not member.bot:
                    role_name = self.unique_role_data[3]
                    role_color = self.unique_role_data[2]
                    created_role = await self.guild.create_role(name=role_name, color=discord.Color(role_color))
                    counter = 0
                    for role in self.guild.roles:
                        counter += 1
                    positions = {
                        created_role: counter - 2
                    }
                    await self.guild.edit_role_positions(positions=positions)
                    await member1.add_roles(created_role)
                    embed1 = discord.Embed(
                        description = f'Заявка участника {member1.mention} на создание уникальной роли была **одобрена**.',
                        color = discord.Color.orange()
                    )
                    embed1.add_field(name='Модератор', value=member.mention)
                    await self.log_channel.send(embed=embed1)
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description = f'Модератор {member.mention} **одобрил** вам заявку на создание уникальной роли.',
                        color = discord.Color.orange()
                    )
                    await member1.send(embed=embed)
                    self.unique_role_data = None
                elif emoji.name == '❌' and not member.bot:
                    con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                    )
                    cur = con.cursor()
                    unique_ticket = await self.get_unique(cur, str(member1.id))
                    await self.set_unique(cur, str(member1.id), unique_ticket + 1)
                    embed1 = discord.Embed(
                        description = f'Заявка участника {member1.mention} на создание уникальной роли была **отклонена**.',
                        color = discord.Color.orange()
                    )
                    embed1.add_field(name='Модератор', value=member.mention)
                    await self.log_channel.send(embed=embed1)
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description = f'Модератор {member.mention} **отклонил** вам заявку на создание уникальной роли. Ваш **билет на уникальную роль** был вернут.',
                        color = discord.Color.orange()
                    )
                    await member1.send(embed=embed)
                    self.unique_role_data = None
                    cur.close()
                    con.close()
        except:
            pass

    @commands.command()
    async def flip(self, ctx, money: int, member: discord.Member = None):
        if ctx.channel.id == 742047899856404522:
            con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                        )
            cur = con.cursor()
            await ctx.message.delete()
            coins = await self.get_coins(cur, str(ctx.message.author.id))
            if money > 0:
                if coins >= money:
                    if member == None:
                        if random.randint(0, 1) == 1:
                            win = True
                        else:
                            win = False
                        if win:
                            await self.set_coins(cur, str(ctx.message.author.id), coins + round((money * 0.8)))
                            con.commit()
                            embed = discord.Embed(
                                title = 'Coinflip',
                                description = f'{ctx.message.author.mention} кидает монетку и **выигрывает {round(money * 0.8)} коинов**.',
                                color = discord.Color.orange()
                            )
                            embed.add_field(name='Баланс', value=f'**{coins + round((money * 0.8))} коинов**', inline=False)
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()
                        else:
                            await self.set_coins(cur, str(ctx.message.author.id), coins - money)
                            con.commit()
                            embed = discord.Embed(
                                title = 'Coinflip',
                                description = f'{ctx.message.author.mention} кидает монетку и **проигрывает {money} коинов**.',
                                color = discord.Color.orange()
                            )
                            embed.add_field(name='Баланс', value=f'**{coins - money} коинов**', inline=False)
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()
                    elif member and not member.bot:
                        coins1 = await self.get_coins(cur, str(member.id))
                        if coins1 >= money:
                            embed = discord.Embed(
                                title = 'Coinflip',
                                description = f'{ctx.message.author.mention} предложил {member.mention} сыграть на **{money} коинов**. {member.mention}, чтобы сыграть нажмите на реакцию "✔" под этим сообщением.',
                                color = discord.Color.orange()
                            )
                            message = await ctx.send(embed=embed)
                            await message.add_reaction('✔')
                            await message.add_reaction('❌')
                            self.coinflip_data = [ctx.message.author, member, message, money]
                            await asyncio.sleep(15)
                            await message.delete()
                        else:
                            embed = discord.Embed(
                                title = 'Coinflip',
                                description = f'{ctx.message.author.mention}, у участника {member.mention} недостаточно коинов для этой ставки.',
                                color = discord.Color.orange()
                            )
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()
                    else:
                        embed = discord.Embed(
                            title = 'Coinflip',
                            description = f'{ctx.message.author.mention}, вы не можете играть с ботом.',
                            color = discord.Color.orange()
                        )
                        message = await ctx.send(embed=embed)
                        await asyncio.sleep(15)
                        await message.delete()
                else:
                    embed = discord.Embed(
                        title = 'Coinflip',
                        description = f'{ctx.message.author.mention}, у вас недостаточно коинов для вашей ставки.',
                        color = discord.Color.orange()
                    )
                    embed.add_field(name='Ваша ставка', value=f'**{money} коинов**', inline=False)
                    embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**', inline=False)
                    message = await ctx.channel.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                cur.close()
                con.close()
            else:
                embed = discord.Embed(
                    title = 'Coinflip',
                    description = f'{ctx.message.author.mention}, вы сделали пустую ставку.',
                    color = discord.Color.orange()
                )
                message = await ctx.send(embed=embed)
                await asyncio.sleep(15)
                await message.delete()

    @commands.command()
    async def bonus(self, ctx):
        con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                        )
        cur = con.cursor()
        cur.execute(f"SELECT user_id, last_bonused FROM warns WHERE user_id='{ctx.message.author.id}'")
        selected = cur.fetchone()
        if selected == None:
            cur.execute(f"INSERT INTO warns (user_id, amount_of_warns, coins, colored_ticket, unique_ticket, last_bonused) VALUES ('{ctx.message.author.id}', 0, 0, 0, 0, 0)")
            con.commit()
            selected = [f'{ctx.message.author.id}', 0]
        if int(datetime.datetime.utcnow().strftime('%Y%m%d')) > selected[1]:
            coins = await self.get_coins(cur, str(ctx.message.author.id))
            await self.set_coins(cur, str(ctx.message.author.id), coins + 200)
            cur.execute(f"UPDATE warns SET last_bonused={int(datetime.datetime.utcnow().strftime('%Y%m%d'))} WHERE user_id='{ctx.message.author.id}'")
            con.commit()
            embed = discord.Embed(
                title = 'Ежедневный бонус',
                description = f'{ctx.message.author.mention}, вы получили **200 коинов** за ежедневный бонус.',
                color = discord.Color.orange()
            )
            await ctx.send(embed=embed)
            cur.close()
            con.close()
        else:
            embed = discord.Embed(
                title = 'Ежедневный бонус',
                description = f'{ctx.message.author.mention}, сегодня вы уже получили ежедневный бонус.',
                color = discord.Color.orange()
            )
            await ctx.send(embed=embed)
        cur.close()
        con.close()

    @commands.command()
    async def opencrate(self, ctx):
        if ctx.channel.id == 742047899856404522:
            embed = discord.Embed(
                title = 'Открытие кейсов',
                description = '''Для того чтобы открыть кейс вам необходимо иметь необходимое количество коинов и нажать на реакцию с номером кейса.
                
                1️⃣ **Маленький кейс: 100 коинов**
                2️⃣ **Средний кейс: 500 коинов**
                3️⃣ **Большой кейс: 2500 коинов**
                ''',
                color = discord.Color.orange()
            )
            message = await ctx.send(embed=embed)
            await message.add_reaction('1️⃣')
            await message.add_reaction('2️⃣')
            await message.add_reaction('3️⃣')
            self.opencrate_data = [message.id, ctx.message.author]
            await asyncio.sleep(20)
            await message.delete()

    @commands.command()
    async def buy_role(self, ctx, type_of_ticket, color: str, *, role_name=None):
        if ctx.channel.id == 742047899856404522:
            con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                        )
            cur = con.cursor()
            colored_ticket = await self.get_colored(cur, str(ctx.message.author.id))
            unique_ticket = await self.get_unique(cur, str(ctx.message.author.id))
            if type_of_ticket == 'colored':
                if colored_ticket >= 1:
                    if not (color.startswith('0x')):
                        color = '0x' + color
                    if len(color) > 8:
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'''
                            {ctx.message.author.mention}, вы ввели не верный цвет вторым аргументом.
                            
                            Используйте вторым аргументом:
                            `0xRRGGBB` или `RRGGBB`
                            ''',
                            color = discord.Color.orange()
                        )
                        message = await ctx.send(embed=embed)
                        await asyncio.sleep(15)
                        await message.delete()
                    else:
                        try:
                            hexed_color = int(color, 16)
                            right_hexed = True
                        except:
                            embed = discord.Embed(
                                title = 'Покупка роли',
                                description = f'''
                                {ctx.message.author.mention}, вы ввели не верный цвет вторым аргументом.
                                
                                Используйте вторым аргументом:
                                `0xRRGGBB` или `RRGGBB`
                                ''',
                                color = discord.Color.orange()
                            )
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()
                        if right_hexed:
                            right_hexed = None
                            await self.set_colored(cur, str(ctx.message.author.id), colored_ticket - 1)
                            con.commit()
                            for role in self.guild.roles:
                                if role.color == hexed_color:
                                    notFound = None
                                    created_role = role
                                    break
                            else:
                                notFound = True
                                counter = 0
                                for role in self.guild.roles:
                                    counter += 1

                            if notFound:
                                notFound = None
                                created_role = await self.guild.create_role(name='Colored', color=discord.Color(hexed_color))
                                created_role_position = {
                                    created_role: counter - 1
                                }
                                await self.guild.edit_role_positions(positions=created_role_position)
                            
                            for role in ctx.message.author.roles:
                                if role.name == 'Colored':
                                    await ctx.message.author.remove_roles(role)
                                    await role.delete()

                            await ctx.message.author.add_roles(created_role)
                            embed = discord.Embed(
                                title = 'Покупка роли',
                                description = f'{ctx.message.author.mention} преобрёл **цветовую роль {created_role.mention}**.',
                                color = discord.Color.orange()
                            )
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()
                else:
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description  = f'{ctx.message.author.mention}, у вас недостаточно билетов для покупки этой роли.',
                        color = discord.Color.orange()
                    )
                    embed.add_field(name='Билетов на цветовую роль:', value=f'**{colored_ticket} билетов**', inline=False)
                    embed.add_field(name='Билетов на уникальную роль:', value=f'**{unique_ticket} билетов**', inline=False)
                    message = await ctx.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
            elif type_of_ticket == 'unique':
                if unique_ticket >= 1:
                    try:
                        hexed_color = int(color, 16)
                        right_hexed = True
                    except:
                        embed = discord.Embed(
                            title = 'Покупка роли',
                            description = f'''
                            {ctx.message.author.mention}, вы ввели не верный цвет вторым аргументом.
                                
                            Используйте вторым аргументом:
                            `0xRRGGBB` или `RRGGBB`
                            ''',
                            color = discord.Color.orange()
                        )
                        message = await ctx.send(embed=embed)
                        await asyncio.sleep(15)
                        await message.delete()
                    if right_hexed:
                        right_hexed = None
                        if role_name != None:
                            role_name = '[У] ' + role_name
                            await self.set_unique(cur, str(ctx.message.author.id), unique_ticket - 1)
                            con.commit()
                            embed = discord.Embed(
                                title = 'Покупка роли',
                                description = f'{ctx.message.author.mention}, ваша заявка на создание уникальной роли **{role_name}** была отправлена на проверку модерации сервера.',
                                color = discord.Color.orange()
                            )
                            embed1 = discord.Embed(
                                description = f'{ctx.message.author.mention} подал заявку на создание уникальной роли **{role_name}**. Нажмите "✔" для одобрения заявки или "❌" для того, чтобы отклонить её.',
                                color = discord.Color.orange()
                            )
                            await ctx.send(embed=embed)
                            message = await self.log_channel.send(embed=embed1)
                            await message.add_reaction('✔')
                            await message.add_reaction('❌')
                            self.unique_role_data = [message.id, ctx.message.author, hexed_color, role_name]
                        else:
                            embed = discord.Embed(
                                title = 'Покупка роли',
                                description = f'''
                                {ctx.message.author.mention}, вы ввели не верное название роли третьим аргументом.
                                
                                Используйте третьим аргументом желаемое название вашей уникальной роли.
                                ''',
                                color = discord.Color.orange()
                            )
                            message = await ctx.send(embed=embed)
                            await asyncio.sleep(15)
                            await message.delete()

                else:
                    embed = discord.Embed(
                        title = 'Покупка роли',
                        description  = f'{ctx.message.author.mention}, у вас недостаточно билетов для покупки этой роли.',
                        color = discord.Color.orange()
                    )
                    embed.add_field(name='Билетов на цветовую роль:', value=f'**{colored_ticket} билетов**', inline=False)
                    embed.add_field(name='Билетов на уникальную роль:', value=f'**{unique_ticket} билетов**', inline=False)
                    message = await ctx.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
            else:
                embed = discord.Embed(
                    title = 'Покупка роли',
                    description = f'''
                    {ctx.message.author.mention}, вы ввели неверный тип роли первым аргументом.
                    
                    Используйте команду:
                    `!buy_role [colored или unique] [цвет в HEX]`
                    ''',
                    color = discord.Color.orange()
                )
                message = await ctx.send(embed=embed)
                await asyncio.sleep(15)
                await message.delete()
            cur.close()
            con.close()
                
    @commands.command()
    async def pay(self, ctx, member: discord.Member, value: int):  
        if ctx.channel.id == 742047899856404522:
            if ctx.message.author != member:
                if value > 0:
                    con = psycopg2.connect(
                                host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                                database = 'dfe269uifoco1o',
                                user = 'ncdnwynzrmqjnc',
                                password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                                port = 5432
                        )
                    cur = con.cursor()
                    coins = await self.get_coins(cur, str(ctx.message.author.id))
                    member_coins = await self.get_coins(cur, str(member.id))
                    if coins >= value:
                        await self.set_coins(cur, str(ctx.message.author.id), coins - value)
                        await self.set_coins(cur, str(member.id), member_coins + value)
                        con.commit()
                        embed = discord.Embed(
                            description = f'{ctx.message.author.mention} передал {member.mention} **{value} коинов**.',
                            color = discord.Color.orange()
                        )
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            description = f'{ctx.message.author.mention}, у вас недостаточно коинов для передачи.',
                            color = discord.Color.orange()
                        )
                        embed.add_field(name='Ваш баланс', value=f'**{coins} коинов**', inline=False)
                        embed.add_field(name='Попытка передать', value=f'**{value} коинов**', inline=False)
                        await ctx.send(embed=embed)
                    cur.close() 
                    con.close()
                else:
                    embed = discord.Embed(
                        description = f'{ctx.message.author.mention}, вы ввели пустое значение.',
                        color = discord.Color.orange()
                    )
                    message = await ctx.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
            else:
                embed = discord.Embed(
                    description = f'{ctx.message.author.mention}, вы не можете передавать самому себе коины.',
                    color = discord.Color.orange()
                )
                message = await ctx.send(embed=embed)
                await asyncio.sleep(15)
                await message.delete()

    @commands.command()
    async def text(self, ctx):
        need_roles = [[self.guild.get_role(747401276228108378), '100 камня'], [self.guild.get_role(747401227846942763), '50 угля, 30 железа, 15 красной пыли, 10 лазурита'], [self.guild.get_role(747401195248812053), '50 золота, 15 алмазов, 10 изумрудов, 5 незерита']]
        for role in need_roles:
            embed = discord.Embed(
                title = 'Покупка роли',
                description = f'Для того, чтобы преобрести билет вам нужно иметь необходимое количество ресурсов и нажать на реакцию под сообщением "✔".',
                color = discord.Color.orange()
            )
            embed.add_field(name='Роль', value=role[0].mention, inline=False)
            embed.add_field(name='Цена', value=f'**{role[1]}**', inline=False)
            message = await ctx.send(embed=embed)
            await message.add_reaction('✔')
            await message.add_reaction('❌')

    @commands.command()
    async def stats(self, ctx):
        if ctx.channel.id == 742047899856404522:
            con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                        )
            cur = con.cursor()
            coins = await self.get_coins(cur, str(ctx.message.author.id))
            colored_ticket = await self.get_colored(cur, str(ctx.message.author.id))
            unique_ticket = await self.get_unique(cur, str(ctx.message.author.id))
            warns = await self.get_warns(cur, str(ctx.message.author.id))
            ores = await self.get_ores(cur, str(ctx.message.author.id))
            embed = discord.Embed(
                title = 'Статистика',
                description = f'Статистика участника {ctx.message.author.mention}:',
                color = discord.Color.orange()
            )
            embed.add_field(name='Баланс: ', value=f'**{coins} коинов**', inline=False)
            embed.add_field(name='Билетов на цветовую роль:', value=f'**{colored_ticket} билетов**', inline=False)
            embed.add_field(name='Билетов на уникальную роль:', value=f'**{unique_ticket} билетов**', inline=False)
            embed.add_field(name='Предупреждений:', value=f'**{warns} предупреждений**', inline=False)
            embed.add_field(name='Руды:', value=f'''
            **Камень x{ores[9]}
            Уголь x{ores[0]}
            Лазурит x{ores[1]}
            Красная пыль x{ores[2]}
            Железо x{ores[3]}
            Золото x{ores[4]}
            Алмазы x{ores[5]}
            Изумруд x{ores[6]}
            Незерит x{ores[7]}**
            ''')
            await ctx.send(embed=embed)
            cur.close()
            con.close()

    @commands.command()
    @commands.has_any_role(671056120433082419, 668888227817586688, 742063102111252610, 742062992505569412)
    async def get_stats(self, ctx, member: discord.Member):
        con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                    )
        cur = con.cursor()
        coins = await self.get_coins(cur, str(member.id))
        colored_ticket = await self.get_colored(cur, str(member.id))
        unique_ticket = await self.get_unique(cur, str(member.id))
        warns = await self.get_warns(cur, str(member.id))
        ores = await self.get_ores(cur, str(member.id))
        embed = discord.Embed(
            description = f'Статистика участника {member.mention}:',
            color = discord.Color.orange()
        )
        embed.add_field(name='Баланс: ', value=f'**{coins} коинов**', inline=False)
        embed.add_field(name='Билетов на цветовую роль:', value=f'**{colored_ticket} билетов**', inline=False)
        embed.add_field(name='Билетов на уникальную роль:', value=f'**{unique_ticket} билетов**', inline=False)
        embed.add_field(name='Предупреждений:', value=f'**{warns} предупреждений**', inline=False)
        embed.add_field(name='Руды:', value=f'''
            **Камень x{ores[9]}
            Уголь x{ores[0]}
            Лазурит x{ores[1]}
            Красная пыль x{ores[2]}
            Железо x{ores[3]}
            Золото x{ores[4]}
            Алмазы x{ores[5]}
            Изумруд x{ores[6]}
            Незерит x{ores[7]}**
            ''')
        await self.log_channel.send(embed=embed)
        cur.close()
        con.close()

    @commands.command()
    @commands.has_any_role(671056120433082419, 668888227817586688)
    async def set_balance(self, ctx, member: discord.Member, coins: int):
        con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                    )
        cur = con.cursor()
        await self.set_coins(cur, str(member.id), coins)
        con.commit()
        embed = discord.Embed(
            description = f'Участнику {member.mention} было обновлено количество коинов',
            color = discord.Color.orange(),
            timestamp = datetime.datetime.utcnow()
        )
        embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
        embed.add_field(name='Количество коинов', value=f'**{coins} коинов**', inline=False)
        await self.log_channel.send(embed=embed)
        cur.close()
        con.close()

    @commands.command()
    @commands.has_any_role(671056120433082419, 668888227817586688)
    async def set_tickets(self, ctx, member: discord.Member, type_of_ticket, value: int):
        con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                    )
        cur = con.cursor()
        if type_of_ticket == 'colored':
            await self.set_colored(cur, str(member.id), value)
            con.commit()
            embed = discord.Embed(
            description = f'Участнику {member.mention} было обновлено количество билетов на цветовую роль.',
            color = discord.Color.orange(),
            timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            embed.add_field(name='Билетов на цветовую роль', value=f'**{value} билетов**', inline=False)
            await self.log_channel.send(embed=embed)
        elif type_of_ticket == 'unique':
            await self.set_unique(cur, str(member.id), value)
            con.commit()
            embed = discord.Embed(
                description = f'Участнику {member.mention} было обновлено количество билетов на уникальную роль.',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            embed.add_field(name='Билетов на уникальную роль', value=f'**{value} билетов**', inline=False)
            await self.log_channel.send(embed=embed)
        cur.close()
        con.close()

    @commands.command()
    @commands.has_any_role(671056120433082419, 668888227817586688)
    async def remove_role(self, ctx, member: discord.Member, type_of_role):
        if type_of_role == 'colored':
            for role in member.roles:
                if role.name == 'Colored':
                    await member.remove_roles(role)
                    await role.delete()
            embed = discord.Embed(
                description = f'Участнику {member.mention} было обнулено количество цветовых ролей.',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            await self.log_channel.send(embed=embed)
        elif type_of_role == 'unique':
            for role in member.roles:
                if '[У]' in role.name:
                    await member.remove_roles(role)
            embed = discord.Embed(
                description = f'Участнику {member.mention} было обнулено количество цветовых ролей.',
                color = discord.Color.orange(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
            await self.log_channel.send(embed=embed)

    @commands.command()
    async def mine(self, ctx):
        if ctx.channel.id == 742047899856404522:
            if not ctx.message.author in self.unavailable_to_mine:
                self.unavailable_to_mine.append(ctx.message.author)
                randomed_first_ore = random.randint(1, 100)
                randomed_second_ore = random.randint(1, 100)
                start_chance1 = 0
                start_chance2 = 0
                for ore in self.ore_dict[1]:
                    if randomed_first_ore >= start_chance1 and randomed_first_ore <= start_chance1 + ore[2]:
                        first_ore = ore
                    start_chance1 += (ore[2] + 1)
                for ore in self.ore_dict[2]:
                    if randomed_second_ore >= start_chance2 and randomed_second_ore <= start_chance2 + ore[2]:
                        second_ore = ore
                    start_chance2 += (ore[2] + 1)
                amount_of_first_ore = random.randint(3, 10)
                amount_of_second_ore = random.randint(1, 5)
                amount_of_stone = random.randint(10, 30)
                embed = discord.Embed(
                    title = 'Шахта',
                    description = f'''{ctx.message.author.mention} пошёл в шахту и добыл:
                    
                    **{self.ore_dict[0][0]}** x{amount_of_stone}
                    **{first_ore[0]}** x{amount_of_first_ore}
                    **{second_ore[0]}** x{amount_of_second_ore}

                    Для быстрой продажы ресурсов нажмите на рекцию "✔" под этим сообщением, чтобы оставить их у себя в инвентаре - "❌".
                    ''',
                    color = discord.Color.orange()
                )
                message = await ctx.send(embed=embed)
                await message.add_reaction('✔')
                await message.add_reaction('❌')
                self.mine_data = [message, ctx.message.author.id, [self.ore_dict[0], amount_of_stone], [first_ore, amount_of_first_ore], [second_ore, amount_of_second_ore]]
                await asyncio.sleep(30)
                try:
                    message = self.mine_data[0]
                    stone = self.mine_data[2]
                    first_ore = self.mine_data[3]
                    second_ore = self.mine_data[4]
                    con = psycopg2.connect(
                        host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                        database = 'dfe269uifoco1o',
                        user = 'ncdnwynzrmqjnc',
                        password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                        port = 5432
                    )
                    cur = con.cursor()
                    await message.delete()
                    if await self.get_ores(cur, str(self.mine_data[1])) != None:
                        cur.execute(f"SELECT {stone[0][2]}, {first_ore[0][3]}, {second_ore[0][3]} FROM mine WHERE user_id='{self.mine_data[1]}'")
                        selected = cur.fetchone()
                        cur.execute(f"UPDATE mine SET {stone[0][2]}={(selected[0] + stone[1])}, {first_ore[0][3]} = {(selected[1] + first_ore[1])}, {second_ore[0][3]} = {(selected[2] + second_ore[1])} WHERE user_id='{self.mine_data[1]}'")
                        con.commit()
                    cur.close()
                    con.close()
                except:
                    pass
                if self.guild.get_role(747401195248812053) in ctx.message.author.roles:
                    await asyncio.sleep(3600)
                    self.unavailable_to_mine.remove(ctx.message.author)
                elif self.guild.get_role(747401227846942763) in ctx.message.author.roles:
                    await asyncio.sleep(7200)
                    self.unavailable_to_mine.remove(ctx.message.author)
                elif self.guild.get_role(747401276228108378) in ctx.message.author.roles:
                    await asyncio.sleep(10800)
                    self.unavailable_to_mine.remove(ctx.message.author)
                else:
                    await asyncio.sleep(14400)
                    self.unavailable_to_mine.remove(ctx.message.author)
            else:
                embed = discord.Embed(
                    title = 'Шахта',
                    description = f'{ctx.message.author.mention}, с момента последнего похода в шахту ещё не прошло необходимое время.',
                    color = discord.Color.orange()
                )
                await ctx.send(embed=embed)

    @commands.command()
    async def sell(self, ctx, type_of_ore):
        if ctx.channel.id == 742047899856404522:
            if type_of_ore == 'all' or type_of_ore == 'stone' or type_of_ore == 'coal' or type_of_ore == 'lapis' or type_of_ore == 'redstone' or type_of_ore == 'iron' or type_of_ore == 'gold' or type_of_ore == 'diamond' or type_of_ore == 'emerald' or type_of_ore == 'netherite':
                arr_of_ores = {
                    'stone': 2,
                    'coal': 5,
                    'lapis': 12,
                    'redstone': 10,
                    'iron': 7,
                    'gold': 60,
                    'diamond': 125,
                    'emerald': 150,
                    'netherite': 200
                } 
                user_id = ctx.message.author.id
                con = psycopg2.connect(
                    host = 'ec2-54-75-248-49.eu-west-1.compute.amazonaws.com',
                    database = 'dfe269uifoco1o',
                    user = 'ncdnwynzrmqjnc',
                    password = '294aa60ea254f2734b3ba6ed1c079f003d24e6e121ed385e12217feda5c018ce',
                    port = 5432
                )
                cur = con.cursor()
                necessary_coins = 0
                if await self.get_ores(cur, str(user_id)) != None:
                    if type_of_ore == 'all':
                        for resource in arr_of_ores:
                            cur.execute(f"SELECT {resource} FROM mine WHERE user_id='{user_id}'")
                            selected = cur.fetchone()
                            necessary_coins += (selected[0] * arr_of_ores[resource])
                            cur.execute(f"UPDATE mine SET {resource} = 0 WHERE user_id='{user_id}'")
                            con.commit()
                    else:
                        cur.execute(f"SELECT {type_of_ore} FROM mine WHERE user_id='{user_id}'")
                        selected = cur.fetchone()
                        necessary_coins += (selected[0] * arr_of_ores[type_of_ore])
                        cur.execute(f"UPDATE mine SET {type_of_ore} = 0 WHERE user_id='{user_id}'")
                        con.commit()
                coins = await self.get_coins(cur, str(user_id))
                await self.set_coins(cur, str(user_id), coins + necessary_coins)
                con.commit()
                if necessary_coins != 0:
                    embed = discord.Embed(
                        title = 'Шахта',
                        description = f'{ctx.message.author.mention}, вы успешно продали ресурсы на сумму **{necessary_coins} коинов**.',
                        color = discord.Color.orange()
                    )
                    message = await ctx.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()
                else:
                    embed = discord.Embed(
                        title = 'Шахта',
                        description = f'{ctx.message.author.mention}, у вас нет необходимых ресурсов для продажи.',
                        color = discord.Color.orange()
                    )
                    message = await ctx.send(embed=embed)
                    await asyncio.sleep(15)
                    await message.delete()

def setup(bot):
    bot.add_cog(Coinsbot(bot))