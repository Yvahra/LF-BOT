##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import os
from datetime import datetime

import discord
from discord.ext import commands

import floods
import functions as f
from dotenv import load_dotenv
from datetime import date, timedelta



import convois

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

# Params du Bot
load_dotenv()

intents = discord.Intents.all()
client = discord.Client(intents=intents)
prefix = "$"
bot = commands.Bot(command_prefix=prefix, intents=intents)
token = str(os.getenv("BOT_TOKEN"))

async def error(channel, errorMsg: str):
  await channel.send(errorMsg)

async def recapRSS():
    channel = bot.get_channel(1276232505116196894)
    msg = convois.repartitionRessources((date.today()- timedelta(days=1)).strftime("%Y-%m-%d"))
    if msg.startswith("ERR:"):
        f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    else:
      for m in f.splitMessage(msg):
        await channel.send(m)

async def recapConvois():
    channel = bot.get_channel(1278074306391183452)
    msg = convois.convoisDuJour((date.today()- timedelta(days=1)).strftime("%Y-%m-%d"))
    if msg.startswith("ERR:"):
        f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    else:
        for m in f.splitMessage(msg):
            await channel.send(m)

async def recapFlood():
    channel = bot.get_channel(1276451985352294440)
    msg = floods.printFloodsFuturs()
    if msg.startswith("ERR:"):
        f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    else:
        for m in f.splitMessage(msg):
            await channel.send(m)

# Login Section
@bot.event
async def on_ready():
  await recapRSS()  # le bot est prêt
  await recapConvois()
  await recapFlood()
  exit()

bot.run(token)