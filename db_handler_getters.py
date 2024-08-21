import os
import json
import functions as f
from datetime import datetime, timedelta


#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

H_FLOODS_FILENAME = "HIST//Historique_FloodsExternes.json"
H_PACTE_FILENAME = "HIST//Historique_Pactes.json"
H_CONVOIS_EXTERNES_FILENAME = "HIST//Historique_ConvoisExternes.json"

S_CONVOIS_FILENAME = "STATS//Stats_ConvoisEnCours.json"
S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"
S_FLOODS_FILENAME = "STATS//Stats_FloodsFuturs.json"

RACES = ["Abeille", "Araignée", "Fourmi", "Termite"]
BONUS_HEROS = ["Vie", "FdF - Combat", "FdF - Chasse"]

COLONIES = f.loadData("CONST//CONST_Colonies.json")
PACTES = f.loadData("CONST//CONST_Pactes.json")
JOUEUR_DANs_ALLIANCE = f.loadData("CONST//CONST_Association-Player-Ally.json")



#__________________________________________________#
## AFFICHAGE DISCORD ##
#__________________________________________________#

async def printDB(channel, filename):
  data = f.loadData(filename)
  await channel.send("```"+str(data)+"```")

