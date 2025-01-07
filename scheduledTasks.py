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
from datetime import date, datetime, timedelta



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
    # channel = bot.get_channel(1276232505116196894)
    # msg = convois.repartitionRessources((date.today()- timedelta(days=1)).strftime("%Y-%m-%d"))
    # msg+= "\n||from cron||"
    # if msg.startswith("ERR:"):
    #     f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    # else:
    #   for m in f.splitMessage(msg):
    #     await channel.send(m)

    msg = convois.repartitionRessources((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"))

    channel= bot.get_channel(1326174754272710737)
    msgDiscord= await channel.fetch_message(1326179817506340945)
    await msgDiscord.edit(content=msg)



async def recapConvois():
    # channel = bot.get_channel(1278074306391183452)
    # msg = convois.convoisDuJour((date.today()- timedelta(days=1)).strftime("%Y-%m-%d"))
    # msg+= "\n||from cron||"
    # if msg.startswith("ERR:"):
    #     f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    # else:
    #     for m in f.splitMessage(msg):
    #         await channel.send(m)

    pass

async def recapFlood():
    # channel = bot.get_channel(1276451985352294440)
    # msg = floods.printFloodsFuturs()
    # msg+= "\n||from cron||"
    # if msg.startswith("ERR:"):
    #     f.log(rank=1, prefixe="[ERROR]", message=msg, suffixe="")
    # else:
    #     for m in f.splitMessage(msg):
    #         await channel.send(m)
    msg = floods.printFloodsFuturs()

    channel = bot.get_channel(1326174677231603713)
    msgDiscord = await channel.fetch_message(1326179787844227175)
    await msgDiscord.edit(content=msg)


import os
import shutil
import time
from datetime import datetime, timedelta

def sauvegarder_fichiers(source_dir, destination_dir):
    date= datetime.now()- timedelta(days=1)
    datename= date.strftime("%Y-%m-%d")
    destination_dir+= "/"+datename
    # Vérifie si le dossier de destination existe, sinon le crée
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Déplace les fichiers du dossier source vers le dossier de destination
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        destination_file = os.path.join(destination_dir, filename)

        shutil.copytree(source_file, destination_file)
        print(f"Dossier {filename} sauvegardé dans {destination_dir}")

def supprimer_anciens_fichiers(destination_dir, age_jours=30):
    # Détermine la date limite (aujourd'hui - 30 jours)
    date = datetime.now() - timedelta(days=age_jours)
    datename = date.strftime("%Y-%m-%d")
    destination_dir += "/" + datename

    # Parcourt les fichiers dans le dossier de destination
    if os.path.exists(destination_dir):
        for filename in os.listdir(destination_dir):
            fichier = os.path.join(destination_dir, filename)

        # Vérifie si c'est un fichier
            if os.path.isfile(fichier):
                os.remove(fichier)
                print(f"Fichier {filename} supprimé (ancien de plus de {age_jours} jours)")
        os.rmdir(destination_dir)
        print(f"Dossier {destination_dir} supprimé (ancien de plus de {age_jours} jours)")



# Login Section
@bot.event
async def on_ready():
    await recapRSS()  # le bot est prêt
    # await recapConvois()
    await recapFlood()

    try:
        source_dir = '/home/yavhra/GIT/LF-BOT/JSON'
        destination_dir = '/home/yavhra/Archives/LF-BOT'

        sauvegarder_fichiers(source_dir, destination_dir)
        supprimer_anciens_fichiers(destination_dir, age_jours=30)
    except:
        pass

    await bot.logout()

bot.run(token)