##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

from discord.app_commands.transformers import CHANNEL_TO_TYPES
import os
import discord
from discord.ext import commands
import json

from keep_alive import keep_alive


#__________________________________________________#
## variables globales ##
#__________________________________________________#

# Params du Bot

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=prefix, intents=intents)
botId = 
token = ""

# IDs
adminRole = ""
RW_authorizedRoleID = 
R_authorizedRoleID = 

# Messages
helpMSG = msg = """Les commandes sont:
    
    **Accès des données en lecture** (`Bot's contact`)
    `!help`: affiche les commandes;
    
    **Accès des données en écriture** (`Bot's friend`)
    """


#__________________________________________________#
## Fonctions ##
#__________________________________________________#



# ERROR HANDLER
# error sender
async def error(channel, errorMsg:str):
  await channel.send(errorMsg)

# length verification
async def lengthVerificator(message:str, command:str):
  if len(message.content.split(" ")) == len(command.content.split(" ")): return True
  else: await error(message.channel, "Peu ou trop d'arguments ont été donnés:`"+command+"`")




# DISCORD EVENT RESPONSE
# !help
# affiche les commandes
async def help(message):
  global helpMSG
  await message.delete()
  await message.channel.send(helpMSG)

# !printPlayer <joueur>
# affiche les données d'un joueur
async def printPlayer(message):
  await message.delete()
  if lengthVerificator(message, "!printPlayer <joueur>"):
    data = loadData()
    await db.printPlayer(message.content.split(" ")[1])







#__________________________________________________#
## Event Handler ##
#__________________________________________________#


# Login Section
@bot.event
async def on_ready():
  print('Bot is ready.')  # le bot est prêt


# Message Section
@bot.event
async def on_message(message):
  user = message.author
  aut_id = 0
  
  if message.content.startswith("!"):
    if user.get_role(R_authorizedRoleID) is not None:
      aut_id = 1
      print("accès en lecture")
    if user.get_role(RW_authorizedRoleID) is not None:
      aut_id = 2
      print("accès en écriture")

  
  if aut_id >= 1 and message.content.startswith("!help"): await help(message) # affiche les commandes. !help
  elif aut_id >= 1 and message.content.startswith("!printplayer "): await printPlayer(message) # imprime les données d'une joueur. !printPlayer <joueur>
  elif message.content.startswith("!"): await error(message.channel, "Commande inconnue ou vous ne possédez pas les permissions nécessaires. `!help` pour voir la liste des commandes disponibles.") #error
  else: pass #usual message



#__________________________________________________#
## Run ##
#__________________________________________________#

#On va maintenir le bot en acitivité
keep_alive()
#On lance le bot
bot.run(token)
