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
from datetime import datetime

from keep_alive import keep_alive
import db_handler_getters as dbg
import db_handler_functions as dbf
import functions as f
from dotenv import load_dotenv



import alliance
import chasses
import convois
import floods
import joueurs
import pactes

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

H_CHASSE_FILENAME = "HIST//Historique_Chasses.json"
H_FLOODS_FILENAME = "HIST//Historique_FloodsExternes.json"
H_PACTE_FILENAME = "HIST//Historique_Pactes.json"
H_CONVOIS_EXTERNES_FILENAME = "HIST//Historique_ConvoisExternes.json"

S_ALLIANCE_FILENAME = "STATS//Stats_Alliance.json"
S_CONVOIS_FILENAME = "STATS//Stats_ConvoisEnCours.json"
S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"
S_FLOODS_FILENAME = "STATS//Stats_FloodsFuturs.json"

CONST_TEMPLATES = "CONST//CONST_Templates.json"
CONST_DISCORD = "CONST//CONST_Discord.json"

# Params du Bot
load_dotenv()

intents = discord.Intents.all()
client = discord.Client(intents=intents)
prefix = "$"
bot = commands.Bot(command_prefix=prefix, intents=intents)
# botId =
#token = str(os.environ['BOT_TOKEN'])
token = str(os.getenv("BOT_TOKEN"))

# IDs
rolesIDs = f.loadData(CONST_DISCORD)["roles_id"]

# Messages
helpMSG = [
    """## Commandes du bot
- Les commandes sont présentées sous la forme:
`!commande <argumentObligatoire> [argumentFacultatif]`: description; 
- Le bot utilise les espaces pour découper les commandes en morceaux et les comprendre. Il faut remplacer les espaces dans les arguments par des "_" pour que le bot comprenne que c'est un seul argument et pas deux. Il y a **une seule exception**: les copier-collers venant de Nature at War comme pour la commade `!setArmy`. Par exemple: on utilise `bad_broly` au lieu de `bad broly`, `chambre_impériale` au lieu de `chambre impériale`.
- `\\n` représente un saut de ligne (`shift + entrée` sur PC)
- Pensez à enlever les `<`, `>`, `[` et `]` quand vous utilisez un modèle de commande ;);)
---
Par exemple: `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`
donne:
```!setArmy bad_broly C1
300 000 Esclaves, 9 717 Jeunes tanks```""",
    """### Commandes Aides
`!help`: affiche les commandes;
`!templatePlayer`: donne la fiche à remplir pour enregistrer un joueur;
`!templatePacte`: donne la commande à remplir pour enregistrer un pacte;""",
    """### Commandes Alliance
`!printAlliance`: affiche les données de l'alliance; 
`!setTDC <tdc>`: modifie la quantité de TDC de l'alliance;
`!setNbMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
`!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie le bonus d'alliance;
`!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie les stats de l'alliance;""",
    """### Commandes Chasses
`!printChasses <joueur>`: affiche les chasses d'un joueur
`!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;""",
    """### Commandes Convois
`!convoisEnCours`: affiche les convois en cours;
`!autoProd <joueur> <C1/C2> <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
`!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`: ajoute un convoi;
`!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;""",
    """### Commandes Floods externes
`!floodExtR <joueurExtérieur> <C1/C2> <ally> <quantité> <joueurLF> <C1/C2>`: enregistre un flood externe reçu;
`!floodExtD <joueurExtérieur> <C1/C2> <ally> <quantité> <joueurLF> <C1/C2>`: enregistre un flood externe donné;
`!futursfloods`: affiche les floods à faire; 
`!printFloodsExt [alliance]`: affiche les floods externes;
`!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple);""",
    """### Commandes Joueurs
`!printPlayer <joueur>`: affiche les données d'un joueur.
`!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`: modifie l'armée d'un joueur;
`!setTDCExploité <joueur> <tdcExploté>`: modifie le tdc exploité d'un joueur;
`!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur;
`!setStatsColo <joueur> <C1/C2> <oe> <ov> <tdp>`: modifie les stats d'une colonie d'un joueur;
`!setVassal <joueurVassalisé> <coloVassalisée:C1/C2> <vassal> <coloVassal:C1/C2> <pillage>`: modifie le vassal d'une colonie d'un joueur;
`!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur;
`!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`: modifie le héros d'un joueur;
`!player \\n <templatePlayer>`: ajoute un nouveau joueur.""", 
    """### Commandes Pactes
`!printPactes`: affiche les pactes;
`!endPacte`: clôt un pacte;
`!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> [end] \\n <titre> \\n <description>`: ajoute un nouveau pacte;"""
]


#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

# ERROR HANDLER
# error sender
async def error(channel, errorMsg: str):
  await channel.send(errorMsg)


# length verification
async def lengthVerificatorWError(message, command):
  if len(message.content.upper().split(" ")) == len(command.upper().split(" ")):
    return True
  elif len(message.content.upper().split(" ")) < len(command.upper().split(" ")):
    await error(message.channel,"Peu d'arguments ont été donnés:`" + command + "`")
    return False
  elif len(message.content.upper().split(" ")) > len(command.upper().split(" ")):
    await error(message.channel,"Trop d'arguments ont été donnés:`" + command + "`")
    return False


async def lengthVerificator(message, command):
  res = False
  if len(message.content.upper().split(" ")) == len(
      command.upper().split(" ")):
    res = True
  return res


async def errorRole(channel, roleList: list):
  msg = "il faut être "
  for i in range(len(roleList)):
    msg += "`" + roleList[i]
    if i == len(roleList) - 1: "` "
    elif i == len(roleList) - 2: msg += "`, ou "
    else: msg += "`, "
  msg += "` pour utiliser cette commande"
  await channel.send(msg)


#__________________________________________________#
## AIDE ##
#__________________________________________________#


# `!help`: affiche les commandes;
async def help(message, page=None):
  global helpMSG
  await message.delete()
  for i in range(len(helpMSG)):
    if page == None or page+1 == i:
      await message.channel.send(helpMSG[i])


# `!templatePlayer`: donne la fiche à remplir pour enregistrer un joueur;
async def templatePlayer(message):
  msg = f.loadData(CONST_TEMPLATES)["player"]
  await message.delete()
  await message.channel.send(msg)


# `!templatePacte`: donne la commande à remplir pour enregistrer un pacte;
async def templatePacte(message):
  msg = f.loadData(CONST_TEMPLATES)["pacte"]
  await message.delete()
  await message.channel.send(msg)


#__________________________________________________#
## ALLIANCE ##
#__________________________________________________#


# `!printAlliance`: affiche les données de l'alliance;
async def printAlliance(message):
  if await lengthVerificatorWError(message, "!printAlliance"):
    msg = alliance.printAlliance()
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setTDC <tdc>`: modifie la quantité de TDC de l'alliance;
async def setTDC(message):
  if await lengthVerificatorWError(message, "!setTDC <tdc>"):
    msg = alliance.setTDC(f.getNumber(message.content.split(" ")[1]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setNBMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
async def setNBMembre(message):
  if await lengthVerificatorWError(message, "!setMembers <quantité>"):
    msg = alliance.setNBMembre(f.getNumber(message.content.split(" ")[1]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie le bonus d'alliance;
async def setBonusAlly(message):
  if await lengthVerificatorWError(
      message,
      "!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>"):
    msg = alliance.setBonusAlly(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        message.content.split(" ")[4])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie les stats de l'alliance;
async def setAlly(message):
  if await lengthVerificatorWError(
      message,
      "!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>"
  ):
    msg = alliance.setAlly(f.getNumber(message.content.split(" ")[1]),
                           message.content.split(" ")[2],
                           message.content.split(" ")[3],
                           message.content.split(" ")[4],
                           message.content.split(" ")[5],
                           message.content.split(" ")[6])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


#__________________________________________________#
## CHASSES ##
#__________________________________________________#


# `!printChasses <joueur>`: affiche les chasses d'un joueur
async def printChasses(message):
  if await lengthVerificatorWError(message, "!printChasses <joueur>"):
    msg = chasses.printChasses(message.content.split(" ")[1])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;
async def chasse(message):
  if await lengthVerificatorWError(message,
                                   "!chasse <joueur> <C1/C2> <quantité>"):
    msg = chasses.chasse(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        f.getNumber(message.content.split(" ")[3]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


#__________________________________________________#
## CONVOIS ##
#__________________________________________________#


# `!convoisEnCours`: affiche les convois en cours;
async def printConvoisEnCours(message):
  if await lengthVerificatorWError(message, "!printConvois"):
    msg = convois.printConvoisEnCours()
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`: ajoute un convoi;
async def convoi(message):
  if await lengthVerificatorWError(
      message,
      "!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>"):
    msg = convois.convoi(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        f.getNumber(message.content.split(" ")[3]),
        f.getNumber(message.content.split(" ")[4]),
        f.getNumber(message.content.split(" ")[5]),
        message.content.split(" ")[6],
        message.content.split(" ")[7])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;
async def demandeConvoi(message):
  if await lengthVerificatorWError(
      message,
      "!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>"
  ):
    msg = convois.demandeConvoi(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        message.content.split(" ")[4],
        f.getNumber(message.content.split(" ")[5]),
        f.getNumber(message.content.split(" ")[6]),
        f.getNumber(message.content.split(" ")[7]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!autoProd <joueur> <C1/C2> <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
async def autoProd(message):
  if await lengthVerificatorWError(
      message, "!autoProd <joueur> <C1/C2> <pomme> <bois> <eau>"):
    msg = convois.autoProd(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        f.getNumber(message.content.split(" ")[3]),
        f.getNumber(message.content.split(" ")[4]),
        f.getNumber(message.content.split(" ")[5]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


#__________________________________________________#
## FLOODS EXTERNES ##
#__________________________________________________#


# `!floodExtR <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>`: enregistre un flood externe reçu;
async def floodExtR(message):
  checked = False
  date = ""
  if await lengthVerificator(
      message,
      "!floodEXT <joueurEXT> <C1/C2> <ally> <quantity> <joueurLF> <C1/C2>"):
    checked = True
    date = datetime.now().strftime("%Y-%m-%d")
  elif await lengthVerificator(
      message,
      "!floodExtR <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2> <date>"
  ):
    checked = True
    date = message.content.split(" ")[7]
  if checked:
    msg = floods.floodExtR(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        f.getNumber(message.content.split(" ")[4]),
        message.content.split(" ")[5],
        message.content.split(" ")[6], date)
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!floodExtD <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>`: enregistre un flood externe donné;
async def floodExtD(message):
  checked = False
  date = ""
  if await lengthVerificator(
      message,
      "!floodExtD <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>"):
    checked = True
    date = datetime.now().strftime("%Y-%m-%d")
  elif await lengthVerificator(
      message,
      "!floodExtD <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2> <date>"
  ):
    checked = True
    date = message.content.split(" ")[7]
  if checked:
    msg = floods.floodExtD(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        f.getNumber(message.content.split(" ")[4]),
        message.content.split(" ")[5],
        message.content.split(" ")[6],
        date,
    )
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!futursfloods`: affiche les floods à faire;
async def printFloodsFuturs(message):
  if await lengthVerificatorWError(message, "!floodsFuturs"):
    msg = floods.printFloodsFuturs()
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!printFloodsExt`: affiche les floods externes;
async def printFloodsExt(message):
  if await lengthVerificatorWError(message, "!printFloodsExt"):
    msg= ""
    if len(message.content.split(" ")) == 1:
      msg = floods.printFloodsExt()
    elif len(message.content.split(" ")) == 2:
      msg = floods.printFloodsExtAlly(message.content.split(" ")[1])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple)
async def donTDC(message):
  if await lengthVerificatorWError(
      message,
      "!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>"):
    msg = floods.donTDC(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        f.getNumber(message.content.split(" ")[3]),
        message.content.split(" ")[4])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


#__________________________________________________#
## PLAYERS ##
#__________________________________________________#


# `!printPlayer <joueur>`: affiche les données d'un joueur.
async def printPlayer(message):
  if await lengthVerificatorWError(message, "!printPlayer <joueur>"):
    msg = joueurs.printPlayer(message.content.split(" ")[1])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!player \n <templatePlayer>`: ajoute un nouveau pacte
async def player(message):
  if len(message.content.split("\n")) > 2:
    msg = joueurs.addPlayer(message)
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message.channel,"Erreur dans la commande: `!player \n <templatePlayer>`")

# `!setTDCExploité <joueur> <tdcExploté>`: modifie le tdc exploité d'un joueur;
async def setTDCExploité(message):
  if await lengthVerificatorWError(message, "!setTDCExploité <joueur> <tdcExploté>"):
    msg = joueurs.setTDCExploité(message.content.split(" ")[1],f.getNumber(message.content.split(" ")[2]))
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)

# `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`: modifie l'armée d'un joueur.
async def setArmy(message):
  if len(message.content.split("\n")) > 1:
    msg = joueurs.setArmy(
        message.content.split("\n")[0].split(" ")[1],
        message.content.split("\n")[0].split(" ")[2],
        message.content.split("\n")[1])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message.channel,"Erreur dans la commande: `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`")


# `!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur.
async def setRace(message):
  if await lengthVerificatorWError(
      message, "!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>"):
    msg = joueurs.setRace(
        message.content.split(" ")[1],
        message.content.split(" ")[2])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  


# `!setStatsColo <joueur> <colo> <oe> <ov> <tdp>`: modifie les stats d'une colonie d'un joueur.
async def setStatsColo(message):
  if await lengthVerificatorWError(
      message, "!setStatsColo <joueur> <colo> <oe> <ov> <tdp>"):
    msg = joueurs.setStatsColo(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        f.getNumber(message.content.split(" ")[3]),
        f.getNumber(message.content.split(" ")[4]),
        message.content.split(" ")[5])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)



# `!setVassal <joueurVassalisé> <coloVassalisée> <vassal> <coloVassal> <pillage>`: modifie le vassal d'une colonie d'un joueur.
async def setVassal(message):
  if await lengthVerificatorWError(
      message,
      "!setVassal <joueurVassalisé> <coloVassalisée> <vassal> <coloVassal> <pillage>"
  ):
    msg = joueurs.setVassal(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        message.content.split(" ")[4],
        message.content.split(" ")[5])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)



# `!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur.
async def setStatsPlayer(message):
  if await lengthVerificatorWError(
      message,
      "!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>"
  ):
    msg = joueurs.setStatsPlayer(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3],
        message.content.split(" ")[4],
        message.content.split(" ")[5])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message.channel,
                "Erreur dans la commande: `!player \n <templatePlayer>`")


# `!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`: modifie le héros d'un joueur.
async def setHero(message):
  if await lengthVerificatorWError(
      message,
      "!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>"):
    msg = joueurs.setHero(
        message.content.split(" ")[1],
        message.content.split(" ")[2],
        message.content.split(" ")[3])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message.channel,
                "Erreur dans la commande: `!player \n <templatePlayer>`")


#__________________________________________________#
## PACTES ##
#__________________________________________________#


# `!printPactes`: affiche les pactes;
async def printPactes(message):
  if await lengthVerificatorWError(message, "!printPactes"):
    msg = pactes.printPactes()
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!endPacte <ally>`: clôt un pacte;
async def endPacte(message):
  if await lengthVerificatorWError(message, "!endPacte <ally>"):
    msg = pactes.endPacte(message.content.split(" ")[1])
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`: ajoute un nouveau pacte
async def pacte(message):
  if len(message.content.split("\n")) > 2:
    msg = pactes.addPacte(message)
    if msg.startswith("ERR:"):
      await error(message.channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(
        message.channel,
        "Erreur dans la commande: `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`"
    )


#__________________________________________________#
## EXTERNE ##
#__________________________________________________#


# !printDB <DB>
# affiche les données d'une base de données
async def printDB(message):
  await message.delete()
  if lengthVerificatorWError(message, "!printDB <DB>"):
    await dbg.printDB(message.channel, message.content.split(" ")[1])


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

  if message.content.upper().startswith("!"):
    admin = user.get_role(rolesIDs["bot admin access"]) is not None
    writer = user.get_role(rolesIDs["bot writer access"]) is not None
    superReader = user.get_role(rolesIDs["bot super-reader access"]) is not None
    reader = user.get_role(rolesIDs["bot reader access"]) is not None

    chef = user.get_role(rolesIDs["chef"]) is not None
    second = user.get_role(rolesIDs["second"]) is not None
    recruteur = user.get_role(rolesIDs["recruteur"]) is not None
    diplo = user.get_role(rolesIDs["diplomate"]) is not None
    membre = user.get_role(rolesIDs["membre"]) is not None

    grenier = user.get_role(rolesIDs["grenier"]) is not None
    chasseur = user.get_role(rolesIDs["chasseur"]) is not None
    guerrier = user.get_role(rolesIDs["guerrier"]) is not None

    is_concerned = False

    lf_members = [
        "antoriax", "bad_broly", "bendowin", "blackpixel", "mystogan",
        "scarapace", "yvahra"
    ]
    for m in lf_members:
      if user.get_role(
          rolesIDs[m]) is not None and m in message.content.lower():
        is_concerned = True



    
    ### ----- ###
    ### Aides ###
    ### ----- ###

    
    #`!help`
    # affiche les commandes;
    if message.content.upper().startswith("!HELP AIDE"):
      await help(message, 0)
    elif message.content.upper().startswith("!HELP ALLIANCE"):
      await help(message, 1)
    elif message.content.upper().startswith("!HELP CHASSE"):
      await help(message, 2)
    elif message.content.upper().startswith("!HELP CONVOI"):
      await help(message, 3)
    elif message.content.upper().startswith("!HELP FLOOD"):
      await help(message, 4)
    elif message.content.upper().startswith("!HELP JOUEUR"):
      await help(message, 5)
    elif message.content.upper().startswith("!HELP PACTE"):
      await help(message, 6)
    elif message.content.upper().startswith("!HELP"): 
      await help(message)

      #`!templatePlayer`
      # donne la fiche à remplir pour enregistrer un joueur;
    elif message.content.upper().startswith("!TEMPLATEPLAYER"):
      if admin:
        await templatePlayer(message)
      else:
        await errorRole(message.channel,["bot admin access"])

    # `!templatePacte`
    # donne la commande à remplir pour enregistrer un pacte;
    elif message.content.upper().startswith("!TEMPLATEPACTE"):
      if admin or diplo:
        await templatePacte(message)
      else:
        await errorRole(message.channel,["bot admin access", "diplo"])

    
    ### -------- ###
    ### Alliance ###
    ### -------- ###

    
    # `!printAlliance`
    # affiche les données de l'alliance;
    elif message.content.upper().startswith("!PRINTALLIANCE"):
      if admin or superReader or membre:
        await printAlliance(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot super-reader acces", "membre"])

    # `!setTDC <tdc>`
    # modifie la quantité de TDC de l'alliance;
    elif message.content.upper().startswith("!SETTDC"):
      if admin or writer:
        await setTDC(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    # `!setNbMember <quantité>`
    # modifie le nombre de joueurs de l'alliance;
    elif message.content.upper().startswith("!SETNBMEMBRE"):
      if admin or writer:
        await setNBMembre(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    # `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie le bonus d'alliance;
    elif message.content.upper().startswith("!SETBONUSALLY"):
      if admin or writer:
        await setBonusAlly(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    # `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie les stats de l'alliance;
    elif message.content.upper().startswith("!SETALLY"):
      if admin or writer:
        await setAlly(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    
    ### ------- ###
    ### Chasses ###
    ### ------- ###

    
    # `!printChasses <joueur>`
    # affiche les chasses d'un joueur
    elif message.content.upper().startswith("!PRINTCHASSES"):
      await printChasses(message)
      if admin or writer:
        await setAlly(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    # `!chasse <joueur> <C1/C2> <quantité>`
    # enregistre une chasse;
    elif message.content.upper().startswith("!CHASSE"):
      if admin or writer or is_concerned:
        await chasse(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

  
      ### ------- ###
      ### Convois ###
      ### ------- ###

  
    # `!convoisEnCours`
    # affiche les convois en cours;
    elif message.content.upper().startswith("!CONVOISENCOURS"):
      if admin or writer or superReader or membre:
        await printConvoisEnCours(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`
      # ajoute un convoi;
    elif message.content.upper().startswith("!CONVOI"):
      if admin or writer or is_concerned:
        await convoi(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!autoProd <joueur> <C1/C2> <pomme> <bois> <eau>`
      # met à jour un convoi avec l'autoprod d'un joueur;
    elif message.content.upper().startswith("!AUTOPROD"):
      if admin or writer or is_concerned:
        await autoProd(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!demandeConvoi <joueur> <C1/C2> <pomme> <bois> <eau>`
      # ajoute un convoi à la liste des convois en cours;
    elif message.content.upper().startswith("!DEMANDECONVOI"):
      if admin or writer or membre:
        await demandeConvoi(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "membre"])

    
      ### --------------- ###
      ### Floods externes ###
      ### --------------- ###

    
      # `!floodExtR <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>`
      # enregistre un flood externe reçu;
    elif message.content.upper().startswith("!FLOODEXTR"):
      if admin or writer or is_concerned:
        await floodExtR(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!floodExtD <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>`
      # enregistre un flood externe donné;
    elif message.content.upper().startswith("!FLOODEXTD"):
      if admin or writer or is_concerned:
        await floodExtD(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!futursfloods`
      # affiche les floods à faire;
    elif message.content.upper().startswith("!FUTURSFLOODS"):
      if admin or writer or superReader or membre:
        await printFloodsFuturs(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!printFloodsExt`
      # affiche les floods externes;
    elif message.content.upper().startswith("!PRINTFLOODSEXT"):
      if admin or writer or superReader:
        await printFloodsExt(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`
      # enregistre un don de tdc (butin de guerre par exemple)
    elif message.content.upper().startswith("!DONTDC"):
      if admin or writer:
        await donTDC(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access"])

    
      ### ------- ###
      ### Joueurs ###
      ### ------- ###

    
      # `!printPlayer <joueur>`
      # affiche les données d'un joueur.
    elif message.content.upper().startswith("!PRINTPLAYER"):
      if admin or writer or is_concerned:
        await printPlayer(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!player \\n <templatePlayer>`
      # ajoute un nouveau pacte
    elif message.content.upper().startswith("!PLAYER"):
      if admin:
        await player(message)
      else:
        await errorRole(message.channel,["bot admin access"])

      # `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`
      # modifie l'armée d'un joueur.
    elif message.content.upper().startswith("!SETARMY"):
      if admin or writer or is_concerned:
        await setArmy(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`
      # modifie la race d'un joueur.
    elif message.content.upper().startswith("!SETRACE"):
      if admin or writer or is_concerned:
        await setRace(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsColo <joueur> <colo> <oe> <ov> <tdp>`
      # modifie les stats d'une colonie d'un joueur.
    elif message.content.upper().startswith("!SETSTATSCOLO"):
      if admin or writer or is_concerned:
        await setStatsColo(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setVassal <joueurVassalisé> <coloVassalisée> <vassal> <coloVassal> <pillage>`
      # modifie le vassal d'une colonie d'un joueur.
    elif message.content.upper().startswith("!SETVASSAL"):
      if admin or writer or is_concerned:
        await setVassal(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`
      # modifie les statistiques générales d'un joueur.
    elif message.content.upper().startswith("!SETSTATSPLAYER"):
      if admin or writer or is_concerned:
        await setStatsPlayer(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`
      # modifie le héros d'un joueur.
    elif message.content.upper().startswith("!SETHERO"):
      if admin or writer or is_concerned:
        await setHero(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "joueur concerné"])

    
      ### ------ ###
      ### Pactes ###
      ### ------ ###

    
      # `!printPactes`
      # affiche les pactes;
    elif message.content.upper().startswith("!PRINTPACTES"):
      if admin or writer or superReader:
        await printPactes(message)
      else:
        await errorRole(message.channel,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!endPacte <ally>`
      # clôt un pacte;
    elif message.content.upper().startswith("!ENDPACTE"):
      if admin or diplo:
        await endPacte(message)
      else:
        await errorRole(message.channel,["bot admin access", "diplo"])

      # `!pacte <ally> <type-guerre> <type-commerce> <start> <end> \\n <titre> \\n <description>`
      # ajoute un nouveau pacte
    elif message.content.upper().startswith("!PACTE"):
      if admin or diplo:
        await pacte(message)
      else:
        await errorRole(message.channel,["bot admin access", "diplo"])

    
      ### ------ ###
      ### ERRORS ###
      ### ------ ###

    
    elif message.content.startswith("!"):
      await error(
          message.channel,
          "Commande inconnue. `!help` pour voir la liste des commandes disponibles."
      )  #error
    else:
      pass  #usual message


#__________________________________________________#
## Run ##
#__________________________________________________#

#On va maintenir le bot en acitivité
keep_alive()
#On lance le bot
bot.run(token)
