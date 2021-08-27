from discord.ext import commands
from datetime import datetime
from discord.utils import get
from discord.ext.commands import cog
from discord import Forbidden
import subprocess
import threading
import aiofiles
import aiosqlite
import discord
import asyncio
import aiohttp
import random
import ctypes
import re
import os

ctypes.windll.kernel32.SetConsoleTitleW('tfollow')
token = ''
prefix = '/'
ROLE = "Member"

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')
bot.warnings = {} # guild_id : {member_id: [count, [(admin_id, reason)]]}

administrators = [put ur id]
chat_channel = put ur channel id
bots_channel = put ur channel id
queue = []

def zoom():
    while True:
        try:
            task, arg1, arg2 = queue.pop(0).split('-')
            subprocess.run([f'{task}', f'{arg1}', f'{arg2}'])
        except:
            pass

threading.Thread(target=zoom).start()

@bot.event
async def on_ready():
    print(f'Servers: {len(bot.guilds)}')
    for guild in bot.guilds:
        print(guild.name)
    print()
    
    for guild in bot.guilds:
        bot.warnings[guild.id] = {}
        
        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass

        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]
        members = sum([guild.member_count for guild in bot.guilds])
        activity = discord.Activity(type=discord.ActivityType.watching, name=f'{members} users!')
        await bot.change_presence(activity=activity)
        await asyncio.sleep(60)

@bot.event
async def on_member_join(member):
    channel = await bot.fetch_channel(bots_channel)
    await channel.send(f'Welcome to **Twitch Followers**, {member.mention}.\nType `/help` to get started!')
    role = get(member.guild.roles, name=ROLE)
    await member.add_roles(role)
    print(f"{member} was given {role}")



@bot.event
async def on_command_error(ctx, error: Exception):
    if ctx.channel.id == bots_channel:
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(color=16379747, description=f'{error}')
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=16379747, description='You are missing arguments required to run this command!')
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
        elif 'You do not own this bot.' in str(error):
            embed = discord.Embed(color=16379747, description='You do not have permission to run this command!')
            await ctx.send(embed=embed)
        else:
            print(str(error))
    else:
        try:
            await ctx.message.delete()
        except:
            pass

@bot.command()
async def help(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /help')
    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(color=16379747)
        embed.add_field(name='Help', value='`/help`', inline=True)
        embed.add_field(name='Open Ticket', value='`/ticket`', inline=True)
        embed.add_field(name='Close Ticket', value='`/close`', inline=True)
        embed.add_field(name='Tasks', value='`/tasks`', inline=True)
        embed.add_field(name='Twitch Followers', value='`/tfollow (channel)`', inline=True)
        embed.add_field(name='⭐ Twitch Spam', value='`/tspam (channel) (message)`', inline=True)
        embed.add_field(name='Staff Help', value='`/helpstaff`', inline=True)
        embed.add_field(name='Donate', value='`/donate`', inline=True)
        embed.add_field(name='Shop / Store', value='`/store`', inline=True)
        await ctx.send(embed=embed)

@bot.command()
async def helpstaff (ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /helpstaff')
    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(color=16379747)
        embed.add_field(name='Help', value='`/help`', inline=True)
        embed.add_field(name='Ban (Staff only)', value='`/ban (user) (reason)`', inline=True)
        embed.add_field(name='Purge (Staff only)', value='`/purge (amount)`', inline=True)
        embed.add_field(name='Warn (Staff only)', value='`/warn (user) (reason)`', inline=True)
        embed.add_field(name='Warnings (Staff only)', value='`/warnings (user)`', inline=True)
        embed.add_field(name='Channel lockdown (Staff only)', value='`/lock`', inline=True)
        embed.add_field(name='Channel Unlock (Staff only)', value='`/unlock`', inline=True)
        await ctx.send(embed=embed)

@bot.command()
async def ticket(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /ticket')
    if ctx.channel.type != discord.ChannelType.private:
        channels = [str(x) for x in bot.get_all_channels()]
        if f'ticket-{ctx.author.id}' in str(channels):
            embed = discord.Embed(color=16379747, description='You already have a ticket open!')
            await ctx.send(embed=embed)
        else:
            ticket_channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.id}')
            await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)
            await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
            embed = discord.Embed(color=16379747, description='Please enter the reason for this ticket, type `/close` if you want to close this ticket.')
            await ticket_channel.send(f'{ctx.author.mention}', embed=embed)
            await ctx.message.delete()

@bot.command()
async def close(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /close')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.name == f'ticket-{ctx.author.id}':
            await ctx.channel.delete()
        elif ctx.author.id in administrators and 'ticket' in ctx.channel.name:
            await ctx.channel.delete()
        else:
            embed = discord.Embed(color=16379747, description=f'You do not have permission to run this command!')
            await ctx.send(embed=embed)

@bot.command()
async def tasks(ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /tasks')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            embed = discord.Embed(color=16379747, description=f'`{len(queue)}` tasks in the queue!')
            await ctx.send(embed=embed)
        else:
            await ctx.message.delete()

tfollow_cooldown = []

@bot.command()
@commands.cooldown(1, 300, type=commands.BucketType.user)
async def tfollow(ctx, channel, amount: int=None):
    print(f'{ctx.author} | {ctx.author.id} -> /tfollow {channel}')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel or ctx.author.id in administrators:
            if str(channel.lower()) in tfollow_cooldown and ctx.author.id not in administrators:
                try:
                    await ctx.message.delete()
                except:
                    pass
            else:
                try:
                    if '-' in str(channel):
                        raise Exception
                    max_amount = 0
                    if ctx.author.id in administrators:
                        tfollow.reset_cooldown(ctx)
                        max_amount += 0
                    premium = discord.utils.get(ctx.guild.roles, name='Premium')
                    if premium in ctx.author.roles:
                        max_amount += 10000
                    diamond = discord.utils.get(ctx.guild.roles, name='Diamond')
                    if diamond in ctx.author.roles:
                        max_amount += 7550
                    gold = discord.utils.get(ctx.guild.roles, name='Gold')
                    if gold in ctx.author.roles:
                        max_amount += 2500
                    silver = discord.utils.get(ctx.guild.roles, name='Silver')
                    if silver in ctx.author.roles:
                        max_amount += 1000
                    bronze = discord.utils.get(ctx.guild.roles, name='Bronze')
                    if bronze in ctx.author.roles:
                        max_amount += 150
                    booster = discord.utils.get(ctx.guild.roles, name='Booster')
                    if booster in ctx.author.roles:
                        max_amount += 12500
                    _75 = discord.utils.get(ctx.guild.roles, name='+75')
                    if _75 in ctx.author.roles:
                        max_amount += 75
                    _25 = discord.utils.get(ctx.guild.roles, name='+25')
                    if _25 in ctx.author.roles:
                        max_amount += 25
                    _10 = discord.utils.get(ctx.guild.roles, name='+10')
                    if _10 in ctx.author.roles:
                        max_amount += 10
                    _5 = discord.utils.get(ctx.guild.roles, name='+5')
                    if _5 in ctx.author.roles:
                        max_amount += 5
                    max_amount += 125
                    if amount is None:
                        amount = max_amount
                    elif amount > max_amount:
                        amount = max_amount
                    if amount <= max_amount:
                        premium = discord.utils.get(ctx.guild.roles, name='Premium')
                        if premium in ctx.author.roles:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`1/{position}`)')
                            embed = discord.Embed(color=16379747, description=f'Adding `{amount}` followers to `{channel}`! (`1/{position}`)')
                            await ctx.send(embed=embed)
                            queue.insert(0, f'tfollow-{channel}-{amount}')
                        else:
                            position = len(queue) + 1
                            # embed = discord.Embed(color=16379747, description=f'Added `tfollow-{channel}-{amount}` to queue! (`{position}/{position}`)')
                            embed = discord.Embed(color=16379747, description=f'Adding `{amount}` followers to `{channel}`! (`{position}/{position}`)')
                            await ctx.send(embed=embed)
                            queue.append(f'tfollow-{channel}-{amount}')
                        if ctx.author.id not in administrators:
                            tfollow_cooldown.append(str(channel.lower()))
                            await asyncio.sleep(300)
                            tfollow_cooldown.remove(str(channel.lower()))
                except:
                    embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed)
                    tfollow.reset_cooldown(ctx)
        else:
            await ctx.message.delete()
            tfollow.reset_cooldown(ctx)

@bot.command()
@commands.cooldown(1, 300, type=commands.BucketType.user)
async def tspam(ctx, channel, *, msg):
    print(f'{ctx.author} | {ctx.author.id} -> /tspam {channel} {msg}')
    if ctx.channel.type != discord.ChannelType.private:
        premium = discord.utils.get(ctx.guild.roles, name='Premium')
        if premium in ctx.author.roles:
            if ctx.channel.id == bots_channel:
                try:
                    max_amount = 0
                    if ctx.author.id in administrators:
                        tspam.reset_cooldown(ctx)
                    max_amount += 125
                    amount = None
                    if amount is None:
                        amount = max_amount
                    if amount <= max_amount:
                        position = len(queue) + 1
                        embed = discord.Embed(color=16379747, description=f'Added `tspam-{channel}-{msg}` to queue! (`1/{position}`)')
                        await ctx.send(embed=embed)
                        queue.insert(0, f'tspam-{channel}-{msg}')
                except:
                    embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed)
                    tspam.reset_cooldown(ctx)
            else:
                await ctx.message.delete()
                tspam.reset_cooldown(ctx)
        else:
            embed = discord.Embed(color=16379747, description='You do not have permission to run this command! You need Premium for this!')
            await ctx.send(embed=embed)

rfollow_cooldown = []

@bot.command()
@commands.cooldown(1, 300, type=commands.BucketType.user)
async def rfollow(ctx, user_id, amount: int=None):
    print(f'{ctx.author} | {ctx.author.id} -> /rfollow {user_id}')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel or ctx.author.id in administrators:
            if str(user_id) in rfollow_cooldown and ctx.author.id not in administrators:
                try:
                    await ctx.message.delete()
                except:
                    pass
            else:
                try:
                    int(user_id)
                    max_amount = 0
                    if ctx.author.id in administrators:
                        rfollow.reset_cooldown(ctx)
                        max_amount += 5000
                    max_amount += 125
                    if amount is None:
                        amount = max_amount
                    elif amount > max_amount:
                        amount = max_amount
                    if amount <= max_amount:
                        premium = discord.utils.get(ctx.guild.roles, name='Premium')
                        if premium in ctx.author.roles:
                            position = len(queue) + 1
                            embed = discord.Embed(color=16379747, description=f'Adding `{amount}` followers to `{user_id}`! (`1/{position}`)')
                            await ctx.send(embed=embed)
                            queue.insert(0, f'rfollow-{user_id}-{amount}')
                        else:
                            position = len(queue) + 1
                            embed = discord.Embed(color=16379747, description=f'Adding `{amount}` followers to `{user_id}`! (`{position}/{position}`)')
                            await ctx.send(embed=embed)
                            queue.append(f'rfollow-{user_id}-{amount}')
                        if ctx.author.id not in administrators:
                            rfollow_cooldown.append(str(user_id))
                            await asyncio.sleep(300)
                            rfollow_cooldown.remove(str(user_id))
                except:
                    embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                    await ctx.send(embed=embed)
                    rfollow.reset_cooldown(ctx)
        else:
            await ctx.message.delete()
            rfollow.reset_cooldown(ctx)

@bot.command()
async def rget(ctx, asset_id):
    print(f'{ctx.author} | {ctx.author.id} -> /rget {asset_id}')
    if ctx.channel.type != discord.ChannelType.private:
        if ctx.channel.id == bots_channel:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}') as r:
                        r = await r.text()
                    async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id=' + re.search('id=(.*)</url>', r).group(1)) as r:
                        r = await r.read()
                try:
                    f = await aiofiles.open(f'{asset_id}.png', mode='wb')
                    await f.write(r)
                    await f.close()
                    embed = discord.Embed(color=16379747)
                    file = discord.File(f'{asset_id}.png')
                    embed.set_image(url=f'attachment://{asset_id}.png')
                    await ctx.send(embed=embed, file=file)
                finally:
                    try:
                        os.remove(f'{asset_id}.png')
                    except:
                        pass
            except:
                embed = discord.Embed(color=16379747, description='An error has occured while attempting to run this command!')
                await ctx.send(embed=embed)
        else:
            await ctx.message.delete()

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.message.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await asyncio.sleep(1)
        await ctx.send(f"Banned {member}, Reason: {reason}")
    else:
        await ctx.send(f"{ctx.message.author} - You dont have permission to that command!")
        await asyncio.sleep(3)

@bot.command(name='purge')
async def purge(ctx, amount, arg:str=None):
    if ctx.message.author.guild_permissions.manage_messages:
        await ctx.message.delete()
        await ctx.channel.purge(limit=int(amount))
        mesage_to_delete = await ctx.send(f'{amount} messages have been deleted!')
        await asyncio.sleep(1)  

@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}




@bot.command()
@commands.has_permissions(ban_members=True)
async def warn(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one.")
        
    if reason is None:
        return await ctx.send("Please provide a reason for warning this user.")

    try:
        first_warning = False
        bot.warnings[ctx.guild.id][member.id][0] += 1
        bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

    count = bot.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def warnings(ctx, member: discord.Member=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one.")
    
    embed = discord.Embed(title=f"Displaying Warnings for {member.name}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {i}** given by: {admin.mention} for: *'{reason}'*.\n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError: # no warnings
        await ctx.send("This user has no warnings.")

@bot.command()
@commands.has_permissions(manage_channels = True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send( ctx.channel.mention + " is now in lockdown.")

@bot.command()
@commands.has_permissions(manage_channels = True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send( ctx.channel.mention + " is now unlocked.")

@bot.command()
async def donate(ctx):
    await ctx.send("Click on this link to donate! https://www.paypal.com/donate?hosted_button_id=TTBMZ2UHTB9AY")

@bot.command()
async def english(ctx):
    await ctx.send("Speak English or gay🏳️‍🌈 ")

@bot.command()
@commands.has_permissions(manage_channels = True)
async def eventstart (ctx):
    print(f'{ctx.author} | {ctx.author.id} -> /eventstart')
    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(color=16379747)
        embed.add_field(name='NEW EVENT', value='`5 New Invites = Gold,              10 New Invites = Diamond!`', inline=True)
        embed.add_field(name='/ticket', value='`Please make a ticket to claim ur role!`', inline=True)
        await ctx.send(embed=embed)

@bot.command()
async def store(ctx):
    await ctx.send("https://shoppy.gg/@Twitch_Followers")

@bot.command()
async def shop(ctx):
    await ctx.send("https://shoppy.gg/@Twitch_Followers")

@bot.command()
async def hi(ctx):
    await ctx.send("Hi daddy!")

bot.run(token)
