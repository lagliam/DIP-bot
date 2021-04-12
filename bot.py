# bot.py
# Author: Liam Goring Apr 2021
# TODO restart running tasks on program restart

import os
import random
import asyncio
import discord
import glob

from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
LIMIT_SIZE = 8000000 # 8MB limit
TRIGGER_DURATION = 86400/2 # task runs twice a day (86400 / 2 seconds)
RUNNING_FILE_POLL_INTERVAL = 2 # every (x) seconds 

@bot.command(name='uWu')
async def startPosting(ctx):
    guildId = ctx.channel.guild.id
    runningFile = f'guilds/{guildId}.running'
    if os.path.exists(runningFile):
        os.remove(runningFile)
        return
    else: 
        open(runningFile, 'a').close()

    print(f'started posting for server {guildId}')
    await ctx.send('AraAra~ Here some pics for you')
    counter = 0
    seenImages = fileToArray(f'guilds/images_{guildId}.txt')
    
    while counter < len(imageList()) and os.path.exists(runningFile):
        fileList = imageList()
        counter += 1
        filename = fileList.pop(random.randrange(len(fileList)))
        if os.path.getsize('images/'+filename) > LIMIT_SIZE:
            filename = fileList.pop(random.randrange(len(fileList)))
        while filename in seenImages:
            filename = fileList.pop(random.randrange(len(fileList)))
        await ctx.send('', file=discord.File('images/'+filename))
        writeViewedImageListForGuild(filename, guildId)
        startWaiting = 0
        while startWaiting < TRIGGER_DURATION and os.path.exists(runningFile):
            await asyncio.sleep(RUNNING_FILE_POLL_INTERVAL)
            startWaiting += 1
    await ctx.send('(o･｀Д´･o) Baka!')
    print(f'Ending posting for {guildId}')

@bot.event
async def on_ready():
    print(f'Onii-chan! {bot.user.name} has connected to Discord! 0w0')

def imageList():
    directory = 'images'
    imageList = []
    for filename in os.listdir(directory):
        if (filename.lower().endswith(".jpg") 
        or filename.lower().endswith(".png")
        or filename.lower().endswith(".gif")
        or filename.lower().endswith(".jpeg")):
            imageList.append(filename)
            continue
        else:
            continue
    return imageList

def writeViewedImageListForGuild(filename, guildId=None):
    with open(f'guilds/images_{guildId}.txt', 'a+') as f:
        f.write("%s\n" % filename)

def fileToArray(filename):
    array = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            array = f.readlines()
    return array

bot.run(TOKEN)
