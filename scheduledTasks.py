##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import os
import discord
from discord.ext import commands

import functions as f
from dotenv import load_dotenv



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

async def recapRSS(message):
    channel = bot.get_channel(1276232505116196894)
    msg = convois.repartitionRessources()
    if msg.startswith("ERR:"):
      await error(channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)

# Login Section
@bot.event
async def on_ready():
  print('Bot is ready.')  # le bot est prêt

bot.run(token)