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
S_ALLIES_PLAYERS = "STATS//Stats_AlliesNames.json"

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

# Droits
PERMISSION_ADMIN=           0
PERMISSION_PRIVILEGED=      1
PERMISSION_CONSEIL=         2
PERMISSION_ONLY_SELF_CMD=   3
PERMISSION_MEMBER=          4
PERMISSION_EXT_PRIVILEGE=   5

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
`!chasse [joueur] <quantité>`: enregistre une chasse;
`!simuChasse [joueur] <tdc_initial> <vitesse_de_traque> <C1/C2> <nombre_de_chasses>`: donne la simulation de chasse pour le joueur;
`!simuChassePex [joueur] <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`: donne la simulation de chasse pour pex un maximum pour le joueur""",
    """### Commandes Convois
`!convoisEnCours`: affiche les convois en cours;
`!autoProd [joueur] <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
`!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`: enregistre une livraison;
`!demandeConvoi [joueur] <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute une nouvelle demande à la liste des convois en cours (attention, un convoi par joueur);
`!recapRessources`: calcul le récapitulatif des ressources récoltées de la journée;
`!printRecapRessources`: affiche le récapitulatif des ressources récoltées de la journée;
`!printConvoisJour [date:aaaa-mm-jj]`: affiche les convois effectués sur cette date""",
    """### Commandes Floods externes
`!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe reçu;
`!floodExtD [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe donné;
`!futursfloods`: affiche les floods à faire; 
`!printFloodsExt [alliance]`: affiche les floods externes;
`!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple);
`!tpsFloodLF [joueur] <C1/C2> <x_cible> <y_cible>`: affiche le temps de flood d'un joueur;
`!tpsFloodExt <x_floodeur> <y_floodeur> <x_cible> <y_cible> <va>`: affiche le temps de flood;
`!listeFloodExtR <x_floodeur> <y_floodeur> <va>`: affiche les durées de flood d'un joueur sur la LF;
`!listeFloodExtD <x_floodé> <y_floodé>`: affiche les durées de flood de la LF sur un joueur;
`!listeDateFloodLF <x_floodeur> <y_floodeur> <va> <date_de_lancement>`: affiche les dates de flood d'un joueur sur la LF -- <date_de_lancement> au format année-mois-jour-heure-minute-seconde, ex: 2024-10-25-15-36-24 pour le 25/10/2024 à 15h 36min 24s;""",
    """### Commandes Joueurs
`!printPlayer <joueur>`: affiche les données d'un joueur.
`!renameColo [joueur] <C1/C2> \\n <nom avec espaces>`: modifie le nom de la colo d'un joueur d'un joueur;
`!setArmy [joueur] <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`: modifie l'armée d'un joueur;
`!setTDCExploité [joueur] <C1/C2> <tdcExploité>`: modifie le tdc exploité d'un joueur;
`!setTDC [joueur] <C1/C2> <tdc>`: modifie le tdc d'un joueur;
`!setRace [joueur] <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur;
`!setStatsColo [joueur] <C1/C2> <oe> <ov> <tdp>`: modifie les stats d'une colonie d'un joueur;
`!setVassal [joueurVassalisé] <coloVassalisée:C1/C2> <vassal> <coloVassal:C1/C2> <pillageDuVassal>`: modifie le vassal d'une colonie d'un joueur;
`!clearVassal [joueurVassalisé] <coloVassalisée>`: retire le vassal d'une colonie d'un joueur;
`!setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur;
`!setHero [joueur] <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`: modifie le héros d'un joueur;
`!player \\n <templatePlayer>`: ajoute un nouveau joueur;
`!player <nom>`: ajoute un joueur avec des valeurs par défaut;
`!allié \\n <templatePlayer>`: ajoute un nouvel allié;
`!setActivePlayers <joueur1> ... <joueurN>`: définit les joueurs actifs de la LF;
`!getTDCExploités`: donne les tdc exploités des joueurs actifs de la LF;
`!getActivePlayers`: donne les joueurs actifs de la LF;
`!optiMandi [joueur]`: dit s'il faut augmenter les mandibules ou pondre des JTk pour un joueur;
`!optiCara [joueur]`: dit s'il faut augmenter la carapace ou pondre des JS pour un joueur;
`!setCoord [joueur] <C1/C2> <x> <y>`: modifie les coordonnées d'une des colonies d'un joueur;
`!setVA [joueur] <va>`: modifie la vitesse d'attaque d'un joueur;""",
    """### Commandes Pactes
`!printPactes`: affiche les pactes;
`!endPacte`: clôt un pacte;
`!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> [end] \\n <titre> \\n <description>`: ajoute un nouveau pacte; """,
    """### Commandes Dev
`!getDbNames`: donne les noms des bases de données;
`!getDB <path//filename>`: donne la base de données;
`!getLog [date:aaaa-mm-jj]`: donne les logs [du jour en cours, par défaut];"""
]


#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

# ERROR HANDLER
# error sender
async def error(channel, command, errorMsg: str):
    f.log(rank=1, prefixe="[ERROR]", message=command, suffixe=errorMsg)
    await channel.send(errorMsg)



def isAuthorized(user, level_needed:int, rw:str,  self_command:bool) -> bool:
    # PERMISSION_ADMIN=           0
    # PERMISSION_PRIVILEGED=      1
    # PERMISSION_ONLY_SELF_CMD=   2
    # PERMISSION_MEMBER=          3
    # PERMISSION_EXT_PRIVILEGE=   4

    is_authorized= False
    player = getPlayerFromRoles(user)

    admin=          user.get_role(rolesIDs["bot admin access"]) is not None
    writer=         user.get_role(rolesIDs["bot writer access"]) is not None
    superReader=    user.get_role(rolesIDs["bot super-reader access"]) is not None
    reader=         user.get_role(rolesIDs["bot reader access"]) is not None

    chef=       user.get_role(rolesIDs["chef"]) is not None
    second=     user.get_role(rolesIDs["second"]) is not None
    recruteur=  user.get_role(rolesIDs["recruteur"]) is not None
    diplo=      user.get_role(rolesIDs["diplomate"]) is not None
    conseil=    chef or second or recruteur or diplo
    membre=     user.get_role(rolesIDs["membre"]) is not None

    grenier =   user.get_role(rolesIDs["grenier"]) is not None
    chasseur =  user.get_role(rolesIDs["chasseur"]) is not None
    guerrier =  user.get_role(rolesIDs["guerrier"]) is not None

    if admin:                                                               is_authorized= True
    elif    superReader and     level_needed < 2    and "R" in rw.upper():  is_authorized= True
    elif    conseil     and     level_needed < 2:                           is_authorized= True
    elif    membre      and     level_needed < 3:                           is_authorized= True
    elif    membre      and     level_needed < 4    and self_command:       is_authorized= True
    elif    writer      and     level_needed < 5    and "W" in rw.upper():  is_authorized= True
    elif    reader      and     level_needed < 5    and "R" in rw.upper():  is_authorized= True

    if not is_authorized:
        f.log(rank=1, prefixe="[ERROR]", message="No permission", suffixe="")
    return is_authorized



# length verification
async def lengthVerificatorWerror(messageCMD, channel, command):
  if len(messageCMD.upper().split(" ")) == len(command.upper().split(" ")):
    return True
  elif len(messageCMD.upper().split(" ")) < len(command.upper().split(" ")):
    f.log(rank=1, prefixe="[ERROR]", message="Peu d'arguments ont été donnés:`" + command + "`", suffixe="")
    await error(channel, command,"Peu d'arguments ont été donnés:`" + command + "`")
    return False
  elif len(messageCMD.upper().split(" ")) > len(command.upper().split(" ")):
    f.log(rank=1, prefixe="[ERROR]", message="Trop d'arguments ont été donnés:`" + command + "`", suffixe="")
    await error(channel, command,"Trop d'arguments ont été donnés:`" + command + "`")
    return False


async def lengthVerificator(messageCMD, command):
  res = False
  if len(messageCMD.upper().split(" ")) == len(command.upper().split(" ")):
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

async def reactMSG(message, error: bool):
    await message.add_reaction('🤖')
    if error: await message.add_reaction('👎')
    else: await message.add_reaction('👍')

#__________________________________________________#
## AIDE ##
#__________________________________________________#


# `!help`: affiche les commandes;
async def help(playerObj, page=None):
    global helpMSG
    #await message.delete()
    for i in range(len(helpMSG)):
        if page == None or page+1 == i:
            await playerObj.send(helpMSG[i])


# `!templatePlayer`: donne la fiche à remplir pour enregistrer un joueur;
async def templatePlayer(playerObj, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
        msg = f.loadData(CONST_TEMPLATES)["player"]
        #await message.delete()
        await playerObj.send(msg)
    else:
        await error(playerObj, "`!templatePlayer`", "Permissions insuffisantes")


# `!templatePacte`: donne la commande à remplir pour enregistrer un pacte;
async def templatePacte(playerObj, user):
    if isAuthorized(user=user, level_needed=PERMISSION_CONSEIL, rw="R", self_command=False):
        msg = f.loadData(CONST_TEMPLATES)["pacte"]
        #await message.delete()
        await playerObj.send(msg)
    else:
        await error(playerObj, "`!templatePacte`", "Permissions insuffisantes")


#__________________________________________________#
## ALLIANCE ##
#__________________________________________________#


# `!printAlliance`: affiche les données de l'alliance;
async def printAlliance(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False):
        if await lengthVerificatorWerror(command, channel, "!printAlliance"):
            msg = alliance.printAlliance()
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                await channel.send(msg)
    else:
        await error(channel, command, "Permissions insuffisantes")



# `!setTDCAlly <tdc>`: modifie la quantité de TDC de l'alliance;
async def setTDCAlly(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="W", self_command=False):
        if await lengthVerificatorWerror(command, channel, "!setTDCAlly <tdc>"):
            msg = alliance.setTDC(f.getNumber(command.split(" ")[1]))
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                await channel.send(msg)
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!setNBMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
async def setNBMembre(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="W", self_command=False):
        if await lengthVerificatorWerror(command, channel, "!setMembers <quantité>"):
            msg = alliance.setNBMembre(f.getNumber(command.split(" ")[1]))
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                await channel.send(msg)
    else:
        await error(channel, command, "Permissions insuffisantes")



# `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie le bonus d'alliance;
async def setBonusAlly(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="W", self_command=False):
        if await lengthVerificatorWerror(command, channel, "!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>"):
            msg = alliance.setBonusAlly(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                await channel.send(msg)
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie les stats de l'alliance;
async def setAlly(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="W", self_command=False):
        if await lengthVerificatorWerror(command, channel,"!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>"):
            msg = alliance.setAlly(f.getNumber(command.split(" ")[1]),
                                   command.split(" ")[2],
                                   command.split(" ")[3],
                                   command.split(" ")[4],
                                   command.split(" ")[5],
                                   command.split(" ")[6])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                await channel.send(msg)
    else:
        await error(channel, command, "Permissions insuffisantes")


#__________________________________________________#
## CHASSES ##
#__________________________________________________#


# `!printChasses <joueur>`: affiche les chasses d'un joueur
async def printChasses(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!chasse [joueur] <quantité>`"
    if await lengthVerificator(command, "!printChasses [joueur]"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            msg = chasses.printChasses(command.split(" ")[1])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                for m in f.splitMessage(msg):
                    await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")
    elif await lengthVerificator(command, "!printChasses"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            msg = chasses.printChasses(command.split(" ")[1])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                for m in f.splitMessage(msg):
                    await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;
async def chasse(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!chasse [joueur] <quantité>`"
    if await lengthVerificator(command, "!chasse [joueur] <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = chasses.chasse(
                command.split(" ")[1],
                f.getNumber(command.split(" ")[2]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!chasse <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas chasser!"
            else:
                msg = chasses.chasse(
                    player,
                    f.getNumber(command.split(" ")[1]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!simuChasse [joueur] <tdc_initial> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`: donne la simulation de chasse pour le joueur
async def simuChasse(playerObj, command, user, player):
    msg = ["ERR: trop ou pas assez d'arguments dans la commande: `!simuChasse [joueur] <tdc_initial> <vitesse_de_traque> <C1/C2> <nombre_de_chasses>`"]
    if await lengthVerificator(command, "!simuChasse [joueur] <tdc_initial> <vitesse_de_traque> <C1/C2> <nombre_de_chasses>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            msg = chasses.simuChasse(
                command.split(" ")[1],
                f.getNumber(command.split(" ")[2]),
                command.split(" ")[4],
                command.split(" ")[3],
                command.split(" ")[5])
        else:
            await error(playerObj, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!simuChasse <tdc_initial> <vitesse_de_traque> <C1/C2> <nombre_de_chasses>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas chasser!"
            else:
                msg = chasses.simuChasse(
                    player,
                    f.getNumber(command.split(" ")[1]),
                    command.split(" ")[3],
                    command.split(" ")[2],
                    command.split(" ")[4])
        else:
            await error(playerObj, command, "Permissions insuffisantes")

    if msg[0].startswith("ERR:"):
        await error(playerObj, command, msg[0])
    else:
        #await message.delete()
        for m in msg:
            await playerObj.send(m)

# !simuChassePex [joueur] <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`: donne la simulation de chasse pour pex un maximum pour le joueur
async def simuChassePex(playerObj, command, user, player):
    msg = ["ERR: trop ou pas assez d'arguments dans la commande: `!simuChassePex [joueur] <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`"]
    if await lengthVerificator(command, "!simuChassePex [joueur] <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            msg = chasses.simuChassePex(
                command.split(" ")[1],
                f.getNumber(command.split(" ")[2]),
                f.getNumber(command.split(" ")[3]),
                command.split(" ")[5],
                command.split(" ")[4],
                command.split(" ")[6])
        else:
            await error(playerObj, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!simuChassePex <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas chasser!"
            else:
                msg = chasses.simuChassePex(
                    player,
                    f.getNumber(command.split(" ")[1]),
                    f.getNumber(command.split(" ")[2]),
                    command.split(" ")[4],
                    command.split(" ")[3],
                    command.split(" ")[5])
        else:
            await error(playerObj, command, "Permissions insuffisantes")

    if msg[0].startswith("ERR:"):
        await error(playerObj, command, msg[0])
    else:
        # await message.delete()
        for m in msg:
            await playerObj.send(m)

#__________________________________________________#
## CONVOIS ##
#__________________________________________________#


# `!convoisEnCours`: affiche les convois en cours;
async def printConvoisEnCours(channel, command, user):
    if await lengthVerificatorWerror(command, channel, "!printConvois"):
        if isAuthorized(user=user, level_needed=PERMISSION_MEMBER, rw="R", self_command=False):
            msg = convois.printConvoisEnCours()
            if msg.startswith("ERR:"):
              await error(channel, command, msg)
            else:
              #await message.delete()
              for m in f.splitMessage(msg):
                await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")


# `!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`: ajoute un convoi;
async def convoi(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`"
    if await lengthVerificator(command, "!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = convois.convoi(
                command.split(" ")[1],
                command.split(" ")[2],
                f.getNumber(command.split(" ")[3]),
                f.getNumber(command.split(" ")[4]),
                f.getNumber(command.split(" ")[5]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!convoi <convoyé> <pomme> <bois> <eau>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas convoyer!"
            else:
                msg = convois.convoi(
                    player,
                    command.split(" ")[1],
                    f.getNumber(command.split(" ")[2]),
                    f.getNumber(command.split(" ")[3]),
                    f.getNumber(command.split(" ")[4]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!demandeConvoi [joueur] <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;
async def demandeConvoi(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!demandeConvoi [joueur] <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`"
    if await lengthVerificator(command, "!demandeConvoi [joueur] <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = convois.demandeConvoi(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                f.getNumber(command.split(" ")[5]),
                f.getNumber(command.split(" ")[6]),
                f.getNumber(command.split(" ")[7]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!demandeConvoi <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>") :
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas demander de convois!"
            else:
                msg = convois.demandeConvoi(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    command.split(" ")[3],
                    f.getNumber(command.split(" ")[4]),
                    f.getNumber(command.split(" ")[5]),
                    f.getNumber(command.split(" ")[6]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
      await error(channel, command, msg)
    else:
      #await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)


# `!autoProd [joueur] <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
async def autoProd(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!autoProd [joueur] <pomme> <bois> <eau>`"
    if await lengthVerificator(command, "!autoProd [joueur] <pomme> <bois> <eau>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = convois.autoProd(
                command.split(" ")[1],
                f.getNumber(command.split(" ")[2]),
                f.getNumber(command.split(" ")[3]),
                f.getNumber(command.split(" ")[4]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!autoProd <pomme> <bois> <eau>") :
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas vous autoconvoyer!"
            else:
                msg = convois.autoProd(
                    player,
                    f.getNumber(command.split(" ")[1]),
                    f.getNumber(command.split(" ")[2]),
                    f.getNumber(command.split(" ")[3]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
      await error(channel, command, msg)
    else:
      #await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)

# `!recapRessources [yyyy-mm-dd]``: calcul le récapitulatif des ressources récoltées de la journée;
async def recapRSS(channel, command):
    channel = bot.get_channel(1276232505116196894)
    msg = ""
    if len(command.split(" ")) > 1:
        msg = convois.repartitionRessources(command.split(" ")[1])
    else:
        msg = convois.repartitionRessources(date.today().strftime("%Y-%m-%d"))
        msg+= "\n||from cmd||"
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# `!printRecapRessources`: affiche le récapitulatif des ressources récoltées de la journée;
async def printRecapRSS(channel, command):
    #channel = bot.get_channel(1276232505116196894)
    msg = ""
    if len(command.split(" ")) > 1:
        msg = convois.printRessourcesPartagees(command.split(" ")[1])
    else:
        msg = convois.printRessourcesPartagees(date.today().strftime("%Y-%m-%d"))
        msg+= "\n||from cmd||"
    if msg.startswith("ERR:"):
      await error(channel, command, msg)
    else:
      #await message.delete()
      for m in f.splitMessage(msg):
        await channel.send(m)

async def printConvoisJour(channel, command):
    channel = bot.get_channel(1278074306391183452)
    msg = ""
    if len(command.split(" ")) > 1:
        msg = convois.convoisDuJour(command.split(" ")[1])
    else:
        msg = convois.convoisDuJour(date.today().strftime("%Y-%m-%d"))
        msg+= "\n||from cmd||"
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

#__________________________________________________#
## FLOODS EXTERNES ##
#__________________________________________________#


# `!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`: enregistre un flood externe reçu;
async def floodExtR(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`"
    if await lengthVerificator(command, "!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = floods.floodExtR(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                f.getNumber(command.split(" ")[5]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!floodExtR [date/joueurLF] <joueurExtérieur> <ally> <quantité>"):
        try:
            datetime.strptime(command.split(" ")[1], "%Y-%m-%d")
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W",self_command=player.upper() in command.upper()):
                msg = floods.floodExtR(
                    command.split(" ")[1],
                    player,
                    command.split(" ")[2],
                    command.split(" ")[3],
                f.getNumber(command.split(" ")[4]))
            else:
                await error(channel, command, "Permissions insuffisantes")

        except:
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
                if player is None:
                    msg = "ERR: vous ne pouvez pas enregistrer de floods!"
                else:
                    msg = floods.floodExtR(
                        datetime.now().strftime("%Y-%m-%d"),
                        command.split(" ")[1],
                        command.split(" ")[2],
                        command.split(" ")[3],
                    f.getNumber(command.split(" ")[4]))
            else:
                await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!floodExtR <joueurExtérieur> <ally> <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas enregistrer de floods!"
            else:
                msg = floods.floodExtR(
                    datetime.now().strftime("%Y-%m-%d"),
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    f.getNumber(command.split(" ")[3]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!floodExtD [floodeur] <C1/C2> <ally> <quantité> <floodé> <C1/C2>`: enregistre un flood externe donné;
async def floodExtD(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`"
    if await lengthVerificator(command, "!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = floods.floodExtD(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                f.getNumber(command.split(" ")[5]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!floodExtR [date/joueurLF] <joueurExtérieur> <ally> <quantité>"):
        try:
            datetime.strptime(command.split(" ")[1], "%Y-%m-%d")
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
                msg = floods.floodExtD(
                    command.split(" ")[1],
                    player,
                    command.split(" ")[2],
                    command.split(" ")[3],
                    f.getNumber(command.split(" ")[4]))
            else:
                await error(channel, command, "Permissions insuffisantes")
        except:
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
                if player is None:
                    msg = "ERR: vous ne pouvez pas enregistrer de floods!"
                else:
                    msg = floods.floodExtD(
                        datetime.now().strftime("%Y-%m-%d"),
                        command.split(" ")[1],
                        command.split(" ")[2],
                        command.split(" ")[3],
                        f.getNumber(command.split(" ")[4]))
            else:
                await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!floodExtR <joueurExtérieur> <ally> <quantité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas enregistrer de floods!"
            else:
                msg = floods.floodExtD(
                    datetime.now().strftime("%Y-%m-%d"),
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    f.getNumber(command.split(" ")[3]))
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!futursfloods`: affiche les floods à faire;
async def printFloodsFuturs(channel, command, user):
    if await lengthVerificatorWerror(command, channel, "!floodsFuturs"):
        if isAuthorized(user=user, level_needed=PERMISSION_MEMBER, rw="R", self_command=False):
            msg = floods.printFloodsFuturs()
            if msg.startswith("ERR:"):
              await error(channel, command, msg)
            else:
              #await message.delete()
              for m in f.splitMessage(msg):
                await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")


# `!printFloodsExt`: affiche les floods externes;
async def printFloodsExt(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False):
        msg= ""
        if len(command.split(" ")) == 1:
            msg = floods.printFloodsExt()
        elif len(command.split(" ")) == 2:
            msg = floods.printFloodsExtAlly(command.split(" ")[1])
        if msg.startswith("ERR:"):
            await error(channel, command, msg)
        else:
            #await message.delete()
            for m in f.splitMessage(msg):
                await channel.send(m)
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple)
async def donTDC(channel, command, user):
    if await lengthVerificatorWerror(command, channel,"!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>"):
        if isAuthorized(user=user, level_needed=PERMISSION_CONSEIL, rw="W", self_command=False):
            msg = floods.donTDC(
                command.split(" ")[1],
                command.split(" ")[2],
                f.getNumber(command.split(" ")[3]),
                command.split(" ")[4])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                for m in f.splitMessage(msg):
                    await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")


# `!tpsFloodLF [joueur] <C1/C2> <x_cible> <y_cible>`
# affiche le temps de flood d'un joueur; LF_attack(joueur:str, colo:str, x:str, y:str)
async def tpsFloodLF(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!tpsFloodLF [joueur] <C1/C2> <x_cible> <y_cible>`"
    if await lengthVerificator(command, "!tpsFloodLF [joueur] <C1/C2> <x_cible> <y_cible>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            msg = floods.LF_attack(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if await lengthVerificator(command, "!tpsFloodLF <C1/C2> <x_cible> <y_cible>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas tester de floods!"
            else:
                msg = floods.LF_attack(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    command.split(" ")[3])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

#`!tpsFloodExt <x_floodeur> <y_floodeur> <x_cible> <y_cible> <va>`
# affiche le temps de flood; simple_attack(x:str, y:str, x_target:str, y_target:str, va:str)
async def tpsFloodExt(channel, command, user):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!tpsFloodExt <x_floodeur> <y_floodeur> <x_cible> <y_cible> <va>`"
    if await lengthVerificator(command, "!tpsFloodExt <x_floodeur> <y_floodeur> <x_cible> <y_cible> <va>"):
        if isAuthorized(user=user, level_needed=PERMISSION_EXT_PRIVILEGE, rw="R", self_command=False):
            msg = floods.simple_attack(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                command.split(" ")[5])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

#`!listeFloodExtR <x_floodeur> <y_floodeur> <va>`:
# affiche les durées de flood d'un joueur sur la LF; attacks_on_LF(x:str, y:str, va:str)
async def listeFloodExtR(channel, command, user):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!listeFloodLF <x_floodeur> <y_floodeur> <va>`"
    if await lengthVerificator(command, "!listeFloodLF <x_floodeur> <y_floodeur> <va>"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False):
            msg = floods.attacks_on_LF(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


#`!listeFloodExtD <x_floodé> <y_floodé>`:
# affiche les durées de flood de la LF sur un joueur; attacks_from_LF(x:str, y:str, va:str)
async def listeFloodExtD(channel, command, user):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!listeFloodExtD <x_floodeur> <y_floodeur>`"
    if await lengthVerificator(command, "!listeFloodExtD <x_floodeur> <y_floodeur>"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False in command.upper()):
            msg = floods.attacks_from_LF(
                command.split(" ")[1],
                command.split(" ")[2])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# `!listeDateFloodLF <x_floodeur> <y_floodeur> <va> <date_de_lancement>`
# affiche les dates de flood d'un joueur sur la LF -- <date_de_lancement> au format année-mois-jour-heure-minute-seconde, ex: 2024-10-25-15-36-24 pour le 25/10/2024 à 15h 36min 24s; attacks_on_LF_arrivee(x:str, y:str, va:str, date:str)""",
async def listeDateFloodLF(channel, command, user):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!listeDateFloodLF <x_floodeur> <y_floodeur> <va> <date_de_lancement>`"
    if await lengthVerificator(command, "!listeDateFloodLF <x_floodeur> <y_floodeur> <va> <date_de_lancement>"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False):
            msg = floods.attacks_on_LF_arrivee(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

#__________________________________________________#
## PLAYERS ##
#__________________________________________________#


# `!printPlayer <joueur>`: affiche les données d'un joueur.
async def printPlayer(playerObj, command, user, player):
    msg= "ERR:"
    if await lengthVerificator(command, "!printPlayer <joueur>"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=player.upper() in command.upper()):
            msg = joueurs.printPlayer(command.split(" ")[1])
        else:
            await error(playerObj, command, "Permissions insuffisantes")
    if await lengthVerificator(command, "!printPlayer"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=True):
            msg = joueurs.printPlayer(player)
        else:
            await error(playerObj, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
      await error(playerObj, command, msg)
    else:
      #await message.delete()
      for m in f.splitMessage(msg):
        await playerObj.send(m)


# `!player \n <templatePlayer>`: ajoute un nouveau pacte
async def addPlayer(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="W", self_command=False):
        if len(command.split("\n")) > 2:
            msg = joueurs.addPlayer(command)
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                for m in f.splitMessage(msg):
                    await channel.send(m)
        elif len(command.split(" ")) == 2:
            msg = joueurs.addDefaultUser(command.split(" ")[1])
            if msg.startswith("ERR:"):
                await error(channel, command, msg)
            else:
                #await message.delete()
                for m in f.splitMessage(msg):
                    await channel.send(m)
        else:
            await error(channel, command, "Erreur dans la commande: `!player \n <templatePlayer>` ou `!player <nom>`")
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!allié \\n <templatePlayer>`: ajoute un nouvel allié;
async def addAllie(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="W", self_command=False):
      if len(command.split("\n")) > 2:
        msg = joueurs.addAllie(command)
        if msg.startswith("ERR:"):
          await error(channel, command, msg)
        else:
          #await message.delete()
          for m in f.splitMessage(msg):
            await channel.send(m)
      else:
        await error(channel, command, "Erreur dans la commande: `!allié \n <templatePlayer>`")
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!renameColo [joueur] <C1/C2> \\n <nom avec espaces>`: modifie le nom de la colo d'un joueur d'un joueur
async def renameColo(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!renameColo [joueur] <C1/C2> \\n <nom avec espaces>`"
    if len(command.split("\n")[0].split(" ")) == 3: #"!renameColo [joueur] <C1/C2>"
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.renameColo(command.split("\n")[0].split(" ")[1],
                                     command.split("\n")[0].split(" ")[2],
                                     command.split("\n")[1])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if len(command.split("\n")[0].split(" ")) == 2: #"!renameColo <C1/C2>"
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas renommer vos colonies!"
            else:
                msg = joueurs.renameColo(
                                        player,
                                        command.split("\n")[0].split(" ")[1],
                                        command.split("\n")[1])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# `!setTDCExploité [joueur] <C1/C2> <tdcExploité>`: modifie le tdc exploité d'un joueur;
async def setTDCExploit(channel, command, user, player):
    msg = "ERR: trop ou pas assez d'arguments dans la commande: `!setTDCExploité [joueur] <C1/C2> <tdcExploité>`"
    if await lengthVerificator(command, "!setTDCExploité [joueur] <C1/C2> <tdcExploité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setTDCExploité(command.split(" ")[1],
                                         command.split(" ")[2],
                                         f.getNumber(command.split(" ")[3]))
        else:
            await error(channel, command, "Permissions insuffisantes")
    if await lengthVerificator(command, "!setTDCExploité <C1/C2> <tdcExploité>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if player is None:
                msg = "ERR: vous ne pouvez pas enregistrer de floods!"
            else:
                msg = joueurs.setTDCExploité(player,
                                             command.split(" ")[1],
                                             f.getNumber(command.split(" ")[2]))
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!setTDC [joueur] <C1/C2> <tdc>`: modifie le tdc d'un joueur;
async def setTDC(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !setTDC [joueur] <C1/C2> <tdc>"
    if await lengthVerificator(command, "!setTDC [joueur] <C1/C2> <tdc>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setTDC(
                command.split(" ")[1],
                command.split(" ")[2],
                f.getNumber(command.split(" ")[3]))
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setTDC <C1/C2> <tdc>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setTDC(
                    player,
                    command.split(" ")[1],
                    f.getNumber(command.split(" ")[2]))
            else:
                msg = "ERR: vous ne pouvez pas changer le tdc de votre colo!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!setArmy [joueur] <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`: modifie l'armée d'un joueur.
async def setArmy(playerObj, command, user, player):
    await playerObj.send("Commande effectuée:\n```"+command+"```")
    if len(command.split("\n")) > 1:
        msg = "ERR: Commande mal formulée - !setArmy [joueur] <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>"
        if len(command.split("\n")[0].split(" ")) == 3:
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
                msg = joueurs.setArmy(
                    command.split("\n")[0].split(" ")[1],
                    command.split("\n")[0].split(" ")[2],
                    command.split("\n")[1])
            else:
                await error(playerObj, command, "Permissions insuffisantes")
        if len(command.split("\n")[0].split(" ")) == 2:
            if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
                if not player is None:
                    msg = joueurs.setArmy(
                        player,
                        command.split("\n")[0].split(" ")[1],
                        command.split("\n")[1])
                else:
                    msg="ERR: vous ne pouvez pas changer votre armée!"
            else:
                await error(playerObj, command, "Permissions insuffisantes")
        if msg.startswith("ERR:"):
            await error(playerObj, command, msg)
        else:
            #await message.delete()
            for m in f.splitMessage(msg):
                await playerObj.send(m)
    else:
        await error(playerObj, command, "Erreur dans la commande: `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`")


# `!setRace [joueur] <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`: modifie la race d'un joueur.
async def setRace(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !setRace [joueur] <0:Abeille,1:Araignée,2:Fourmi,3:Termite>"
    if await lengthVerificator(command,"!setRace [joueur] <0:Abeille,1:Araignée,2:Fourmi,3:Termite>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setRace(
                command.split(" ")[1],
                command.split(" ")[2])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setRace <0:Abeille,1:Araignée,2:Fourmi,3:Termite>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setRace(
                    player,
                    command.split(" ")[1])
            else:
                msg = "ERR: vous ne pouvez pas changer votre race!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

  


# `!setStatsColo [joueur] <colo> <oe> <ov> <tdp>`: modifie les stats d'une colonie d'un joueur.
async def setStatsColo(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !setStatsColo [joueur] <colo> <oe> <ov> <tdp>"
    if await lengthVerificator(command,"!setStatsColo [joueur] <colo> <oe> <ov> <tdp>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setStatsColo(
                command.split(" ")[1],
                command.split(" ")[2],
                f.getNumber(command.split(" ")[3]),
                f.getNumber(command.split(" ")[4]),
                command.split(" ")[5])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setStatsColo <colo> <oe> <ov> <tdp>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setStatsColo(
                    player,
                    command.split(" ")[1],
                    f.getNumber(command.split(" ")[2]),
                    f.getNumber(command.split(" ")[3]),
                    command.split(" ")[4])
            else:
                msg="ERR: vous ne pouvez pas changer les statistiques de votre colo!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)



# `!setVassal [joueurVassalisé] <coloVassalisée> <vassal> <coloVassal> <pillageDuVassal>`: modifie le vassal d'une colonie d'un joueur.
async def setVassal(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !setVassal [joueurVassalisé] <coloVassalisée> <vassal> <coloVassal> <pillageDuVassal>"
    if await lengthVerificator(command, "!setVassal [joueurVassalisé] <coloVassalisée> <vassal> <coloVassal> <pillageDuVassal>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setVassal(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                command.split(" ")[5])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setVassal <coloVassalisée> <vassal> <coloVassal> <pillageDuVassal>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setVassal(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    command.split(" ")[3],
                    command.split(" ")[4])
            else:
                msg="ERR: vous ne pouvez pas changer le vassal de votre colo!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!clearVassal [joueurVassalisé] <coloVassalisée>`: retire le vassal d'une colonie d'un joueur.
async def clearVassal(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !clearVassal [joueurVassalisé] <coloVassalisée>"
    if await lengthVerificator(command, "!clearVassal [joueurVassalisé] <coloVassalisée>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.clearVassal(
                command.split(" ")[1],
                command.split(" ")[2])
        else:
            await error(channel, command, "Permissions insuffisantes")
    if await lengthVerificator(command, "!clearVassal <coloVassalisée>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.clearVassal(
                    player,
                    command.split(" ")[1])
            else:
                msg="ERR: vous ne pouvez pas changer le vassal de votre colo!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)



# `!setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur.
async def setStatsPlayer(channel, command, user, player):
    msg = "ERR: Commande mal formulée - !setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>"
    if await lengthVerificator(command, "!setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setStatsPlayer(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4],
                command.split(" ")[5])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setStatsPlayer <mandibule> <carapace> <phéromone> <thermique>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setStatsPlayer(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    command.split(" ")[3],
                    command.split(" ")[4])
            else:
                msg="ERR: vous ne pouvez pas changer vos statistiques!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


# `!setHero [joueur] <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`: modifie le héros d'un joueur.
async def setHero(channel,command, user, player):
    msg = "ERR: Commande mal formulée - !setHero [joueur] <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>"
    if await lengthVerificator(command,"!setHero [joueur] <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setHero(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setHero <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setHero(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2])
            else:
                msg = "ERR: vous ne pouvez pas changer votre héros!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)



#`!setActivePlayers <joueur1> ... <joueurN>`: définit les joueurs actifs de la LF;
async def setActivePlayers(channel,command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_CONSEIL, rw="W", self_command=False):
        newData = []
        if len(command.split(" ")) == 0:
            pass
        else:
            for p in command.split(" ")[1:]:
                newData.append(p.lower())
        f.saveData(newData, S_ACTIVE_PLAYERS)
        await getActivePlayers(channel, user)
    else:
        await error(channel, command, "Permissions insuffisantes")


# `!getTDCExploités`: donne les tdc exploités des joueurs actifs de la LF;
async def getTDCExploites(channel, command, user):
    msg = "ERR: trop d'arguments pour la commande: `!getTDCExploités`"
    if await lengthVerificator(command, "!getTDCExploités"):
        if isAuthorized(user=user, level_needed=PERMISSION_PRIVILEGED, rw="R", self_command=False):
            msg = joueurs.getTDCExploités()
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

#`!getActivePlayers`: donne les joueurs actifs de la LF;
async def getActivePlayers(channel, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
        activeP = f.loadData(S_ACTIVE_PLAYERS)
        msg = "Les joueurs actifs de la LF sont:\n"
        for p in activeP:
            msg+="   "+p+"\n"
        for m in f.splitMessage(msg):
            await channel.send(m)
    else:
        await error(channel, "`!getActivePlayers`", "Permissions insuffisantes")

# `!optiMandi [joueur]`: dit s'il faut augmenter les mandibules ou pondre des JTk pour un joueur;
async def optiMandi(channel,command, user, player):
    msg = "ERR: Commande mal formulée - !optiMandi [joueur]"
    if await lengthVerificator( command, "!optiMandi [joueur]"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            j_obj= joueurs.Joueur(command.split(" ")[1])
            msg = j_obj.optiMandi()
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator( command, "!optiMandi"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            if not player is None:
                j_obj = joueurs.Joueur(player)
                msg = j_obj.optiMandi()
            else:
                msg="ERR: vous ne pouvez pas calculer la rentabilité de vos mandibules!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# `!optiCara [joueur]`: dit s'il faut augmenter la carapace ou pondre des JS pour un joueur;
async def optiCara(channel,command, user, player):
    msg = "ERR: Commande mal formulée - !optiCara [joueur]"
    if await lengthVerificator( command, "!optiCara [joueur]"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
            j_obj= joueurs.Joueur(command.split(" ")[1])
            msg = j_obj.optiCara()
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator( command, "!optiCara"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
            if not player is None:
                j_obj = joueurs.Joueur(player)
                msg = j_obj.optiCara()
            else:
                msg="ERR: vous ne pouvez pas calculer la rentabilité de votre carapace!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        #await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# # `!setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>`: modifie les statistiques générales d'un joueur.
# async def setStatsPlayer(channel, command, user, player):
#     msg = "ERR: Commande mal formulée - !setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>"
#     if await lengthVerificator(command,
#                                "!setStatsPlayer [joueur] <mandibule> <carapace> <phéromone> <thermique>"):
#         if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=player.upper() in command.upper()):
#             msg = joueurs.setStatsPlayer(
#                 command.split(" ")[1],
#                 command.split(" ")[2],
#                 command.split(" ")[3],
#                 command.split(" ")[4],
#                 command.split(" ")[5])
#         else:
#             await error(channel, command, "Permissions insuffisantes")
#
#     if await lengthVerificator(command, "!setStatsPlayer <mandibule> <carapace> <phéromone> <thermique>"):
#         if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="R", self_command=True):
#             if not player is None:
#                 msg = joueurs.setStatsPlayer(
#                     player,
#                     command.split(" ")[1],
#                     command.split(" ")[2],
#                     command.split(" ")[3],
#                     command.split(" ")[4])
#             else:
#                 msg = "ERR: vous ne pouvez pas changer vos statistiques!"
#         else:
#             await error(channel, command, "Permissions insuffisantes")
#     if msg.startswith("ERR:"):
#         await error(channel, command, msg)
#     else:
#         # await message.delete()
#         for m in f.splitMessage(msg):
#             await channel.send(m)

# `!setCoord [joueur] <C1/C2> <x> <y>`
# modifie les coordonnées d'une des colonies d'un joueur
async def setCoord(channel, command, user, player):
    msg = "ERR: Commande mal formulée - `!setCoord [joueur] <C1/C2> <x> <y>`"
    if await lengthVerificator(command,
                               "!setCoord [joueur] <C1/C2> <x> <y>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setCoord(
                command.split(" ")[1],
                command.split(" ")[2],
                command.split(" ")[3],
                command.split(" ")[4])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!!setCoord <C1/C2> <x> <y>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setCoord(
                    player,
                    command.split(" ")[1],
                    command.split(" ")[2],
                    command.split(" ")[3])
            else:
                msg = "ERR: vous ne pouvez pas changer vos coordonnées!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        # await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)

# `!setVA [joueur] <va>`
# modifie la vitesse d'attaque d'un joueur
async def setVA(channel, command, user, player):
    msg = "ERR: Commande mal formulée - `!setVA [joueur] <va>`"
    if await lengthVerificator(command,"!setVA [joueur] <va>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=player.upper() in command.upper()):
            msg = joueurs.setVA(
                command.split(" ")[1],
                command.split(" ")[2])
        else:
            await error(channel, command, "Permissions insuffisantes")

    if await lengthVerificator(command, "!setVA <va>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ONLY_SELF_CMD, rw="W", self_command=True):
            if not player is None:
                msg = joueurs.setVA(
                    player,
                    command.split(" ")[1])
            else:
                msg = "ERR: vous ne pouvez pas changer votre VA!"
        else:
            await error(channel, command, "Permissions insuffisantes")
    if msg.startswith("ERR:"):
        await error(channel, command, msg)
    else:
        # await message.delete()
        for m in f.splitMessage(msg):
            await channel.send(m)


#__________________________________________________#
## PACTES ##
#__________________________________________________#


# `!printPactes`: affiche les pactes;
async def printPactes(channel, command, user):
  if await lengthVerificatorWerror(command, channel, "!printPactes"):
        if isAuthorized(user=user, level_needed=PERMISSION_MEMBER, rw="R", self_command=False):
            msg = pactes.printPactes()
            if msg.startswith("ERR:"):
              await error(channel, command, msg)
            else:
              #await message.delete()
              for m in f.splitMessage(msg):
                await channel.send(m)
        else:
            await error(channel, command, "Permissions insuffisantes")


# `!endPacte <ally>`: clôt un pacte;
async def endPacte(channel,command, user):
    if await lengthVerificatorWerror(command, channel, "!endPacte <ally>"):
        if isAuthorized(user=user, level_needed=PERMISSION_CONSEIL, rw="W", self_command=False):
            msg = pactes.endPacte(command.split(" ")[1])
            if msg.startswith("ERR:"):
              await error(channel, command, msg)
            else:
              #await message.delete()
              for m in f.splitMessage(msg):
                await channel.send(m)
    else:
        await error(channel, command, "Permissions insuffisantes")



# `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`: ajoute un nouveau pacte
async def pacte(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_CONSEIL, rw="W", self_command=False in command.upper()):
          if len(command.split("\n")) > 2:
            msg = pactes.addPacte(command)
            if msg.startswith("ERR:"):
              await error(channel, command, msg)
            else:
              #await message.delete()
              for m in f.splitMessage(msg):
                await channel.send(m)
          else:
            await error(channel, command, "Erreur dans la commande: `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`")
    else:
        await error(channel, command, "Permissions insuffisantes")


#__________________________________________________#
## DEV ##
#__________________________________________________#

# `!getDbNames`: donne les noms des bases de données;
async def getDbNames(channel, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
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
          #await message.delete()
          await channel.send(msg)
    else:
        await error(channel, "`!getDbNames`", "Permissions insuffisantes")


# `!getDB <path//filename>`: donne la base de données;
async def getDB(channel, command, user):
    # Rewrite
    filename = command.split(" ")[1]
    dirname = os.path.dirname(__file__)
    if await lengthVerificatorWerror(command, channel, "!getDB <path//filename>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
            if os.path.exists(dirname+"/JSON/"+filename):
                if len(filename.split("//")) == 1 or len(filename.split("/")) == 1:
                    file = discord.File(dirname+"/JSON/"+filename)  # an image in the same folder as the main bot file
                    embed = discord.Embed()  # any kwargs you want here
                    embed.set_image(url="attachment://" + filename.split("//")[-1])
                    # filename and extension have to match (ex. "thisname.jpg" has to be "attachment://thisname.jpg")
                    #await message.delete()
                    await channel.send(embed=embed, file=file)
                else:
                    msg = "```!getDB <path//filename>```"
                    msg += "\nNo authorised access to: `" + filename + "`"
                    await channel.send(msg)
            else:
                msg = "```!getDB <path//filename>```"
                msg += "\nNo file with this path: `" + filename + "`"
                await channel.send(msg)
        else:
            await error(channel, command, "Permissions insuffisantes")

# !printDB <DB>
# affiche les données d'une base de données
async def printDB(channel, command, user):
    #await message.delete()
    if lengthVerificatorWerror(command, channel, "!printDB <DB>"):
        if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
            await dbg.printDB(channel, command.split(" ")[1])
        else:
            await error(channel, command, "Permissions insuffisantes")

# `!getLog [date:aaaa-mm-jj]`: donne les logs [par défaut, du jour en cours];
async def getLog(channel, command, user):
    if isAuthorized(user=user, level_needed=PERMISSION_ADMIN, rw="R", self_command=False):
        # Rewrite
        filename = os.path.dirname(__file__)+"/LOGS/"+date.today().strftime("%Y-%m-%d")
        if len(command.split(" ")) > 1:
            filename = os.path.dirname(__file__) + "/LOGS/" + datetime.strptime(command.split(" ")[1],"%Y-%m-%d")
        if os.path.exists(filename):
            file = discord.File(filename)
            embed = discord.Embed()
            embed.set_image(url="attachment://log.txt")
            #await message.delete()
            await channel.send(embed=embed, file=file)
        else:
            msg = "```!getLog [date:aaaa-mm-jj]```"
            msg += "\nNo file with this path: `" + filename + "`"
            await channel.send(msg)
    else:
            await error(channel, command, "Permissions insuffisantes")


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
  player = getPlayerFromRoles(user)


  if message.content.upper().startswith("!"):
    command= f.parseCMD(message.content)
    channel= message.channel


    lf_members = f.loadData(S_ACTIVE_PLAYERS)
    for m in lf_members:
        if m in rolesIDs:
            if user.get_role(rolesIDs[m]) is not None and m in command.lower():
                is_concerned = True

    allies= f.loadData(S_ALLIES_PLAYERS)
    for m in allies:
        if m in rolesIDs:
            if user.get_role(rolesIDs[m]) is not None and m in command.lower():
                is_concerned = True



    
    ### ----- ###
    ### Aides ###
    ### ----- ###

    
    #`!help`
    # affiche les commandes;
    if command.upper().startswith("!HELP AIDE"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 0)
    elif command.upper().startswith("!HELP ALLIANCE"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 1)
    elif command.upper().startswith("!HELP CHASSE"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 2)
    elif command.upper().startswith("!HELP CONVOI"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 3)
    elif command.upper().startswith("!HELP FLOOD"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 4)
    elif command.upper().startswith("!HELP JOUEUR"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 5)
    elif command.upper().startswith("!HELP PACTE"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 6)
    elif command.upper().startswith("!HELP DEV"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(channel, 7)
    elif command.upper().startswith("!HELP"): 
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await help(message.author)
      await reactMSG(message, False)

      #`!templatePlayer`
      # donne la fiche à remplir pour enregistrer un joueur;
    elif command.upper().startswith("!TEMPLATEPLAYER"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await templatePlayer(message.author, user)
        #await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access"])

    # `!templatePacte`
    # donne la commande à remplir pour enregistrer un pacte;
    elif command.upper().startswith("!TEMPLATEPACTE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, diplo]):
        await templatePacte(message.author, user)
      #   await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access", "diplo"])

    # `!getDbNames`: donne les noms des bases de données;
    elif command.upper().startswith("!GETDBNAMES"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await getDbNames(message.author, user)
      #   await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access"])

    # `!getDB <path//filename>`: donne la base de données;
    elif command.upper().startswith("!GETDB"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await getDB(message.author,command, user)
      #   await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access"])

    elif command.upper().startswith("!GETLOG"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await getLog(message.author,command, user)
      #   await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access"])
    
    ### -------- ###
    ### Alliance ###
    ### -------- ###

    
    # `!printAlliance`
    # affiche les données de l'alliance;
    elif command.upper().startswith("!PRINTALLIANCE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, superReader, membre]):
        await printAlliance(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot super-reader acces", "membre"])

    # `!setTDC <tdc>`
    # modifie la quantité de TDC de l'alliance;
    elif command.upper().startswith("!SETTDCALLY"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await setTDCAlly(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    # `!setNbMember <quantité>`
    # modifie le nombre de joueurs de l'alliance;
    elif command.upper().startswith("!SETNBMEMBRE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await setNBMembre(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    # `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie le bonus d'alliance;
    elif command.upper().startswith("!SETBONUSALLY"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await setBonusAlly(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    # `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`
    # modifie les stats de l'alliance;
    elif command.upper().startswith("!SETALLY"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await setAlly(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    
    ### ------- ###
    ### Chasses ###
    ### ------- ###

    
    # `!printChasses <joueur>`
    # affiche les chasses d'un joueur
    elif command.upper().startswith("!PRINTCHASSES"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await printChasses(channel, command, user, player)
        #await setAlly(channel,command)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    # `!chasse [joueur] <quantité>`
    # enregistre une chasse;
    elif command.upper().startswith("!CHASSE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await chasse(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

    # `!simuChasse [joueur] <tdc_initial> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`:
    # donne la simulation de chasse pour le joueur
    elif command.upper().startswith("!SIMUCHASSE "):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, superReader, is_concerned]):
        await simuChasse(message.author,command, user, player)
        await reactMSG(message, False)
      # else:
      #   await errorRole(channel,["bot admin access", "bot super-reader access", "joueur concerné"])

      # `!simuChassePex [joueur] <tdc_initial> <tdc_chasse:entre_1_et_1000_cm> <vitesse_de_traque> <colonie_de_chasse> <nombre_de_chasses>`:
      # donne la simulation de chasse pour le joueur
    elif command.upper().startswith("!SIMUCHASSEPEX "):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, superReader, is_concerned]):
        await simuChassePex(message.author, command, user, player)
      #     await reactMSG(message, False)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader access", "joueur concerné"])

      ### ------- ###
      ### Convois ###
      ### ------- ###

  
    # `!convoisEnCours`
    # affiche les convois en cours;
    elif command.upper().startswith("!CONVOISENCOURS"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, superReader, membre]):
        await printConvoisEnCours(channel,command,user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`
      # ajoute un convoi;
    elif command.upper().startswith("!CONVOI"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await convoi(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!autoProd [joueur] <pomme> <bois> <eau>`
      # met à jour un convoi avec l'autoprod d'un joueur;
    elif command.upper().startswith("!AUTOPROD"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await autoProd(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!demandeConvoi <joueur> <C1/C2> <pomme> <bois> <eau>`
      # ajoute un convoi à la liste des convois en cours;
    elif command.upper().startswith("!DEMANDECONVOI"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, membre]):
        await demandeConvoi(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "membre"])

        # `!recapRessources [yyyy-mm-dd]`
        # calcul le récapitulatif des ressources récoltées de la journée;
    elif command.upper().startswith("!RECAPRESSOURCES"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await recapRSS(channel,command)
      # else:
      #   await errorRole(channel,["bot admin access"])


        # `!printRecapRessources`
        # affiche le récapitulatif des ressources récoltées de la journée;
    elif command.upper().startswith("!PRINTRECAPRESSOURCES"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await printRecapRSS(channel,command)
      # else:
      #   await errorRole(channel,["bot admin access"])

        # `!printConvoisJour [date:aaaa-mm-jj]`
        # affiche les convois effectués sur cette date
    elif command.upper().startswith("!PRINTCONVOISJOUR"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, superReader]):
        await printConvoisJour(channel,command)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader access"])

      ### --------------- ###
      ### Floods externes ###
      ### --------------- ###

    
      # `!floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`
      # enregistre un flood externe reçu;
    elif command.upper().startswith("!FLOODEXTR"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await floodExtR(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!floodExtD [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>`
      # enregistre un flood externe donné;
    elif command.upper().startswith("!FLOODEXTD"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await floodExtD(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!futursfloods`
      # affiche les floods à faire;
    elif command.upper().startswith("!FUTURSFLOODS"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, superReader, membre]):
        await printFloodsFuturs(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "bot super-reader access", "membre"])

      # `!printFloodsExt`
      # affiche les floods externes;
    elif command.upper().startswith("!PRINTFLOODSEXT"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, superReader]):
        await printFloodsExt(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`
      # enregistre un don de tdc (butin de guerre par exemple)
    elif command.upper().startswith("!DONTDC"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer]):
        await donTDC(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access"])

    elif command.upper().startswith("!TPSFLOODLF"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, writer]):
        await tpsFloodLF(channel, command, user, player)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader"])


    elif command.upper().startswith("!TPSFLOODEXT"):
      f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      await tpsFloodExt(channel, command, user)

    elif command.upper().startswith("!LISTEFLOODEXTR"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, writer]):
        await listeFloodExtR(channel, command, user)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader"])

    elif command.upper().startswith("!LISTEFLOODEXTD"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, writer]):
        await listeFloodExtD(channel, command, user)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader"])

    elif command.upper().startswith("!LISTEDATEFLOODLF"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, writer]):
        await listeDateFloodLF(channel, command, user)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot super-reader"])

    
      ### ------- ###
      ### Joueurs ###
      ### ------- ###

    
      # `!printPlayer <joueur>`
      # affiche les données d'un joueur.
    elif command.upper().startswith("!PRINTPLAYER"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await printPlayer(message.author,command, user, player)
      #   await reactMSG(message,False)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])
      #   await reactMSG(message,True)

      # `!player \\n <templatePlayer>` // `!player <nom>`
      # ajoute un nouveau joueur
    elif command.upper().startswith("!PLAYER"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await addPlayer(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access"])

        # `!allié \\n <templatePlayer>`
        # ajoute un nouvel allié;
    elif command.upper().startswith("!ALLIÉ"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles([admin]):
        await addAllie(channel, command, user)
        # else:
        #     await errorRole(channel, ["bot admin access"])

        # `!renameColo [joueur] <C1/C2> \\n <nom avec espaces>`
        # modifie le nom de la colo d'un joueur d'un joueur.
    elif command.upper().startswith("!RENAMECOLO"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles( [admin, writer, is_concerned]):
        await renameColo(channel,command, user, player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot writer access", "joueur concerné"])

      # `!setArmy <joueur> <C1/C2> \\n <copie_du_simulateur_de_chasse_de_NaW>`
      # modifie l'armée d'un joueur.
    elif command.upper().startswith("!SETARMY"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        await message.delete()
      # if checkRoles( [admin, writer, is_concerned]):
        await setArmy(message.author,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setRace <joueur> <0:Abeille,1:Araignée,2:Fourmi,3:Termite>`
      # modifie la race d'un joueur.
    elif command.upper().startswith("!SETRACE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await setRace(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

        # `!setTDCExploité <joueur> <C1/C2> <tdcExploté>`:
        # modifie le tdc exploité d'un joueur;
    elif command.upper().startswith("!SETTDCEXPLOITÉ"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles( [admin, writer, is_concerned]):
        await setTDCExploit(channel,command, user,player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot writer access", "joueur concerné"])

        # `!setTDC <joueur> <C1/C2> <tdcExploté>`:
        # modifie le tdc d'un joueur;
    elif command.upper().startswith("!SETTDC "):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles( [admin, writer, is_concerned]):
        await setTDC(channel,command, user, player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsColo <joueur> <colo> <oe> <ov> <tdp>`
      # modifie les stats d'une colonie d'un joueur.
    elif command.upper().startswith("!SETSTATSCOLO"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await setStatsColo(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setVassal <joueurVassalisé> <coloVassalisée> <vassal> <coloVassal> <pillage>`
      # modifie le vassal d'une colonie d'un joueur.
    elif command.upper().startswith("!SETVASSAL"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await setVassal(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!clearVassal [joueurVassalisé] <coloVassalisée>`
      # retire le vassal d'une colonie d'un joueur.
    elif command.upper().startswith("!CLEARVASSAL"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles([admin, writer, is_concerned]):
        await clearVassal(channel, command, user, player)
      # else:
      #     await errorRole(channel, ["bot admin access", "bot writer access", "joueur concerné"])

      # `!setStatsPlayer <joueur> <mandibule> <carapace> <phéromone> <thermique>`
      # modifie les statistiques générales d'un joueur.
    elif command.upper().startswith("!SETSTATSPLAYER"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await setStatsPlayer(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

      # `!setHero <joueur> <0:Vie|1:FdF-Combat|2:FdF-Chasse> <niveauDuBonus>`
      # modifie le héros d'un joueur.
    elif command.upper().startswith("!SETHERO"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, is_concerned]):
        await setHero(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "joueur concerné"])

    #`!setActivePlayers <joueur1> ... <joueurN>`
    # définit les joueurs actifs de la LF;
    elif command.upper().startswith("!SETACTIVEPLAYERS"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await setActivePlayers(channel, user,command)
      # else:
      #   await errorRole(channel,["bot admin access"])

    #`!getTDCExploités`
    # donne les tdc exploités des joueurs actifs de la LF;
    elif command.upper().startswith("!GETTDCEXPLOITÉS"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, superReader]):
        await getTDCExploites(channel, command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot super-reader access"])

    #`!getActivePlayers`
    # donne les joueurs actifs de la LF;
    elif command.upper().startswith("!GETACTIVEPLAYERS"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin]):
        await getActivePlayers(channel, user)
      # else:
      #   await errorRole(channel,["bot admin access"])

    #`!optiMandi [joueur]`
    # dit s'il faut augmenter les mandibules ou pondre des JTk pour un joueur;
    elif command.upper().startswith("!OPTIMANDI"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, superReader, is_concerned]):
        await optiMandi(channel,command, user, player)
      # else:
      #   await errorRole(channel,["bot admin access", "bot super-reader access", "joueur concerné"])

    # `!optiCara [joueur]`
    # dit s'il faut augmenter la carapace ou pondre des JS pour un joueur;
    elif command.upper().startswith("!OPTICARA"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles( [admin, superReader, is_concerned]):
        await optiCara(channel,command, user, player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot super-reader access", "joueur concerné"])

    elif command.upper().startswith("!SETVA"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles([admin, superReader, is_concerned]):
        await setVA(channel, command, user, player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot super-reader access", "joueur concerné"])

    elif command.upper().startswith("!SETCOORD"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
        # if checkRoles([admin, superReader, is_concerned]):
        await setCoord(channel, command, user, player)
        # else:
        #     await errorRole(channel, ["bot admin access", "bot super-reader access", "joueur concerné"])


    
      ### ------ ###
      ### Pactes ###
      ### ------ ###

    
      # `!printPactes`
      # affiche les pactes;
    elif command.upper().startswith("!PRINTPACTES"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, writer, superReader]):
        await printPactes(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "bot writer access", "bot super-reader access"])

      # `!endPacte <ally>`
      # clôt un pacte;
    elif command.upper().startswith("!ENDPACTE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, diplo]):
        await endPacte(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "diplo"])

      # `!pacte <ally> <type-guerre> <type-commerce> <start> <end> \\n <titre> \\n <description>`
      # ajoute un nouveau pacte
    elif command.upper().startswith("!PACTE"):
        f.log(rank=0, prefixe="[CMD]", message=command, suffixe="")
      # if checkRoles( [admin, diplo]):
        await pacte(channel,command, user)
      # else:
      #   await errorRole(channel,["bot admin access", "diplo"])

    
      ### ------ ###
      ### ERRORS ###
      ### ------ ###

    
    elif command.startswith("!"):
        f.log(rank=0, prefixe="[ERROR]", message="Unknown error - " + command, suffixe="")
        await error(channel,command,"Commande inconnue. `!help` pour voir la liste des commandes disponibles.")  #error



#__________________________________________________#
## Run ##
#__________________________________________________#

#On va maintenir le bot en activité
keep_alive()
#On lance le bot
f.log(rank=0, prefixe="[START]", message="Bot launching", suffixe="")
bot.run(token)
