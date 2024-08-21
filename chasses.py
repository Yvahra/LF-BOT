##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import datetime
from db_handler_functions import COLONIES, S_JOUEUR_FILENAME
import functions as f

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

H_CHASSE_FILENAME = "HIST//Historique_Chasses.json"
S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"

COLONIES = f.setCOLONIES()

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def printChasses(joueur:str) -> str:
  global COLONIES
  data = f.loadData(H_CHASSE_FILENAME)
  msg = "**Chasses de "+joueur+"**:\n```"
  for c in data:
    if c["player"]["name"].upper() == joueur.upper():
      msg+= "["+ c["day"] +"] +"+ f.convertNumber(str(c["quantity"])) + "cm² "
      msg+= "avec " + COLONIES[c["player"]["name"].upper()][c["player"]["colony"]] + "\n"
  msg+= "```"
  return msg


# 3 - `!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;
def chasse(joueur:str, colony:str, quantity:str):
  msg = ""
  try:
    data = f.loadData(H_CHASSE_FILENAME)
    colo = 0 if colony == "C1" else 1
    data.append({
                 "player": {
                   "name": joueur,
                   "colony": colo
                 },
                 "quantity": int(quantity),
                 "day": datetime.date.today().strftime("%Y-%m-%d")
               })
    f.saveData(data, H_CHASSE_FILENAME)
    msg = "Chasse enregistrée avec succès"
  except Exception as e:
    msg = "ERR: " + str(e)
  return msg
  