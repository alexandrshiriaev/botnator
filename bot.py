# BOT WAS CREATED BY ALEXANDER SHIRIAEV

import discord
import datetime

from discord.ext import commands
TOKEN = 'NzQxNjE4MzA4ODg0NzI1ODQw.Xy6L3w.UlGJIEwQ_Y49t-dqAWsLrWuXwLU'
client = commands.Bot(command_prefix='!')
client.remove_command('help')

help_commands = None

@client.event
async def on_ready():
    print('Bot is ready!')


@client.command()
async def help(ctx, necessary_command=None):
    guild = client.get_guild(660793084703145985)
    report_channel = guild.get_channel(671399645578264606)
    suggestion_channel = guild.get_channel(743746501817401346)
    help_commands = {
    'Основные': {
        '!help': 'С помощью этой команды вы сможете посмотреть информацию о всех существующих командах этого бота.',
        '!ticket': f'''Данную команду можно использовать только в {report_channel.mention}. 
        
        Используйте команду для подачи жалобы на модерацию:
        `!ticket @moderator text`, где `@moderator` - упоминание модератора, а `text` - текст жалобы.
        ''',
        '!suggestion': f'''Данную команду можно использовать только в {suggestion_channel.mention}.

        Используйте команду для подачи предложения по улучшению:
        `!suggestion text`, где `text` - текст вашей идеи.
        '''},
    'Coins': {
        '!flip': '''С помощью данной команды вы сможете играть в **Coinflip**.
        
        Используйте команду для игры на определённую ставку:
        `!flip money [@mention]`, где `money` - ваша ставка, `[@mention]` - необязательный аргумент, упомяните кого-то, если вы хотите с ним сыграть в **Coinflip**.
        ''',
        '!opencrate': 'Используйте данную команду для открытия кейсов.',
        '!buy_role': '''Данная команда позволяет купить вам уникальную или цветовую роль, использую билет.
        
        Используйте команду:
        `!buy_role colored/unique color [name]`, где `colored` - использование билета для цветовой роли, а `unique` - для уникальной, `color` - HEX-цвет типа 0xRRGGBB или RRGGBB, `[name]` - обязательный аргумент, если вы выбрали первым аргументом `unique`, название вашей уникальной роли.
        ''',
        '!mine': 'С помощью данной команды вы сможете отправиться в шахту и добыть ресурсы, которые в дальнейшем сможете продать или обменять на роли.',
        '!sell': '''С помощью данной команды вы можете продать определённые ресурсы.
        
        Используйте команду для продажи:
        `!sell all/stone/coal/lapis/redstone/iron/gold/diamond/emerald/netherite`, где `all` - продать все ресурсы, а `stone/coal/lapis/redstone/iron/gold/diamond/emerald/netherite` - продать камень, уголь, лазурит, красную пыль, железо, золото, алмазы, изумруды или незерит соответственно.
        '''
        }
    }
    if necessary_command == None:
        output = ''
        embed = discord.Embed(
            title = 'Список команд',
            description = 'Здесь перечислен список всех существующих команд. Для того, чтобы получить более подробную информацию о какой либо команде пропишите `!help` и название команды без `!`.',
            color = discord.Color.orange()
        )
        for command_type in help_commands:
            for command in help_commands[command_type]:
                output += (command + ' ')
            else:
                embed.add_field(name=command_type, value=f'`{output.strip()}`', inline=False)
                output = ''
        await ctx.send(embed=embed)
    else:
        for command_type in help_commands:
            for command in help_commands[command_type]:
                if necessary_command == command.replace('!', ''):
                    embed = discord.Embed(
                        title = command,
                        description = help_commands[command_type][command],
                        color = discord.Color.orange()
                    )
                    await ctx.send(embed=embed)
    
client.load_extension('cogs.moderation')
client.load_extension('cogs.coinsbot')
client.run(TOKEN)


