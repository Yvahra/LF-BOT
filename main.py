##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import os
import discord
from discord.ext import commands
from datetime import datetime, date
from dotenv import load_dotenv

from keep_alive import keep_alive
import db_rawGetters as dbg
import functions as f
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
S_ACTIVE_PLAYERS = "STATS//Stats_JoueursActifs.json"

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
`!help <aide/alliance/convois/chasse/joueur/pacte>`: affiche les commandes sur un sujet spécifique;
`!templatePlayer`: donne la fiche à remplir pour enregistrer un joueur;
`!templatePacte`: donne la commande à remplir pour enregistrer un pacte;""",
    """### Commandes Alliance
`!printAlliance`: affiche les données de l'alliance; 
`!setTDCAlly <tdc>`: modifie la quantité de TDC de l'alliance;
`!setNbMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
`!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie le bonus d'alliance;
`!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie les stats de l'alliance;""",
    """### Commandes Chasses
`!printChasses <joueur>`: affiche les chasses d'un joueur
`!chasse [joueur] <quantité>`: enregistre une chasse;""",
    """### Commandes Convois
`!convoisEnCours`: affiche les convois en cours;
`!autoProd [joueur] <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
`!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`: ajoute un convoi;
`!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;
`!recapRessources`: calcul le récapitulatif des ressources récoltées de la journée;
`!printRecapRessources`: affiche le récapitulatif des ressources récoltées de la journée;""",
    """### Commandes Floods externes
`!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe reçu;
`!floodExtD [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe donné;
`!futursfloods`: affiche les floods à faire; 
`!printFloodsExt [alliance]`: affiche les floods externes;
`!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple);""",
    """### Commandes Joueurs
`!printPlayer <joueur>`: affiche les données d'un joueur.
`!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`: modifie l'armée d'un joueur;
`!setTDCExploité [joueur] <C1/C2> <tdcExploité>`: modifie le tdc exploité d'un joueur;
`!setTDC <joueur> <C1/C2> <tdc>`: modifie le tdc d'un joueur;
`!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur;
`!setStatsColo <joueur> <C1/C2> <oe> <ov> <tdp>`: modifie les stats d'une colonie d'un joueur;
`!setVassal <joueurVassalisé> <coloVassalisée:C1/C2> <vassal> <coloVassal:C1/C2> <pillage>`: modifie le vassal d'une colonie d'un joueur;
`!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur;
`!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`: modifie le héros d'un joueur;
`!player \\n <templatePlayer>`: ajoute un nouveau joueur;
`!setActivePlayers <joueur1> ... <joueurN>`: définit les joueurs actifs de la LF;
`!getActivePlayers`: donne les joueurs actifs de la LF;""",
    """### Commandes Pactes
`!printPactes`: affiche les pactes;
`!endPacte`: clôt un pacte;
`!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> [end] \\n <titre> \\n <description>`: ajoute un nouveau pacte;""",
    """### Commandes Dev
`!getDbNames`: donne les noms des bases de données;
`!getDB <path//filename>`: donne la base de données;
`!getLog [date]`: donne les logs [du jour en cours, par défaut];"""
]


#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

# ERROR HANDLER
# error sender
async def error(message, errorMsg: str):
    f.log(rank=1, prefixe="[ERROR]", message=message.content, suffixe=errorMsg)
    await message.channel.send(errorMsg)

def checkRoles(message, roles:list) -> bool:
    if not any(roles):
        f.log(rank=1, prefixe="[ERROR]", message="No permission", suffixe=" - "+str(roles))
    return any(roles)

# length verification
async def lengthVerificatorWError(message, command):
  if len(message.content.upper().split(" ")) == len(command.upper().split(" ")):
    return True
  elif len(message.content.upper().split(" ")) < len(command.upper().split(" ")):
    f.log(rank=1, prefixe="[ERROR]", message="Peu d'arguments ont été donnés:`" + command + "`", suffixe="")
    await error(message,"Peu d'arguments ont été donnés:`" + command + "`")
    return False
  elif len(message.content.upper().split(" ")) > len(command.upper().split(" ")):
    f.log(rank=1, prefixe="[ERROR]", message="Trop d'arguments ont été donnés:`" + command + "`", suffixe="")
    await error(message,"Trop d'arguments ont été donnés:`" + command + "`")
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
    if i == len(roleList) - 1:
        "` "
    elif i == len(roleList) - 2:
        msg += "`, ou "
    else:
        msg += "`, "
  msg += "` pour utiliser cette commande"
  await channel.send(msg)

def getPlayerFromRoles(user) -> str:
     players = f.loadData(CONST_DISCORD)["player_id"]
     res = None
     for player in players:
        if not user.get_role(players[player]) is None:
            res = player
     return res

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
      await error(message, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setTDCAlly <tdc>`: modifie la quantité de TDC de l'alliance;
async def setTDCAlly(message):
  if await lengthVerificatorWError(message, "!setTDCAlly <tdc>"):
    msg = alliance.setTDC(f.getNumber(message.content.split(" ")[1]))
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      await message.channel.send(msg)


# `!setNBMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
async def setNBMembre(message):
  if await lengthVerificatorWError(message, "!setMembers <quantité>"):
    msg = alliance.setNBMembre(f.getNumber(message.content.split(" ")[1]))
    if msg.startswith("ERR:"):
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;
async def chasse(message):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!chasse [joueur] <quantité>`"
    if await lengthVerificator(message, "!chasse [joueur] <quantité>"):
        msg = convois.convoi(
            message.content.split(" ")[1],
            f.getNumber(message.content.split(" ")[2]))
    if await lengthVerificator(message, "!chasse <quantité>"):
        if player is None:
            msg = "ERR: vous ne pouvez pas chasser!"
        else:
            msg = convois.convoi(
                player,
                f.getNumber(message.content.split(" ")[1]))
        if msg.startswith("ERR:"):
            await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`: ajoute un convoi;
async def convoi(message, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`"
    if await lengthVerificator(message, "!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>"):
        msg = convois.convoi(
            message.content.split(" ")[1],
            message.content.split(" ")[2],
            f.getNumber(message.content.split(" ")[3]),
            f.getNumber(message.content.split(" ")[4]),
            f.getNumber(message.content.split(" ")[5]))
    if await lengthVerificator(message, "!convoi <convoyé> <pomme> <bois> <eau>"):
        if player is None:
            msg = "ERR: vous ne pouvez pas convoyer!"
        else:
            msg = convois.convoi(
                player,
                message.content.split(" ")[1],
                f.getNumber(message.content.split(" ")[2]),
                f.getNumber(message.content.split(" ")[3]),
                f.getNumber(message.content.split(" ")[4]))
        if msg.startswith("ERR:"):
            await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!autoProd [joueur] <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
async def autoProd(message, player):
  msg = "ERR: trop ou pas assez d'arguments dans la commande: `!autoProd [joueur] <pomme> <bois> <eau>`"
  if await lengthVerificator(message, "!autoProd [joueur] <pomme> <bois> <eau>"):
    msg = convois.autoProd(
        message.content.split(" ")[1],
        f.getNumber(message.content.split(" ")[2]),
        f.getNumber(message.content.split(" ")[3]),
        f.getNumber(message.content.split(" ")[4]))
  if await lengthVerificator(message, "!autoProd <pomme> <bois> <eau>") :
    if player is None:
        msg = "ERR: vous ne pouvez pas vous autoconvoyer!"
    else:
        msg = convois.autoProd(
            player,
            f.getNumber(message.content.split(" ")[1]),
            f.getNumber(message.content.split(" ")[2]),
            f.getNumber(message.content.split(" ")[3]))
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)

# `!recapRessources [yyyy-mm-dd]``: calcul le récapitulatif des ressources récoltées de la journée;
async def recapRSS(message):
    channel = bot.get_channel(1276232505116196894)
    msg = ""
    if len(message.content.split(" ")) > 1:
        msg = convois.repartitionRessources(message.content.split(" ")[1])
    else:
        msg = convois.repartitionRessources(date.today().strftime("%Y-%m-%d"))
    if msg.startswith("ERR:"):
      await error(channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)

# `!printRecapRessources`: affiche le récapitulatif des ressources récoltées de la journée;
async def printRecapRSS(message):
    channel = bot.get_channel(1276232505116196894)
    msg = ""
    if len(message.content.split(" ")) > 1:
        msg = convois.printRessourcesPartagees(message.content.split(" ")[1])
    else:
        msg = convois.printRessourcesPartagees(date.today().strftime("%Y-%m-%d"))

    if msg.startswith("ERR:"):
      await error(channel, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)


#__________________________________________________#
## FLOODS EXTERNES ##
#__________________________________________________#


# `!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe reçu;
async def floodExtR(message, palyer):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`"
    if await lengthVerificator(message, "!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>"):
        msg = floods.floodExtR(
            message.content.split(" ")[1],
            message.content.split(" ")[2],
            message.content.split(" ")[3],
            message.content.split(" ")[4],
            f.getNumber(message.content.split(" ")[5]))
    if await lengthVerificator(message, "!floodExtR [date/joueurLF] <joueurExtérieur> <ally> <quantité>"):
        try:
            datetime.strptime(message.content.split(" ")[1], "%Y-%m-%d")
            msg = floods.floodExtR(
                message.content.split(" ")[1],
                player,
                message.content.split(" ")[2],
                message.content.split(" ")[3],
            f.getNumber(message.content.split(" ")[4]))
        except:
            if player is None:
                msg = "ERR: vous ne pouvez pas enregistrer de floods!"
            else:
                msg = floods.floodExtR(
                    datetime.now().strftime("%Y-%m-%d"),
                    message.content.split(" ")[1],
                    message.content.split(" ")[2],
                    message.content.split(" ")[3],
                f.getNumber(message.content.split(" ")[4]))
    if await lengthVerificator(message, "!floodExtR <joueurExtérieur> <ally> <quantité>"):
        if player is None:
            msg = "ERR: vous ne pouvez pas enregistrer de floods!"
        else:
            msg = floods.floodExtR(
                datetime.now().strftime("%Y-%m-%d"),
                player,
                message.content.split(" ")[1],
                message.content.split(" ")[2],
                f.getNumber(message.content.split(" ")[3]))
        if msg.startswith("ERR:"):
            await error(message, msg)
        else:
            await message.delete()
            for m in f.splitMessage(msg):
                await message.channel.send(m)


# `!floodExtD <floodeur> <C1/C2> <ally> <quantité> <floodé> <C1/C2>`: enregistre un flood externe donné;
async def floodExtD(message, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`"
    if await lengthVerificator(message, "!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>"):
        msg = floods.floodExtD(
            message.content.split(" ")[1],
            message.content.split(" ")[2],
            message.content.split(" ")[3],
            message.content.split(" ")[4],
            f.getNumber(message.content.split(" ")[5]))
    if await lengthVerificator(message, "!floodExtR [date/joueurLF] <joueurExtérieur> <ally> <quantité>"):
        try:
            datetime.strptime(message.content.split(" ")[1], "%Y-%m-%d")
            msg = floods.floodExtD(
                message.content.split(" ")[1],
                player,
                message.content.split(" ")[2],
                message.content.split(" ")[3],
                f.getNumber(message.content.split(" ")[4]))
        except:
            if player is None:
                msg = "ERR: vous ne pouvez pas enregistrer de floods!"
            else:
                msg = floods.floodExtD(
                    datetime.now().strftime("%Y-%m-%d"),
                    message.content.split(" ")[1],
                    message.content.split(" ")[2],
                    message.content.split(" ")[3],
                    f.getNumber(message.content.split(" ")[4]))
    if await lengthVerificator(message, "!floodExtR <joueurExtérieur> <ally> <quantité>"):
        if player is None:
            msg = "ERR: vous ne pouvez pas enregistrer de floods!"
        else:
            msg = floods.floodExtD(
                datetime.now().strftime("%Y-%m-%d"),
                player,
                message.content.split(" ")[1],
                message.content.split(" ")[2],
                f.getNumber(message.content.split(" ")[3]))
        if msg.startswith("ERR:"):
            await error(message, msg)
        else:
            await message.delete()
            for m in f.splitMessage(msg):
                await message.channel.send(m)


# `!futursfloods`: affiche les floods à faire;
async def printFloodsFuturs(message):
  if await lengthVerificatorWError(message, "!floodsFuturs"):
    msg = floods.printFloodsFuturs()
    if msg.startswith("ERR:"):
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!player \n <templatePlayer>`: ajoute un nouveau pacte
async def player(message):
  if len(message.content.split("\n")) > 2:
    msg = joueurs.addPlayer(message)
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message,"Erreur dans la commande: `!player \n <templatePlayer>`")

# `!setTDCExploité [joueur] <C1/C2> <tdcExploité>`: modifie le tdc exploité d'un joueur;
async def setTDCExploit(message, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!setTDCExploité [joueur] <C1/C2> <tdcExploité>`"
    if await lengthVerificator(message, "!setTDCExploité [joueur] <C1/C2> <tdcExploité>"):
        msg = joueurs.setTDCExploité(message.content.split(" ")[1],
                                     message.content.split(" ")[2],
                                     f.getNumber(message.content.split(" ")[3]))
    if await lengthVerificator(message, "!setTDCExploité <C1/C2> <tdcExploité>"):
        if player is None:
            msg = "ERR: vous ne pouvez pas enregistrer de floods!"
        else:
            msg = joueurs.setTDCExploité(player,
                                         message.content.split(" ")[1],
                                         f.getNumber(message.content.split(" ")[2]))
        if msg.startswith("ERR:"):
            await error(message, msg)
        else:
            await message.delete()
            for m in f.splitMessage(msg):
                await message.channel.send(m)


# `!setTDC <joueur> <C1/C2> <tdc>`: modifie le tdc d'un joueur;
async def setTDC(message):
  if await lengthVerificatorWError(message, "!setTDC <joueur> <C1/C2> <tdc>"):
    msg = joueurs.setTDC(message.content.split(" ")[1],
                         message.content.split(" ")[2],
                         f.getNumber(message.content.split(" ")[3]))
    if msg.startswith("ERR:"):
      await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message,"Erreur dans la commande: `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`")


# `!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur.
async def setRace(message):
  if await lengthVerificatorWError(
      message, "!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>"):
    msg = joueurs.setRace(
        message.content.split(" ")[1],
        message.content.split(" ")[2])
    if msg.startswith("ERR:"):
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message,
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
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(message,
                "Erreur dans la commande: `!player \n <templatePlayer>`")

#`!setActivePlayers <joueur1> ... <joueurN>`: définit les joueurs actifs de la LF;
async def setActivePlayers(message):
    newData = []
    if len(message.content.split(" ")) == 0:
        pass
    else:
        for p in message.content.split(" ")[1:]:
            newData.append(p.lower())
    f.saveData(newData, S_ACTIVE_PLAYERS)
    await getActivePlayers(message)

#`!getActivePlayers`: donne les joueurs actifs de la LF;
async def getActivePlayers(message):
    activeP = f.loadData(S_ACTIVE_PLAYERS)
    msg = "Les joueurs actifs de la LF sont:\n"
    for p in activeP:
        msg+="   "+p+"\n"
    for m in f.splitMessage(msg):
        await message.channel.send(m)


#__________________________________________________#
## PACTES ##
#__________________________________________________#


# `!printPactes`: affiche les pactes;
async def printPactes(message):
  if await lengthVerificatorWError(message, "!printPactes"):
    msg = pactes.printPactes()
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!endPacte <ally>`: clôt un pacte;
async def endPacte(message):
  if await lengthVerificatorWError(message, "!endPacte <ally>"):
    msg = pactes.endPacte(message.content.split(" ")[1])
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)


# `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`: ajoute un nouveau pacte
async def pacte(message):
  if len(message.content.split("\n")) > 2:
    msg = pactes.addPacte(message)
    if msg.startswith("ERR:"):
      await error(message, msg)
    else:
      await message.delete()
      for m in f.splitMessage(msg):
        await message.channel.send(m)
  else:
    await error(
        message,
        "Erreur dans la commande: `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`"
    )


#__________________________________________________#
## DEV ##
#__________________________________________________#

# `!getDbNames`: donne les noms des bases de données;
async def getDbNames(message):

  msg = "Available files:\n```"
  print(os.path.dirname(__file__))
  for f in os.listdir(os.path.dirname(__file__)+"/JSON/CONST/"):
      msg+= "    CONST/" + f + "\n"
  for f in os.listdir(os.path.dirname(__file__)+"/JSON/HIST/"):
      msg+= "    HIST/" + f + "\n"
  for f in os.listdir(os.path.dirname(__file__)+"/JSON/STATS/"):
      msg+= "    STATS/" + f + "\n"
  for f in os.listdir(os.path.dirname(__file__)+"/JSON/ARCHIVES/"):
      msg+= "    ARCHIVES/" + f + "\n"
  msg+= "```"
  await message.delete()
  await message.channel.send(msg)


# `!getDB <path//filename>`: donne la base de données;
async def getDB(message):
    # Rewrite
    filename = message.content.split(" ")[1]
    dirname = os.path.dirname(__file__)
    if await lengthVerificatorWError(message, "!getDB <path//filename>"):
        if os.path.exists(dirname+"/JSON/"+filename):
            if len(filename.split("//")) == 1 or len(filename.split("/")) == 1:
                file = discord.File(dirname+"/JSON/"+filename)  # an image in the same folder as the main bot file
                embed = discord.Embed()  # any kwargs you want here
                embed.set_image(url="attachment://" + filename.split("//")[-1])
                # filename and extension have to match (ex. "thisname.jpg" has to be "attachment://thisname.jpg")
                await message.delete()
                await message.channel.send(embed=embed, file=file)
            else:
                msg = "```!getDB <path//filename>```"
                msg += "\nNo authorised access to: `" + filename + "`"
                await message.channel.send(msg)
        else:
            msg = "```!getDB <path//filename>```"
            msg += "\nNo file with this path: `" + filename + "`"
            await message.channel.send(msg)

# !printDB <DB>
# affiche les données d'une base de données
async def printDB(message):
  await message.delete()
  if lengthVerificatorWError(message, "!printDB <DB>"):
    await dbg.printDB(message.channel, message.content.split(" ")[1])

# `!getLog [date]`: donne les logs [par défaut, du jour en cours];
async def getLog(message):
    # Rewrite
    filename = os.path.dirname(__file__)+"/LOGS/"+date.today().strftime("%Y-%m-%d")
    if len(message.content.split(" ")) > 1:
        filename = os.path.dirname(__file__) + "/LOGS/" + datetime.strptime(message.content.split(" ")[1],"%Y-%m-%d")
    if os.path.exists(filename):
        file = discord.File(filename)
        embed = discord.Embed()
        embed.set_image(url="attachment://log.txt")
        await message.delete()
        await message.channel.send(embed=embed, file=file)
    else:
        msg = "```!getLog [date]```"
        msg += "\nNo file with this path: `" + filename + "`"
        await message.channel.send(msg)


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
    player = getPlayerFromRoles(user)

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

    lf_members = f.loadData(S_ACTIVE_PLAYERS)
    for m in lf_members:
      if user.get_role(rolesIDs[m]) is not None and m in message.content.lower():
        is_concerned = True



    
    ### ----- ###
    ### Aides ###
    ### ----- ###

    
    #`!help`
    # affiche les commandes;
    if message.content.upper().startswith("!HELP AIDE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 0)
    elif message.content.upper().startswith("!HELP ALLIANCE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 1)
    elif message.content.upper().startswith("!HELP CHASSE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 2)
    elif message.content.upper().startswith("!HELP CONVOI"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 3)
    elif message.content.upper().startswith("!HELP FLOOD"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 4)
    elif message.content.upper().startswith("!HELP JOUEUR"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 5)
    elif message.content.upper().startswith("!HELP PACTE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 6)
    elif message.content.upper().startswith("!HELP DEV"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message, 7)
    elif message.content.upper().startswith("!HELP"): 
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await help(message)

      #`!templatePlayer`
      # donne la fiche à remplir pour enregistrer un joueur;
    elif message.content.upper().startswith("!TEMPLATEPLAYER"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await templatePlayer(message)
      else:
        await errorRole(message,["bot admin access"])

    # `!templatePacte`
    # donne la commande à remplir pour enregistrer un pacte;
    elif message.content.upper().startswith("!TEMPLATEPACTE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, diplo]):
        await templatePacte(message)
      else:
        await errorRole(message,["bot admin access", "diplo"])

    # `!getDbNames`: donne les noms des bases de données;
    elif message.content.upper().startswith("!GETDBNAMES"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await getDbNames(message)
      else:
        await errorRole(message,["bot admin access"])

    # `!getDB <path//filename>`: donne la base de données;
    elif message.content.upper().startswith("!GETDB"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await getDB(message)
      else:
        await errorRole(message,["bot admin access"])

    elif message.content.upper().startswith("!GETLOG"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await getLog(message)
      else:
        await errorRole(message,["bot admin access"])
    
    ### -------- ###
    ### Alliance ###
    ### -------- ###

    
    # `!printAlliance`
    # affiche les données de l'alliance;
    elif message.content.upper().startswith("!PRINTALLIANCE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, superReader, membre]):
        await printAlliance(message)
      else:
        await errorRole(message,["bot admin access", "bot super-reader acces", "membre"])

    # `!setTDC <tdc>`
    # modifie la quantité de TDC de l'alliance;
    elif message.content.upper().startswith("!SETTDCALLY"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer]):
        await setTDCAlly(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    # `!setNbMember <quantité>`
    # modifie le nombre de joueurs de l'alliance;
    elif message.content.upper().startswith("!SETNBMEMBRE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer]):
        await setNBMembre(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    # `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie le bonus d'alliance;
    elif message.content.upper().startswith("!SETBONUSALLY"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer]):
        await setBonusAlly(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    # `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie les stats de l'alliance;
    elif message.content.upper().startswith("!SETALLY"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer]):
        await setAlly(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    
    ### ------- ###
    ### Chasses ###
    ### ------- ###

    
    # `!printChasses <joueur>`
    # affiche les chasses d'un joueur
    elif message.content.upper().startswith("!PRINTCHASSES"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      await printChasses(message)
      if checkRoles(message, [admin, writer]):
        await setAlly(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    # `!chasse [joueur] <quantité>`
    # enregistre une chasse;
    elif message.content.upper().startswith("!CHASSE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await chasse(message, player)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

  
      ### ------- ###
      ### Convois ###
      ### ------- ###

  
    # `!convoisEnCours`
    # affiche les convois en cours;
    elif message.content.upper().startswith("!CONVOISENCOURS"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, superReader, membre]):
        await printConvoisEnCours(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`
      # ajoute un convoi;
    elif message.content.upper().startswith("!CONVOI"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await convoi(message, player)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!autoProd [joueur] <pomme> <bois> <eau>`
      # met à jour un convoi avec l'autoprod d'un joueur;
    elif message.content.upper().startswith("!AUTOPROD"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await autoProd(message, player)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!demandeConvoi <joueur> <C1/C2> <pomme> <bois> <eau>`
      # ajoute un convoi à la liste des convois en cours;
    elif message.content.upper().startswith("!DEMANDECONVOI"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, membre]):
        await demandeConvoi(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "membre"])

        # `!recapRessources [yyyy-mm-dd]`
        # calcul le récapitulatif des ressources récoltées de la journée;
    elif message.content.upper().startswith("!RECAPRESSOURCES"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await recapRSS(message)
      else:
        await errorRole(message,["bot admin access"])


        # `!printRecapRessources`
        # affiche le récapitulatif des ressources récoltées de la journée;
    elif message.content.upper().startswith("!PRINTRECAPRESSOURCES"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await printRecapRSS(message)
      else:
        await errorRole(message,["bot admin access"])
    
      ### --------------- ###
      ### Floods externes ###
      ### --------------- ###

    
      # `!floodExtR [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`
      # enregistre un flood externe reçu;
    elif message.content.upper().startswith("!FLOODEXTR"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await floodExtR(message, player)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!floodExtD [date] [joueurLF] <joueurExtérieur> <ally> <quantité>`
      # enregistre un flood externe donné;
    elif message.content.upper().startswith("!FLOODEXTD"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await floodExtD(message, player)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!futursfloods`
      # affiche les floods à faire;
    elif message.content.upper().startswith("!FUTURSFLOODS"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, superReader, membre]):
        await printFloodsFuturs(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!printFloodsExt`
      # affiche les floods externes;
    elif message.content.upper().startswith("!PRINTFLOODSEXT"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, superReader]):
        await printFloodsExt(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`
      # enregistre un don de tdc (butin de guerre par exemple)
    elif message.content.upper().startswith("!DONTDC"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer]):
        await donTDC(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access"])

    
      ### ------- ###
      ### Joueurs ###
      ### ------- ###

    
      # `!printPlayer <joueur>`
      # affiche les données d'un joueur.
    elif message.content.upper().startswith("!PRINTPLAYER"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await printPlayer(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!player \\n <templatePlayer>`
      # ajoute un nouveau pacte
    elif message.content.upper().startswith("!PLAYER"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await player(message)
      else:
        await errorRole(message,["bot admin access"])

      # `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`
      # modifie l'armée d'un joueur.
    elif message.content.upper().startswith("!SETARMY"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setArmy(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`
      # modifie la race d'un joueur.
    elif message.content.upper().startswith("!SETRACE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setRace(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

        # `!setTDCExploité <joueur> <C1/C2> <tdcExploté>`:
        # modifie le tdc exploité d'un joueur;
    elif message.content.upper().startswith("!SETTDCEXPLOITÉ"):
        f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
        if checkRoles(message, [admin, writer, is_concerned]):
            await setTDCExploit(message,player)
        else:
            await errorRole(message, ["bot admin access", "bot writer access", "joueur concerné"])

        # `!setTDC <joueur> <C1/C2> <tdcExploté>`:
        # modifie le tdc d'un joueur;
    elif message.content.upper().startswith("!SETTDC "):
        f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
        if checkRoles(message, [admin, writer, is_concerned]):
            await setTDC(message)
        else:
            await errorRole(message, ["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsColo <joueur> <colo> <oe> <ov> <tdp>`
      # modifie les stats d'une colonie d'un joueur.
    elif message.content.upper().startswith("!SETSTATSCOLO"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setStatsColo(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setVassal <joueurVassalisé> <coloVassalisée> <vassal> <coloVassal> <pillage>`
      # modifie le vassal d'une colonie d'un joueur.
    elif message.content.upper().startswith("!SETVASSAL"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setVassal(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`
      # modifie les statistiques générales d'un joueur.
    elif message.content.upper().startswith("!SETSTATSPLAYER"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setStatsPlayer(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`
      # modifie le héros d'un joueur.
    elif message.content.upper().startswith("!SETHERO"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, is_concerned]):
        await setHero(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "joueur concerné"])

    #`!setActivePlayers <joueur1> ... <joueurN>`
    # définit les joueurs actifs de la LF;
    elif message.content.upper().startswith("!SETACTIVEPLAYERS"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await setActivePlayers(message)
      else:
        await errorRole(message,["bot admin access"])

    #`!getActivePlayers`
    # donne les joueurs actifs de la LF;
    elif message.content.upper().startswith("!GETACTIVEPLAYERS"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin]):
        await getActivePlayers(message)
      else:
        await errorRole(message,["bot admin access"])

    
      ### ------ ###
      ### Pactes ###
      ### ------ ###

    
      # `!printPactes`
      # affiche les pactes;
    elif message.content.upper().startswith("!PRINTPACTES"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, writer, superReader]):
        await printPactes(message)
      else:
        await errorRole(message,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!endPacte <ally>`
      # clôt un pacte;
    elif message.content.upper().startswith("!ENDPACTE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, diplo]):
        await endPacte(message)
      else:
        await errorRole(message,["bot admin access", "diplo"])

      # `!pacte <ally> <type-guerre> <type-commerce> <start> <end> \\n <titre> \\n <description>`
      # ajoute un nouveau pacte
    elif message.content.upper().startswith("!PACTE"):
      f.log(rank=0, prefixe="[CMD]", message=message.content, suffixe="")
      if checkRoles(message, [admin, diplo]):
        await pacte(message)
      else:
        await errorRole(message,["bot admin access", "diplo"])

    
      ### ------ ###
      ### ERRORS ###
      ### ------ ###

    
    elif message.content.startswith("!"):
      f.log(rank=0, prefixe="[ERROR]", message="Unknown error - " + message.content, suffixe="")
      await error(
          message,
          "Commande inconnue. `!help` pour voir la liste des commandes disponibles."
      )  #error



#__________________________________________________#
## Run ##
#__________________________________________________#

#On va maintenir le bot en activité
keep_alive()
#On lance le bot
f.log(rank=0, prefixe="[START]", message="Bot launching", suffixe="")
bot.run(token)
